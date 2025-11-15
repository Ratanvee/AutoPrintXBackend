from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.utils.timezone import localtime, now
from datetime import timedelta, datetime, time
from django.core.paginator import Paginator
from django.core.cache import cache
import json
import environ

from smartdocx.models import UploadFiles, CustomUser
from smartdocx.serializer import UploadFilesSerializer
from .utils import (
    serialize_mongo_data, 
    convert_decimal128, 
    get_dashboard_stats,
    get_last_modified_timestamp
)
from customerside.utils import ImageKitClient

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_cache_key(user_id, endpoint):
    """Generate consistent cache keys"""
    return f"owner_{user_id}_{endpoint}"


def get_time_ago(timestamp):
    """Calculate human-readable time difference"""
    now_time = now()
    diff = now_time - timestamp

    if diff.days > 0:
        return "1 day ago" if diff.days == 1 else f"{diff.days} days ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        return "1 hour ago" if hours == 1 else f"{hours} hours ago"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return "1 min ago" if minutes == 1 else f"{minutes} min ago"
    
    return "Just now"


def format_order(order):
    """Format order object to consistent dictionary"""
    return {
        "id": order.OrderId or f"Order-{order.id}",
        "customer": order.CustomerName or "Unknown Customer",
        "date": localtime(order.Created_at).strftime("%b %d, %Y"),
        "amount": f"₹{convert_decimal128(order.PaymentAmount):.2f}",
        "status": order.PrintStatus or "Pending",
        "file_url": order.FileUpload,
        "file_path": order.FileUpload,
        "paper_size": order.PaperSize,
        "paper_type": order.PaperType,
        "print_color": order.PrintColor,
        "print_side": order.PrintSide,
        "binding": order.Binding,
        "no_of_copies": order.NumberOfCopies,
        "no_of_pages": order.NoOfPages,
        "transaction_id": order.Transaction_id,
        "payment_status": order.PaymentStatus,
        "payment_method": order.PaymentMethod,
    }


# ============================================
# DASHBOARD VIEWS
# ============================================

class OrdersOverview(APIView):
    """Get dashboard statistics overview"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = get_cache_key(user.id, 'orders_overview')
        
        # Try to get from cache (cache for 30 seconds)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        try:
            dashboard_stats = get_dashboard_stats(user.unique_url)
            dashboard_stats = serialize_mongo_data(dashboard_stats)
            
            response_data = {
                "OrderOverview": [{
                    "unique_url": user.unique_url,
                    "dashboard_stats": dashboard_stats
                }]
            }
            
            # Cache for 30 seconds
            cache.set(cache_key, response_data, 30)
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch dashboard overview: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardView(APIView):
    """Get user dashboard data"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        user_data = {
            "username": user.username,
            "email": user.email,
            "unique_url": user.unique_url,
            'is_modified': user.info_modified,
            'owner_name': user.owner_fullname,
        }
        
        return Response({
            "message": "Welcome to your dashboard",
            "user": user_data
        })


# ============================================
# CACHEABLE RECENT ORDERS VIEW
# ============================================

class RecentOrdersView(APIView):
    """
    Return recent orders with smart caching and ETag support
    Cache is automatically invalidated when data changes
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if not user or user.is_anonymous:
            return Response(
                {"error": "User not authenticated"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate cache key
        cache_key = get_cache_key(user.id, 'recent_orders')
        
        # Get last modified timestamp for ETag
        last_modified = get_last_modified_timestamp(user)
        
        # Check if client has the same version (ETag validation)
        client_etag = request.META.get('HTTP_IF_NONE_MATCH')
        if client_etag and client_etag == last_modified:
            # Data hasn't changed, return 304 Not Modified
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data and cached_data.get('last_modified') == last_modified:
            # Cache hit and data is fresh
            response = Response(
                {"orders": cached_data['orders']}, 
                status=status.HTTP_200_OK
            )
            # Add ETag header for client-side caching
            response['ETag'] = last_modified
            response['Cache-Control'] = 'private, max-age=10'
            return response

        # Cache miss or stale data - fetch from database
        try:
            all_orders = UploadFiles.objects.filter(
                Owner=user
            ).order_by('-Created_at')
            
            # Format orders
            formatted_orders = [format_order(order) for order in all_orders]

            # Prepare cache data
            cache_data = {
                'orders': formatted_orders,
                'last_modified': last_modified,
                'cached_at': timezone.now().isoformat()
            }
            
            # Cache for 30 seconds (will be invalidated on data change)
            cache.set(cache_key, cache_data, 30)
            
            response = Response(
                {"orders": formatted_orders}, 
                status=status.HTTP_200_OK
            )
            
            # Add cache headers
            response['ETag'] = last_modified
            response['Cache-Control'] = 'private, max-age=10'
            response['X-Cache'] = 'MISS'
            
            return response

        except Exception as e:
            print(f"Error fetching orders: {str(e)}")
            return Response(
                {"error": f"Failed to fetch orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# CHART DATA
# ============================================

class OrdersChartData(APIView):
    """Returns chart data based on filter: day, week, month, overall"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_type = request.GET.get("filter", "day")
        user = request.user
        
        # Try cache first (cache for 60 seconds)
        cache_key = get_cache_key(user.id, f'chart_{filter_type}')
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        try:
            chart_data = self._generate_chart_data(user, filter_type)
            
            # Cache for 60 seconds
            cache.set(cache_key, chart_data, 60)
            
            return Response(chart_data)
            
        except Exception as e:
            print(f"Error generating chart data: {str(e)}")
            return Response(
                {"error": f"Failed to generate chart data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_chart_data(self, user, filter_type):
        """Generate chart data based on filter type"""
        now_time = timezone.now()
        labels = []
        revenue_data = []
        orders_data = []
        
        qs = UploadFiles.objects.filter(Unique_url=user.unique_url)
        
        if filter_type == "day":
            labels, revenue_data, orders_data = self._get_daily_data(qs, now_time)
        elif filter_type == "week":
            labels, revenue_data, orders_data = self._get_weekly_data(qs, now_time)
        elif filter_type == "month":
            labels, revenue_data, orders_data = self._get_monthly_data(qs, now_time)
        elif filter_type == "overall":
            labels, revenue_data, orders_data = self._get_overall_data(qs)
        
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Revenue",
                    "data": revenue_data,
                    "borderColor": "#0a2463",
                    "backgroundColor": "rgba(10, 36, 99, 0.1)",
                    "tension": 0.4,
                },
                {
                    "label": "Orders",
                    "data": orders_data,
                    "borderColor": "#2176ff",
                    "backgroundColor": "rgba(33, 118, 255, 0.1)",
                    "tension": 0.4,
                },
            ],
        }
    
    def _get_daily_data(self, qs, now_time):
        """Get data for last 7 days"""
        labels = []
        revenue_data = []
        orders_data = []
        
        for i in range(6, -1, -1):
            day = now_time - timedelta(days=i)
            labels.append(day.strftime("%d %b"))
            
            day_start = datetime.combine(day.date(), time.min)
            day_end = datetime.combine(day.date(), time.max)
            
            if timezone.is_aware(now_time):
                day_start = timezone.make_aware(day_start)
                day_end = timezone.make_aware(day_end)
            
            daily_qs = qs.filter(Created_at__gte=day_start, Created_at__lte=day_end)
            
            revenue = sum(
                convert_decimal128(obj.PaymentAmount) 
                for obj in daily_qs.only('PaymentAmount')
            )
            orders = daily_qs.count()
            
            revenue_data.append(round(revenue, 2))
            orders_data.append(orders)
        
        return labels, revenue_data, orders_data
    
    def _get_weekly_data(self, qs, now_time):
        """Get data for last 4 weeks"""
        labels = []
        revenue_data = []
        orders_data = []
        
        for i in range(3, -1, -1):
            start_week = now_time - timedelta(weeks=i, days=now_time.weekday())
            end_week = start_week + timedelta(days=6)
            labels.append(f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b')}")
            
            week_start = datetime.combine(start_week.date(), time.min)
            week_end = datetime.combine(end_week.date(), time.max)
            
            if timezone.is_aware(now_time):
                week_start = timezone.make_aware(week_start)
                week_end = timezone.make_aware(week_end)
            
            weekly_qs = qs.filter(Created_at__gte=week_start, Created_at__lte=week_end)
            
            revenue = sum(
                convert_decimal128(obj.PaymentAmount) 
                for obj in weekly_qs.only('PaymentAmount')
            )
            orders = weekly_qs.count()
            
            revenue_data.append(round(revenue, 2))
            orders_data.append(orders)
        
        return labels, revenue_data, orders_data
    
    def _get_monthly_data(self, qs, now_time):
        """Get data for current year (12 months)"""
        labels = []
        revenue_data = []
        orders_data = []
        year = now_time.year
        
        for month in range(1, 13):
            labels.append(datetime(year, month, 1).strftime("%b"))
            
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
            
            if timezone.is_aware(now_time):
                month_start = timezone.make_aware(month_start)
                month_end = timezone.make_aware(month_end)
            
            monthly_qs = qs.filter(Created_at__gte=month_start, Created_at__lte=month_end)
            
            revenue = sum(
                convert_decimal128(obj.PaymentAmount) 
                for obj in monthly_qs.only('PaymentAmount')
            )
            orders = monthly_qs.count()
            
            revenue_data.append(round(revenue, 2))
            orders_data.append(orders)
        
        return labels, revenue_data, orders_data
    
    def _get_overall_data(self, qs):
        """Get all-time data grouped by month"""
        labels = []
        revenue_data = []
        orders_data = []
        
        all_records = qs.order_by('Created_at')
        month_data = {}
        
        for record in all_records:
            if record.Created_at:
                month_key = record.Created_at.strftime("%Y-%m")
                month_label = record.Created_at.strftime("%b %Y")
                
                if month_key not in month_data:
                    month_data[month_key] = {
                        'label': month_label,
                        'revenue': 0.0,
                        'orders': 0
                    }
                
                month_data[month_key]['revenue'] += convert_decimal128(record.PaymentAmount)
                month_data[month_key]['orders'] += 1
        
        for month_key in sorted(month_data.keys()):
            data = month_data[month_key]
            labels.append(data['label'])
            revenue_data.append(round(data['revenue'], 2))
            orders_data.append(data['orders'])
        
        return labels, revenue_data, orders_data


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class UpdatePrintStatusAPIView(APIView):
    """Update PrintStatus of a specific order to 'Complete' after printing"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        order_id = request.data.get("order_id")
        
        print("\n" + "=" * 70)
        print("[ PRINT STATUS UPDATE REQUEST ]")
        print(f"  Order ID: {order_id}")
        print(f"  Timestamp: {timezone.now()}")
        print("=" * 70)
        
        if not order_id:
            print("[ERROR] Missing order_id in request")
            return Response(
                {"error": "order_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Clean the order_id
            order_id = str(order_id).strip()
            
            # Check if order exists
            if not UploadFiles.objects.filter(OrderId=order_id).exists():
                print(f"[ERROR] Order '{order_id}' not found in database")
                
                # Show similar orders for debugging
                similar_orders = UploadFiles.objects.filter(
                    OrderId__icontains=order_id[:5]
                ).values_list('OrderId', flat=True)[:3]
                
                if similar_orders:
                    print(f"  Similar orders found: {list(similar_orders)}")
                
                return Response(
                    {
                        "error": "Order not found",
                        "order_id": order_id
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get current status before update
            order = UploadFiles.objects.get(OrderId=order_id)
            old_status = order.PrintStatus
            
            print(f"[ INFO ] Found order: {order_id}")
            print(f"  Current PrintStatus: {old_status}")
            
            # Update PrintStatus to Complete
            updated_count = UploadFiles.objects.filter(OrderId=order_id).update(
                PrintStatus="Complete"
            )
            
            if updated_count > 0:
                print(f"[ SUCCESS ] ✓ Updated PrintStatus")
                print(f"  Order: {order_id}")
                print(f"  Status: {old_status} → Complete")
                print(f"  Records updated: {updated_count}")
                print("=" * 70 + "\n")
                
                return Response(
                    {
                        "success": True,
                        "message": f"Order {order_id} PrintStatus updated to Complete",
                        "order_id": order_id,
                        "old_status": old_status,
                        "new_status": "Complete",
                        "updated": True
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                print(f"[WARN] No records updated for order {order_id}")
                return Response(
                    {
                        "error": "Update failed - no records modified",
                        "order_id": order_id
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except UploadFiles.DoesNotExist:
            print(f"[ERROR] Order not found: {order_id}")
            return Response(
                {
                    "error": "Order not found",
                    "order_id": order_id
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Exception as e:
            print(f"[FATAL] Unexpected error updating PrintStatus")
            print(f"  Error: {str(e)}")
            print(f"  Type: {type(e).__name__}")
            
            import traceback
            traceback.print_exc()
            
            return Response(
                {
                    "error": str(e),
                    "type": type(e).__name__,
                    "order_id": order_id
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_owner_orders(request):
    """
    Get orders with pagination, search, status filter, and date range
    """
    owner = request.user
    
    # Get query parameters with defaults
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 10)), 100)  # Max 100 per page
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    
    try:
        # Base queryset
        orders = UploadFiles.objects.filter(Owner=owner).order_by('-Created_at')
        
        # Apply search filter
        if search:
            orders = orders.filter(
                Q(CustomerName__icontains=search) |
                Q(OrderId__icontains=search)
            )
        
        # Apply date range filter
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                orders = orders.filter(Created_at__date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                orders = orders.filter(Created_at__date__lte=to_date)
            except ValueError:
                pass
        
        # Apply status filter
        if status_filter and status_filter.lower() != "all":
            orders = orders.filter(PrintStatus__iexact=status_filter)
        
        # Pagination
        paginator = Paginator(orders, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize
        serializer = UploadFilesSerializer(page_obj, many=True)
        
        return Response({
            "orders": serializer.data,
            "total_orders": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        })
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================
# RECENT ACTIVITY
# ============================================

class RecentActivityView(APIView):
    """Return recent activities for the logged-in user (owner)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if not user or user.is_anonymous:
            return Response(
                {"error": "User not authenticated"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        limit = min(int(request.GET.get('limit', 4)), 20)  # Max 20 activities
        
        # Try cache first (cache for 10 seconds)
        cache_key = get_cache_key(user.id, f'activity_{limit}')
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        try:
            activities = self._get_activities(user, limit)
            response_data = {"activities": activities}

            # Cache for 30 seconds
            cache.set(cache_key, response_data, 30)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error fetching recent activities: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_activities(self, user, limit):
        """Generate activities list"""
        activities = []
        activity_id = 1
        recent_time = now() - timedelta(hours=24)
        
        # 1. New Orders
        new_orders = UploadFiles.objects.filter(
            Owner=user,
            Created_at__gte=recent_time
        ).order_by('-Created_at')[:5]
        
        for order in new_orders:
            activities.append({
                "id": activity_id,
                "type": "order",
                "message": f"New order from {order.CustomerName or 'Unknown Customer'}",
                "time": get_time_ago(order.Created_at),
                "timestamp": order.Created_at.isoformat(),
                "order_id": order.OrderId,
            })
            activity_id += 1
        
        # 2. Payment Activities
        paid_orders = UploadFiles.objects.filter(
            Owner=user,
            PaymentStatus=True,
            Updated_at__gte=recent_time
        ).order_by('-Updated_at')[:5]
        
        for order in paid_orders:
            activities.append({
                "id": activity_id,
                "type": "payment",
                "message": f"Payment received for Order #{order.OrderId}",
                "time": get_time_ago(order.Updated_at),
                "timestamp": order.Updated_at.isoformat(),
                "order_id": order.OrderId,
                "amount": f"₹{convert_decimal128(order.PaymentAmount):.2f}",
            })
            activity_id += 1
        
        # 3. Completed Orders
        completed_orders = UploadFiles.objects.filter(
            Owner=user,
            PrintStatus="Complete",
            Updated_at__gte=recent_time
        ).order_by('-Updated_at')[:5]
        
        for order in completed_orders:
            activities.append({
                "id": activity_id,
                "type": "delivery",
                "message": f"Order #{order.OrderId} delivered",
                "time": get_time_ago(order.Updated_at),
                "timestamp": order.Updated_at.isoformat(),
                "order_id": order.OrderId,
            })
            activity_id += 1
        
        # 4. New Customers (only unique new customers)
        try:
            recent_customer_names = UploadFiles.objects.filter(
                Owner=user,
                Created_at__gte=recent_time
            ).values_list('CustomerName', flat=True).distinct()
            
            for customer_name in recent_customer_names:
                if not customer_name:
                    continue
                
                # Check if customer is truly new
                previous_orders = UploadFiles.objects.filter(
                    Owner=user,
                    CustomerName=customer_name,
                    Created_at__lt=recent_time
                ).exists()
                
                if not previous_orders:
                    first_order = UploadFiles.objects.filter(
                        Owner=user,
                        CustomerName=customer_name,
                        Created_at__gte=recent_time
                    ).order_by('Created_at').first()
                    
                    if first_order:
                        activities.append({
                            "id": activity_id,
                            "type": "customer",
                            "message": f"New customer registration: {customer_name}",
                            "time": get_time_ago(first_order.Created_at),
                            "timestamp": first_order.Created_at.isoformat(),
                            "customer_name": customer_name,
                        })
                        activity_id += 1
        except Exception as e:
            print(f"Error fetching customers: {str(e)}")
        
        # Sort by timestamp and return limited results
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]


# ============================================
# SETTINGS MANAGEMENT
# ============================================

def update_user_settings(user, section, data, uploaded_file_url=None):
    """Update user settings based on section"""
    try:
        if section == 'general':
            user.shop_name = data.get('shopName', user.shop_name)
            user.email = data.get('email', user.email)
            user.owner_phone_number = data.get('phone', user.owner_phone_number)
            user.owner_shop_address = data.get('address', user.owner_shop_address)
            # user.info_modified = True
            user.save()
            return True
        
        if section == 'profile':
            user.owner_fullname = data.get('firstName', user.owner_fullname)
            user.email = data.get('email', user.email)
            
            # Update avatar if uploaded
            if uploaded_file_url:
                user.owner_shop_image = uploaded_file_url
            
            user.info_modified = True
            user.save()
            return True
        
        if section == 'notifications':
            # Add notification settings logic here
            return True
        
        if section == 'billing':
            # Add billing settings logic here
            return True
        
        return False
        
    except Exception as e:
        print(f"Error updating settings: {str(e)}")
        raise


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])

def DashboardSettings(request):
    """Get or update dashboard settings"""
    user = request.user
    
    # GET: Return current settings
    # GET: Return current settings in the exact format needed by frontend
    if request.method == 'GET':
        # Prepare settings data
        settings_data = {
            "general": {
                "shopName": getattr(user, 'shop_name'),
                "email": user.email or '',
                "phone": getattr(user, 'owner_phone_number', ''),
                "address": getattr(user, 'owner_shop_address', ''),
                "currency": "INR",  # Default value
                "timezone": "Asia/Kolkata",  # Default value
            },
            "profile": {
                "fullName": getattr(user, 'owner_fullname'),
                "email": user.email or '',
                "role": "Shop Owner",  # Default role
                "avatar": getattr(user, 'owner_shop_image', ''),
            }
        }
        
        return Response({
            "success": True,
            "settings": settings_data,
            "user": {
                "username": user.username,
                "unique_url": getattr(user, 'unique_url', ''),
            }
        })
    
    # POST: Update settings
    if request.method == 'POST':
        section = request.data.get('section')
        raw_data = request.data.get('data')
        uploaded_file = request.FILES.get('avatar')
        
        # Validate required fields
        if not section or not raw_data:
            return Response(
                {"error": "Both 'section' and 'data' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse data if it's a string (from multipart/form-data)
        try:
            settings_data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON format in 'data' field."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle file upload for profile section
        uploaded_file_url = None
        if section == "profile" and uploaded_file:
            try:
                imgkit = ImageKitClient(file=uploaded_file)
                result = imgkit.upload_media
                uploaded_file_url = result['url']
            except Exception as e:
                return Response(
                    {"error": f"File upload failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Update settings
        try:
            if update_user_settings(user, section, settings_data, uploaded_file_url):
                # Clear cache for this user
                cache_pattern = f"owner_{user.id}_*"
                # cache.delete_pattern(cache_pattern)
                if cache_pattern:
                    cache.delete(cache_pattern)
                    
                
                return Response(
                    {
                        "message": f"{section.capitalize()} settings updated successfully.",
                        "updated_data": settings_data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": f"Invalid section '{section}' or update failed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(
        {"error": "Method not allowed"}, 
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )




# ============================================
# consumers.py - Simplified (auth handled by middleware)
# ============================================

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseAuthenticatedConsumer(AsyncWebsocketConsumer):
    """Base consumer - authentication handled by middleware"""
    
    async def connect(self):
        self.user = self.scope.get("user")
        
        logger.info(f"Connection attempt - User: {self.user}, Is authenticated: {self.user.is_authenticated if hasattr(self.user, 'is_authenticated') else False}")
        
        # Check if user is authenticated
        if not self.user or not hasattr(self.user, 'is_authenticated') or not self.user.is_authenticated:
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'auth_error',
                'error': 'Authentication required. Please login first.',
                'details': 'No valid JWT token found in cookies'
            }))
            await self.close(code=4003)
            return
        
        # Accept connection
        await self.accept()
        
        # Send success message
        await self.send(text_data=json.dumps({
            'type': 'connection_success',
            'message': f'Authenticated as {self.user.username}',
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            }
        }))
        
        logger.info(f"WebSocket connection accepted for user: {self.user.username}")


class OrdersOverviewConsumer(BaseAuthenticatedConsumer):
    """WebSocket for dashboard statistics overview"""
    
    async def connect(self):
        await super().connect()
        
        # Only send data if authenticated
        if self.user and self.user.is_authenticated:
            try:
                await self.send_overview_data()
            except Exception as e:
                logger.error(f"Error sending overview: {str(e)}", exc_info=True)
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': str(e)
                }))
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_overview_data()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': f'Unknown action: {action}'
                }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': str(e)
            }))
    
    async def send_overview_data(self):
        try:
            logger.info(f"Fetching overview data for user: {self.user.username}")
            
            # Check if user has unique_url
            if not hasattr(self.user, 'unique_url'):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': 'User does not have unique_url attribute'
                }))
                return
            
            # Get dashboard stats (implement your logic here)
            dashboard_stats = await self.get_dashboard_stats()
            
            # Send response
            await self.send(text_data=json.dumps({
                "type": "orders_overview",
                "OrderOverview": [{
                    "unique_url": self.user.unique_url,
                    "dashboard_stats": dashboard_stats
                }]
            }))
            
        except Exception as e:
            logger.error(f"Error in send_overview_data: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f'Failed to fetch dashboard overview: {str(e)}'
            }))
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        """Fetch dashboard statistics"""
        try:
            from ownerside.utils import get_dashboard_stats, serialize_mongo_data
            dashboard_stats = get_dashboard_stats(self.user.unique_url)
            return serialize_mongo_data(dashboard_stats)
        except ImportError:
            # Return mock data if utils don't exist
            return {
                "total_orders": 42,
                "total_revenue": 12345.67,
                "pending_orders": 5
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return {"error": str(e)}


class RecentOrdersConsumer(BaseAuthenticatedConsumer):
    """WebSocket for recent orders"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and self.user.is_authenticated:
            try:
                await self.send_orders_data()
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_orders_data()
        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'error': str(e)}))
    
    async def send_orders_data(self):
        try:
            orders = await self.get_recent_orders()
            await self.send(text_data=json.dumps({
                "type": "recent_orders",
                "orders": orders
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'error': str(e)}))
    
    @database_sync_to_async
    def get_recent_orders(self):
        try:
            from smartdocx.models import UploadFiles
            
            # Get orders - avoid .first() for Djongo
            all_orders = list(
                UploadFiles.objects.filter(Owner=self.user)[:100]
            )
            all_orders.sort(key=lambda x: x.Created_at if hasattr(x, 'Created_at') and x.Created_at else timezone.now(), reverse=True)
            
            # Format orders
            return [{
                'order_id': order.OrderId if hasattr(order, 'OrderId') else 'N/A',
                'customer_name': order.CustomerName if hasattr(order, 'CustomerName') else 'Unknown',
                'created_at': order.Created_at.isoformat() if hasattr(order, 'Created_at') and order.Created_at else None,
            } for order in all_orders[:20]]  # Limit to 20 orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return []

