# from django.shortcuts import render
# from rest_framework import viewsets, permissions, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from smartdocx.models import UploadFiles, CustomUser
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from smartdocx.serializer import UploadFilesSerializer
# # Create your views here.
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django.db.models import Sum, Count, F
# from django.utils import timezone
# from datetime import timedelta, datetime, time
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.utils.timezone import localtime

# # Helper function to convert Decimal128 to float
# from .utils import serialize_mongo_data, convert_decimal128, get_dashboard_stats



# # Initialise environment variables
# import environ
# env = environ.Env()
# environ.Env.read_env()


# #########################################################
# ############ This is use of Production server

# # ============ API Views ============

# class OrdersOverview(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
       
#         # print("this is user unique url:", user.unique_url)
#         # print("this is user:", user)
        
#         dashboard_stats = get_dashboard_stats(user.unique_url)
        
#         # Serialize the data to handle Decimal128
#         dashboard_stats = serialize_mongo_data(dashboard_stats)
        
#         formatted_OrderOverview = [{
#             "unique_url": user.unique_url,
#             "dashboard_stats": dashboard_stats
#         }]
        
#         return Response({"OrderOverview": formatted_OrderOverview})


# class DashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         # print(user)
        
#         # Get user data and serialize
#         user_data = {
#             "username": user.username,
#             "email": user.email,
#             "unique_url": user.unique_url,
#         }
        
#         return Response({
#             "message": "Welcome to your dashboard",
#             "user": user_data
#         })

# class RecentOrdersView(APIView):
#     """
#     Return all recent orders for the logged-in user (shop owner),
#     including full file path and public file URL.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         print("Logged-in user:", user)

#         if not user or user.is_anonymous:
#             return Response({"error": "User not authenticated"}, status=401)

#         try:
#             # Get all orders belonging to this owner
#             all_orders = UploadFiles.objects.filter(Owner=user).order_by('-Created_at')
#             formatted_orders = []

#             for order in all_orders:
#                 formatted_orders.append({
#                     "id": order.OrderId or f"Order-{order.id}",
#                     "customer": order.CustomerName or "Unknown Customer",
#                     "date": localtime(order.Created_at).strftime("%b %d, %Y"),
#                     "amount": f"₹{convert_decimal128(order.PaymentAmount):.2f}",
#                     "status": order.PrintStatus or "Pending",
#                     "file_url": order.FileUpload,
#                     "file_path": order.FileUpload,
#                     "paper_size": order.PaperSize,
#                     "paper_type": order.PaperType,
#                     "print_color": order.PrintColor,
#                     "print_side": order.PrintSide,
#                     "binding": order.Binding,
#                     "no_of_copies": order.NumberOfCopies,
#                     "no_of_pages": order.NoOfPages,
#                     "transaction_id": order.Transaction_id,
#                     "payment_status": order.PaymentStatus,
#                     "payment_method": order.PaymentMethod,
#                 })

#             return Response({"orders": formatted_orders}, status=200)

#         except Exception as e:
#             print("Error fetching orders:", str(e))
#             return Response({"error": str(e)}, status=500)


# ############ This is use of Production server
# class OrdersChartData(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """
#         Returns chart data based on 'filter' query param: day, week, month, overall
#         """
#         filter_type = request.GET.get("filter", "day")  # default day
#         user = request.user
#         now = timezone.now()
#         labels = []
#         revenue_data = []
#         orders_data = []

#         qs = UploadFiles.objects.filter(Unique_url=user.unique_url)

#         if filter_type == "day":
#             # Last 7 days
#             for i in range(6, -1, -1):
#                 day = now - timedelta(days=i)
#                 labels.append(day.strftime("%d %b"))
                
#                 # ✅ FIXED: Use date range instead of __date lookup
#                 day_start = datetime.combine(day.date(), time.min)
#                 day_end = datetime.combine(day.date(), time.max)
                
#                 # Make timezone-aware if using timezone
#                 if timezone.is_aware(now):
#                     day_start = timezone.make_aware(day_start)
#                     day_end = timezone.make_aware(day_end)
                
#                 daily_qs = qs.filter(Created_at__gte=day_start, Created_at__lte=day_end)
#                 # revenue = daily_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 revenue = sum(
#                     convert_decimal128(obj.PaymentAmount) 
#                     for obj in daily_qs.only('PaymentAmount')
#                 )
#                 orders = daily_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

#         elif filter_type == "week":
#             # Last 4 weeks
#             for i in range(3, -1, -1):
#                 start_week = now - timedelta(weeks=i, days=now.weekday())
#                 end_week = start_week + timedelta(days=6)
#                 labels.append(f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b')}")

#                 # ✅ FIXED: Use datetime range with time bounds
#                 week_start = datetime.combine(start_week.date(), time.min)
#                 week_end = datetime.combine(end_week.date(), time.max)
                
#                 if timezone.is_aware(now):
#                     week_start = timezone.make_aware(week_start)
#                     week_end = timezone.make_aware(week_end)

#                 weekly_qs = qs.filter(Created_at__gte=week_start, Created_at__lte=week_end)

#                 # revenue = weekly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 revenue = sum(
#                     convert_decimal128(obj.PaymentAmount) 
#                     for obj in weekly_qs.only('PaymentAmount')
#                 )
#                 orders = weekly_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

#         elif filter_type == "month":
#             # Current year, 12 months
#             year = now.year
#             for month in range(1, 13):
#                 labels.append(datetime(year, month, 1).strftime("%b"))
                
#                 # ✅ FIXED: Use date range for month
#                 month_start = datetime(year, month, 1)
#                 if month == 12:
#                     month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
#                 else:
#                     month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
                
#                 if timezone.is_aware(now):
#                     month_start = timezone.make_aware(month_start)
#                     month_end = timezone.make_aware(month_end)
                
#                 monthly_qs = qs.filter(Created_at__gte=month_start, Created_at__lte=month_end)
#                 # revenue = monthly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 revenue = sum(
#                     convert_decimal128(obj.PaymentAmount) 
#                     for obj in monthly_qs.only('PaymentAmount')
#                 )
#                 orders = monthly_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

#         elif filter_type == "overall":
#             # All time grouped by month
#             # ✅ FIXED: Use Python grouping instead of .dates() which doesn't work well with Djongo
#             all_records = qs.order_by('Created_at')
            
#             # Group records by month manually
#             month_data = {}
#             for record in all_records:
#                 if record.Created_at:
#                     month_key = record.Created_at.strftime("%Y-%m")
#                     month_label = record.Created_at.strftime("%b %Y")
                    
#                     if month_key not in month_data:
#                         month_data[month_key] = {
#                             'label': month_label,
#                             'revenue': 0.0,
#                             'orders': 0
#                         }
                    
#                     # month_data[month_key]['revenue'] += (record.PaymentAmount or 0)
#                     month_data[month_key]['revenue'] += convert_decimal128(record.PaymentAmount)
#                     month_data[month_key]['orders'] += 1
            
#             # Sort by month and prepare data
#             for month_key in sorted(month_data.keys()):
#                 data = month_data[month_key]
#                 labels.append(data['label'])
#                 revenue_data.append(round(data['revenue'], 2))
#                 orders_data.append(data['orders'])

#         chart_data = {
#             "labels": labels,
#             "datasets": [
#                 {
#                     "label": "Revenue",
#                     "data": revenue_data,
#                     "borderColor": "#0a2463",
#                     "backgroundColor": "rgba(10, 36, 99, 0.1)",
#                     "tension": 0.4,
#                 },
#                 {
#                     "label": "Orders",
#                     "data": orders_data,
#                     "borderColor": "#2176ff",
#                     "backgroundColor": "rgba(33, 118, 255, 0.1)",
#                     "tension": 0.4,
#                 },
#             ],
#         }

#         return Response(chart_data)


# class UpdatePrintStatusAPIView(APIView):
#     """
#     API to update the print status of a specific order to 'Complete'.
#     """
#     permission_classes = [AllowAny]  # or [AllowAny] if not using auth
#     def post(self, request):
#         order_id = request.data.get("order_id")
#         if not order_id:
#             return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             order = UploadFiles.objects.get(OrderId=order_id)
#             order.PrintStatus = "Complete"
#             print("Updating order:", order_id, "to Complete")
#             order.save()
#             return Response({"message": f"Order {order_id} marked as Complete"}, status=status.HTTP_200_OK)
#         except UploadFiles.DoesNotExist:
#             return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_owner_orders(request):
#     """
#     Returns orders for a specific owner with pagination, search, and date filtering
#     """
#     owner = request.user
#     page = int(request.GET.get('page', 1))
#     per_page = int(request.GET.get('per_page', 10))
#     search = request.GET.get('search', '').strip()
#     status = request.GET.get('status', '').strip()
#     date_from = request.GET.get('from', '')
#     date_to = request.GET.get('to', '')
#     print("This is owner from request user : ", owner)
#     orders = UploadFiles.objects.filter(Owner=owner).order_by('-Created_at')
#     # print("This is orders before filtering : ", orders[1])
#     # 🔍 Apply search filter
#     if search:
#         orders = orders.filter(
#             Q(CustomerName__icontains=search) |
#             Q(id__icontains=search)
#         )

#     # 🗓️ Apply date range filter
#     if date_from:
#         orders = orders.filter(Created_at__date__gte=date_from)
#     if date_to:
#         orders = orders.filter(Created_at__date__lte=date_to)

#     # ⚙️ Status filter
#     if status and status != "all":
#         orders = orders.filter(PrintStatus__iexact=status)

#     # 📄 Pagination
#     paginator = Paginator(orders, per_page)
#     page_obj = paginator.get_page(page)

#     serializer = UploadFilesSerializer(page_obj, many=True)

#     return Response({
#         "orders": serializer.data,
#         "total_orders": paginator.count,
#         "total_pages": paginator.num_pages,
#         "current_page": page_obj.number
#     })




# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.utils.timezone import localtime, now
# from datetime import timedelta
# # from .models import UploadFiles  # Adjust based on your models
# from .utils import convert_decimal128
# class RecentActivityView(APIView):
#     """
#     Return recent activities for the logged-in user (shop owner).
#     Activities include: new orders, payments, deliveries, and new customers.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         print("Logged-in user:", user)

#         if not user or user.is_anonymous:
#             return Response({"error": "User not authenticated"}, status=401)

#         # ✅ Get limit from query params, default to 4
#         limit = int(request.GET.get('limit', 4))

#         try:
#             activities = []
#             activity_id = 1

#             # Get recent time window (last 24 hours)
#             recent_time = now() - timedelta(hours=24)

#             # ✅ 1. New Orders Activity
#             new_orders = UploadFiles.objects.filter(
#                 Owner=user,
#                 Created_at__gte=recent_time
#             ).order_by('-Created_at')[:5]

#             for order in new_orders:
#                 time_diff = self.get_time_ago(order.Created_at)
#                 activities.append({
#                     "id": activity_id,
#                     "type": "order",
#                     "message": f"New order from {order.CustomerName or 'Unknown Customer'}",
#                     "time": time_diff,
#                     "timestamp": order.Created_at.isoformat(),
#                     "order_id": order.OrderId,
#                 })
#                 activity_id += 1

#             # ✅ 2. Payment Activities
#             paid_orders = UploadFiles.objects.filter(
#                 Owner=user,
#                 PaymentStatus=True,
#                 Updated_at__gte=recent_time
#             ).order_by('-Updated_at')[:5]

#             for order in paid_orders:
#                 time_diff = self.get_time_ago(order.Updated_at)
#                 activities.append({
#                     "id": activity_id,
#                     "type": "payment",
#                     "message": f"Payment received for Order #{order.OrderId}",
#                     "time": time_diff,
#                     "timestamp": order.Updated_at.isoformat(),
#                     "order_id": order.OrderId,
#                     "amount": f"₹{convert_decimal128(order.PaymentAmount):.2f}",
#                 })
#                 activity_id += 1

#             # ✅ 3. Delivery/Completed Orders Activity
#             completed_orders = UploadFiles.objects.filter(
#                 Owner=user,
#                 PrintStatus="Complete",
#                 Updated_at__gte=recent_time
#             ).order_by('-Updated_at')[:5]

#             for order in completed_orders:
#                 time_diff = self.get_time_ago(order.Updated_at)
#                 activities.append({
#                     "id": activity_id,
#                     "type": "delivery",
#                     "message": f"Order #{order.OrderId} delivered",
#                     "time": time_diff,
#                     "timestamp": order.Updated_at.isoformat(),
#                     "order_id": order.OrderId,
#                 })
#                 activity_id += 1

#             # ✅ 4. New Customer Registrations (ONLY UNIQUE CUSTOMERS)
#             try:
#                 # Get all customer names from orders in recent time
#                 recent_customer_names = UploadFiles.objects.filter(
#                     Owner=user,
#                     Created_at__gte=recent_time
#                 ).values_list('CustomerName', flat=True).distinct()

#                 # Check if this customer existed before the recent time window
#                 for customer_name in recent_customer_names:
#                     if not customer_name:
#                         continue
                    
#                     # Check if this customer had any orders BEFORE the recent time window
#                     previous_orders = UploadFiles.objects.filter(
#                         Owner=user,
#                         CustomerName=customer_name,
#                         Created_at__lt=recent_time
#                     ).exists()
                    
#                     # ✅ Only add if customer is NEW (no previous orders)
#                     if not previous_orders:
#                         # Get the first order of this new customer
#                         first_order = UploadFiles.objects.filter(
#                             Owner=user,
#                             CustomerName=customer_name,
#                             Created_at__gte=recent_time
#                         ).order_by('Created_at').first()
                        
#                         if first_order:
#                             time_diff = self.get_time_ago(first_order.Created_at)
#                             activities.append({
#                                 "id": activity_id,
#                                 "type": "customer",
#                                 "message": f"New customer registration: {customer_name}",
#                                 "time": time_diff,
#                                 "timestamp": first_order.Created_at.isoformat(),
#                                 "customer_name": customer_name,
#                             })
#                             activity_id += 1
                            
#             except Exception as e:
#                 print(f"Error fetching customers: {str(e)}")

#             # Sort all activities by timestamp (most recent first)
#             activities.sort(key=lambda x: x['timestamp'], reverse=True)

#             # ✅ Return limited activities based on query param
#             return Response({"activities": activities[:limit]}, status=200)

#         except Exception as e:
#             print("Error fetching recent activities:", str(e))
#             return Response({"error": str(e)}, status=500)

#     def get_time_ago(self, timestamp):
#         """
#         Calculate human-readable time difference
#         """
#         now_time = now()
#         diff = now_time - timestamp

#         if diff.days > 0:
#             if diff.days == 1:
#                 return "1 day ago"
#             return f"{diff.days} days ago"
        
#         hours = diff.seconds // 3600
#         if hours > 0:
#             if hours == 1:
#                 return "1 hour ago"
#             return f"{hours} hours ago"
        
#         minutes = diff.seconds // 60
#         if minutes > 0:
#             if minutes == 1:
#                 return "1 min ago"
#             return f"{minutes} min ago"
        
#         return "Just now"
    

# # from customerside.utils import ImageKitClient

# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def upload_file_to_imagekit(request):
# #     if request.method == 'POST':
# #         print("File upload view initiated.")
# #         uploaded_file = request.FILES.get('file')
# #         print("Uploaded file:", uploaded_file)
# #         if not uploaded_file:
# #             return Response({"error": "No file uploaded"}, status=400)

# #         try:
# #             imgkit = ImageKitClient(uploaded_file)
# #             result = imgkit.upload_media()
# #             return Response({"url": result['url']}, status=200)
# #         except Exception as e:
# #             return Response({"error": str(e)}, status=500)

# #     return Response({"error": "Invalid request method"}, status=405)



# import json # Used for parsing the 'data' field
# from customerside.utils import ImageKitClient

# def update_user_settings(user, section, data, uploaded_file=None):
#     """
#     Simulates updating user settings based on section.
#     This function has been kept for consistency and mocking the database logic.
#     """
    
#     # In a real application, you should handle potential errors (e.g., integrity errors, validation errors)
#     if section == 'general':
#         # Assuming CustomUser model has fields like shop_name, owner_phone_number, etc.
#         user.shop_name = data.get('shopName', user.shop_name)
#         user.email = data.get('email', user.email)
#         user.owner_phone_number = data.get('phone', user.owner_phone_number)
#         user.owner_shop_address = data.get('address', user.owner_shop_address)
#         # user.currency = data.get('currency', user.currency)
#         # user.timezone = data.get('timezone', user.timezone)
#         user.info_modified = True
        
#         user.save()
#         print("General settings updated for user:", user.username)
#         return True

#     if section == 'profile':
#         user.owner_fullname = data.get('firstName', user.first_name)
#         # user.last_name = data.get('lastName', user.last_name)
#         user.email = data.get('email', user.email)
#         user.owner_shop_image = data.get('avatarFile', user.owner_shop_image)
#         # user.owner_phone_number = data.get('phone', user.owner_phone_number)
#         user.info_modified = True
        
#         user.save()
#         print("Profile settings updated for user:", user.username)
#         return True
    
#     if section == 'notifications':
#         print("Notifications settings update called.")
#         return True
    
#     if section == 'billing':
#         print("Billing settings update called.")
#         return True

    
#     # You would add logic for other sections like 'billing', 'users', etc. here
#     return False

# # --- DRF Function-Based API View (Based on user's structure) ---

# # NOTE: Ensure you uncomment and import the necessary DRF decorators in your actual settings file
# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# # @parser_classes([MultiPartParser, FormParser])
# def DashboardSettings(request):
#     print("Dashboard Settings view initiated.")
    
#     # In a decorated view with IsAuthenticated, request.user is the authenticated user object
#     user = request.user 

#     # --- GET Request Handling ---
#     if request.method == 'GET':
#         # This lookup is redundant if IsAuthenticated is used, as request.user is already the user instance.
#         # But kept in case CustomUser is used for extra context lookup.
#         # We will simplify by just returning user details:
#         if user.is_authenticated:
#             return Response({"message": f"User Found: {user.username}. Use POST to update settings."})
#         else:
#             return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
#     # --- POST Request Handling (Settings Update) ---
#     if request.method == 'POST':
#         # 1. Access the submitted data via request.data (correct DRF method)
#         # request.data contains all fields (section, data) sent from the frontend.
        
#         # Get the 'section' (e.g., 'general')
#         section = request.data.get('section')
        
#         # Get the 'data' containing the settings values (this might be a string if sent via multipart/form-data)
#         raw_data = request.data.get('data')
        
#         # 2. Access File Object via request.FILES (File key is assumed to be 'avatarFile')
#         uploaded_file = request.FILES.get('avatar') 
        
#         # print("This is raw_data: ", raw_data)
#         print("This is section: ", section)
#         # print(f"File received: {uploaded_file.name if uploaded_file else 'None'}")

        
#         # --- Critical Parsing Step (Handles multipart/form-data string issue) ---
#         settings_data = {}
        
#         if not raw_data:
#             return Response({"error": "Missing 'data' field in request."}, status=status.HTTP_400_BAD_REQUEST)

#         # If the frontend uses multipart/form-data, non-file fields arrive as strings, 
#         # so we must parse the 'data' field back into a JSON object (dictionary).
#         if isinstance(raw_data, str):
#             try:
#                 settings_data = json.loads(raw_data)
#             except json.JSONDecodeError:
#                 return Response({"error": "Invalid JSON format in the 'data' field."}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # If the frontend used application/json, it's already a dictionary
#             settings_data = raw_data


#         # 2. Check essential fields
#         if not section or not settings_data:
#             return Response(
#                 {"error": "Both 'section' and 'data' are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         if section == "profile":
#             imgkit = ImageKitClient(file = uploaded_file)
#             result = imgkit.upload_media
#             uploaded_file_url = result['url']
#             settings_data['avatarFile'] = uploaded_file_url  # Include file in settings data if needed

#         print("Parsed settings_data:", settings_data)

#         # 3. Process and Update
#         try:
#             # We use request.user directly since the user is authenticated
            
#             if update_user_settings(user, section, settings_data, uploaded_file):
#                 return Response(
#                     {"message": f"{section.capitalize()} settings updated successfully.", "updated_data": settings_data},
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                  return Response(
#                     {"error": f"Invalid section '{section}' provided or update failed."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                
#         except Exception as e:
#             print(f"Error during settings update: {e}")
#             return Response(
#                 {"error": f"Server processing error: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




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
        }
        
        return Response({
            "message": "Welcome to your dashboard",
            "user": user_data
        })


# class RecentOrdersView(APIView):
#     """Return recent orders for the logged-in user (owner)"""
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
        
#         if not user or user.is_anonymous:
#             return Response(
#                 {"error": "User not authenticated"}, 
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         try:
#             # Get all orders with select_related/prefetch_related if needed
#             all_orders = UploadFiles.objects.filter(
#                 Owner=user
#             ).order_by('-Created_at')
            
#             # Format orders using helper function
#             formatted_orders = [format_order(order) for order in all_orders]

#             return Response({"orders": formatted_orders}, status=status.HTTP_200_OK)

#         except Exception as e:
#             print(f"Error fetching orders: {str(e)}")
#             return Response(
#                 {"error": f"Failed to fetch orders: {str(e)}"}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )





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


# ============================================
# ORDER MANAGEMENT
# ============================================

class UpdatePrintStatusAPIView(APIView):
    """Update print status of a specific order to 'Complete'"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        order_id = request.data.get("order_id")
        
        if not order_id:
            return Response(
                {"error": "order_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = UploadFiles.objects.get(OrderId=order_id)
            order.PrintStatus = "Complete"
            order.save()
            
            print(f"Updated order {order_id} to Complete")
            
            return Response(
                {"message": f"Order {order_id} marked as Complete"}, 
                status=status.HTTP_200_OK
            )
            
        except UploadFiles.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
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
            user.info_modified = True
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
    if request.method == 'GET':
        return Response({
            "message": f"User Found: {user.username}. Use POST to update settings.",
            "user": {
                "username": user.username,
                "email": user.email,
                "shop_name": getattr(user, 'shop_name', ''),
                "owner_fullname": getattr(user, 'owner_fullname', ''),
                "owner_phone_number": getattr(user, 'owner_phone_number', ''),
                "owner_shop_address": getattr(user, 'owner_shop_address', ''),
                "owner_shop_image": getattr(user, 'owner_shop_image', ''),
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