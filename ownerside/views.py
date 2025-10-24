from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from smartdocx.models import UploadFiles, CustomUser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from smartdocx.serializer import UploadFilesSerializer
# Create your views here.
from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

# Initialise environment variables
import environ
env = environ.Env()
environ.Env.read_env()

# # Dashboard Data
# class DashboardView(APIView):
#     # permission_classes = [AllowAny]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user  # Authenticated user
#         print(user)
#         return Response({
#             "message": "Welcome to your dashboard",
#             "user": {
#                 "username": user.username,
#                 "email": user.email,
#                 "unique_url": user.unique_url,
#                 "total_orders": user.total_orders,
#                 "total_revenue": user.total_revenue,
#                 "total_customers": user.total_customers,
#             }
#             # "users": user
#         })
    
# from django.utils import timezone
# from datetime import timedelta
# from django.db.models import Sum, F

# def get_dashboard_stats(unique_url):
#     """
#     Returns today's, yesterday's stats and overall totals for orders, revenue,
#     customers, and printed pages.
#     """
#     today = timezone.now().date()
#     yesterday = today - timedelta(days=1)

#     stats = {}

#     # ---------------- Querysets ----------------
#     today_qs = UploadFiles.objects.filter(Unique_url=unique_url, Created_at__date=today)
#     yesterday_qs = UploadFiles.objects.filter(Unique_url=unique_url, Created_at__date=yesterday)
#     all_qs = UploadFiles.objects.filter(Unique_url=unique_url)

#     # ---------------- Orders ----------------
#     today_orders = today_qs.count()
#     yesterday_orders = yesterday_qs.count()
#     overall_orders = all_qs.count()

#     orders_percent_change = ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders else (100 if today_orders > 0 else 0)
#     stats['orders'] = {
#         "today": today_orders,
#         "yesterday": yesterday_orders,
#         "percent_change": round(orders_percent_change, 2),
#         "overall": overall_orders
#     }

#     # ---------------- Revenue ----------------
#     today_revenue = today_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#     yesterday_revenue = yesterday_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#     overall_revenue = all_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0

#     revenue_percent_change = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue else (100 if today_revenue > 0 else 0)
#     stats['revenue'] = {
#         "today": round(today_revenue, 2),
#         "yesterday": round(yesterday_revenue, 2),
#         "percent_change": round(revenue_percent_change, 2),
#         "overall": round(overall_revenue, 2)
#     }

#     # ---------------- Customers ----------------
#     today_customers = today_qs.values('CustomerName').distinct().count()
#     yesterday_customers = yesterday_qs.values('CustomerName').distinct().count()
#     overall_customers = all_qs.values('CustomerName').distinct().count()

#     customers_percent_change = ((today_customers - yesterday_customers) / yesterday_customers * 100) if yesterday_customers else (100 if today_customers > 0 else 0)
#     stats['customers'] = {
#         "today": today_customers,
#         "yesterday": yesterday_customers,
#         "percent_change": round(customers_percent_change, 2),
#         "overall": overall_customers
#     }

#     # ---------------- Printed Pages ----------------
#     today_pages_data = today_qs.filter(PrintStatus='Pending') \
#         .aggregate(total_pages=Sum(F('NoOfPages') * F('NumberOfCopies')))
#     today_pages = today_pages_data['total_pages'] or 0

#     yesterday_pages_data = yesterday_qs.filter(PrintStatus='Pending') \
#         .aggregate(total_pages=Sum(F('NoOfPages') * F('NumberOfCopies')))
#     yesterday_pages = yesterday_pages_data['total_pages'] or 0

#     # overall_pages_data = all_qs.filter(PrintStatus='Pending') \
#     #     .aggregate(total_pages=Sum(F('NoOfPages') * F('NumberOfCopies')))
#     # overall_pages = overall_pages_data['total_pages'] or 0
#     total_pages = (
#         UploadFiles.objects.filter(Unique_url=unique_url, PrintStatus="Pending")
#         .aggregate(total=Sum(F('NoOfPages') * F('NumberOfCopies')))
#         .get('total', 0)
#     )

#     pages_percent_change = ((today_pages - yesterday_pages) / yesterday_pages * 100) if yesterday_pages else (100 if today_pages > 0 else 0)
#     stats['printed_pages'] = {
#         "today": today_pages,
#         "yesterday": yesterday_pages,
#         "percent_change": round(pages_percent_change, 2),
#         "overall": total_pages
#     }

#     return stats


# # def get_total_customers(unique_url):
# #     return UploadFiles.objects.filter(Unique_url = unique_url).count()

# from django.db.models import Sum
# def get_total_revenue(unique_url):
#     total_revenue = UploadFiles.objects.filter(Unique_url=unique_url).aggregate(total=Sum('PaymentAmount'))['total']
#     return total_revenue if total_revenue else 0.00

# # def get_all_orders(unique_url):
# #     orders = UploadFiles.objects.filter(Unique_url=unique_url).values(
# #         "FileUpload", "PaperSize", "PaperType", "PrintColor", "PrintSide", 
# #         "Binding", "NumberOfCopies", "PaymentStatus", "PaymentAmount", 
# #         "PaymentMethod", "Owner__username", "Updated_at"
# #     )
    
# #     for order in orders:
# #         order["Updated_at"] = datetime.fromtimestamp(order["Updated_at"].timestamp(), ist).strftime("%Y-%m-%d %I:%M:%S %p")
    
# #     return list(orders)


# from django.db.models import F, Sum

# def get_total_printed_pages(unique_url):
#     """
#     Returns total printed pages for a specific owner
#     where PrintStatus is 'Completed'.
#     Formula: Total Pages = Σ(NoOfPages × NumberOfCopies)
#     """
#     total_pages = (
#         UploadFiles.objects.filter(Unique_url=unique_url, PrintStatus="Pending")
#         .aggregate(total=Sum(F('NoOfPages') * F('NumberOfCopies')))
#         .get('total', 0)
#     )
#     return total_pages if total_pages else 0

# class OrdersOverview(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
       
#         print("this is user unique url : ", user.unique_url)
#         print("this is user : ", user)
#         dashboard_stats = get_dashboard_stats(user.unique_url)
#         # name = env('NAME')
#         # print("this is environmant Variable : ", name)
#         # print("Dashboard Stats:", dashboard_stats)
#         formatted_OrderOverview = []
#         formatted_OrderOverview.append({
#             # "username": user,
#             "unique_url": user.unique_url,
#             "dashboard_stats": dashboard_stats
#         })
#         return Response({"OrderOverview": formatted_OrderOverview})

    

####################################################################################
# from django.utils import timezone
# from datetime import timedelta, datetime, time
# from django.db.models import Sum, F
# from bson import Decimal128
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

# # ============ Helper Functions ============

# def serialize_mongo_data(data):
#     """Convert MongoDB types (like Decimal128) to JSON-serializable types"""
#     if isinstance(data, Decimal128):
#         return float(data.to_decimal())
#     elif isinstance(data, dict):
#         return {key: serialize_mongo_data(value) for key, value in data.items()}
#     elif isinstance(data, list):
#         return [serialize_mongo_data(item) for item in data]
#     return data


# def get_dashboard_stats(unique_url):
#     """
#     Returns today's, yesterday's stats and overall totals for orders, revenue,
#     customers, and printed pages.
#     """
#     now = timezone.now()
#     today = now.date()
#     yesterday = today - timedelta(days=1)

#     # Create datetime ranges for filtering
#     today_start = datetime.combine(today, time.min)
#     today_end = datetime.combine(today, time.max)
#     yesterday_start = datetime.combine(yesterday, time.min)
#     yesterday_end = datetime.combine(yesterday, time.max)

#     # Make timezone-aware if needed
#     if timezone.is_aware(now):
#         today_start = timezone.make_aware(today_start)
#         today_end = timezone.make_aware(today_end)
#         yesterday_start = timezone.make_aware(yesterday_start)
#         yesterday_end = timezone.make_aware(yesterday_end)

#     stats = {}

#     # ---------------- Querysets ----------------
#     today_qs = UploadFiles.objects.filter(
#         Unique_url=unique_url,
#         Created_at__gte=today_start,
#         Created_at__lte=today_end
#     )
#     yesterday_qs = UploadFiles.objects.filter(
#         Unique_url=unique_url,
#         Created_at__gte=yesterday_start,
#         Created_at__lte=yesterday_end
#     )
#     all_qs = UploadFiles.objects.filter(Unique_url=unique_url)

#     # ---------------- Orders ----------------
#     today_orders = today_qs.count()
#     yesterday_orders = yesterday_qs.count()
#     overall_orders = all_qs.count()

#     orders_percent_change = (
#         ((today_orders - yesterday_orders) / yesterday_orders * 100) 
#         if yesterday_orders else (100 if today_orders > 0 else 0)
#     )
#     stats['orders'] = {
#         "today": today_orders,
#         "yesterday": yesterday_orders,
#         "percent_change": round(orders_percent_change, 2),
#         "overall": overall_orders
#     }

#     # ---------------- Revenue ----------------
#     today_revenue = today_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#     yesterday_revenue = yesterday_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#     overall_revenue = all_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0

#     # Convert Decimal128 to float
#     today_revenue = float(today_revenue.to_decimal()) if isinstance(today_revenue, Decimal128) else float(today_revenue)
#     yesterday_revenue = float(yesterday_revenue.to_decimal()) if isinstance(yesterday_revenue, Decimal128) else float(yesterday_revenue)
#     overall_revenue = float(overall_revenue.to_decimal()) if isinstance(overall_revenue, Decimal128) else float(overall_revenue)

#     revenue_percent_change = (
#         ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) 
#         if yesterday_revenue else (100 if today_revenue > 0 else 0)
#     )
#     stats['revenue'] = {
#         "today": round(today_revenue, 2),
#         "yesterday": round(yesterday_revenue, 2),
#         "percent_change": round(revenue_percent_change, 2),
#         "overall": round(overall_revenue, 2)
#     }

#     # ---------------- Customers ----------------
#     # Use Python sets to count distinct customers (Djongo doesn't handle .distinct().count() well)
#     today_customer_names = set(
#         obj.CustomerName for obj in today_qs.only('CustomerName') 
#         if obj.CustomerName
#     )
#     yesterday_customer_names = set(
#         obj.CustomerName for obj in yesterday_qs.only('CustomerName') 
#         if obj.CustomerName
#     )
#     overall_customer_names = set(
#         obj.CustomerName for obj in all_qs.only('CustomerName') 
#         if obj.CustomerName
#     )
    
#     today_customers = len(today_customer_names)
#     yesterday_customers = len(yesterday_customer_names)
#     overall_customers = len(overall_customer_names)

#     customers_percent_change = (
#         ((today_customers - yesterday_customers) / yesterday_customers * 100) 
#         if yesterday_customers else (100 if today_customers > 0 else 0)
#     )
#     stats['customers'] = {
#         "today": today_customers,
#         "yesterday": yesterday_customers,
#         "percent_change": round(customers_percent_change, 2),
#         "overall": overall_customers
#     }

#     # ---------------- Printed Pages ----------------
#     # Calculate in Python since Djongo doesn't support F() expressions in aggregation
#     today_pending = today_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
#     today_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in today_pending
#     )

#     yesterday_pending = yesterday_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
#     yesterday_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in yesterday_pending
#     )

#     all_pending = all_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
#     total_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in all_pending
#     )

#     pages_percent_change = (
#         ((today_pages - yesterday_pages) / yesterday_pages * 100) 
#         if yesterday_pages else (100 if today_pages > 0 else 0)
#     )
#     stats['printed_pages'] = {
#         "today": int(today_pages),
#         "yesterday": int(yesterday_pages),
#         "percent_change": round(pages_percent_change, 2),
#         "overall": int(total_pages)
#     }

#     return stats


# def get_total_revenue(unique_url):
#     """Get total revenue for a unique_url"""
#     total_revenue = UploadFiles.objects.filter(
#         Unique_url=unique_url
#     ).aggregate(total=Sum('PaymentAmount'))['total']
    
#     if total_revenue:
#         if isinstance(total_revenue, Decimal128):
#             return float(total_revenue.to_decimal())
#         return float(total_revenue)
#     return 0.00


# def get_total_printed_pages(unique_url):
#     """
#     Returns total printed pages for a specific owner
#     where PrintStatus is 'Pending'.
#     Formula: Total Pages = Σ(NoOfPages × NumberOfCopies)
#     """
#     pending_files = UploadFiles.objects.filter(
#         Unique_url=unique_url, 
#         PrintStatus="Pending"
#     ).only('NoOfPages', 'NumberOfCopies')
    
#     total_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in pending_files
#     )
    
#     return int(total_pages)


# # ============ API Views ============

# class OrdersOverview(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
       
#         print("this is user unique url:", user.unique_url)
#         print("this is user:", user)
        
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
#         print(user)
        
#         # Get user data and serialize
#         user_data = {
#             "username": user.username,
#             "email": user.email,
#             "unique_url": user.unique_url,
#             "total_orders": user.total_orders,
#             "total_revenue": serialize_mongo_data(user.total_revenue),
#             "total_customers": user.total_customers,
#         }
        
#         return Response({
#             "message": "Welcome to your dashboard",
#             "user": user_data
#         })





# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from django.utils.timezone import localtime
# # from .models import UploadFiles


# class RecentOrdersView(APIView):
#     """
#     Return all recent orders for the logged-in user (shop owner),
#     including full file path and public file URL.
#     """
#     permission_classes = [IsAuthenticated]  # or [AllowAny] if not using auth

#     def get(self, request):
#         user = request.user
#         print("Logged-in user:", user)

#         if not user or user.is_anonymous:
#             return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             # Get all orders belonging to this owner
#             all_orders = UploadFiles.objects.filter(Owner=user).order_by('-Created_at')
#             formatted_orders = []

#             for order in all_orders:
#                 # File system path (absolute)
#                 # file_path = getattr(order.FileUpload, 'path', None) if order.FileUpload else None

#                 # # Public file URL
#                 # file_url = request.build_absolute_uri(order.FileUpload.url) if order.FileUpload else None

#                 formatted_orders.append({
#                     "id": order.OrderId or f"Order-{order.id}",
#                     "customer": order.CustomerName or "Unknown Customer",
#                     "date": localtime(order.Created_at).strftime("%b %d, %Y"),
#                     "amount": f"₹{order.PaymentAmount:.2f}" if order.PaymentAmount else "₹0.00",
#                     "status": order.PrintStatus or "Pending",
#                     "file_url": order.FileUpload,
#                     "file_path": order.FileUpload,  # ✅ unique per file
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

#             return Response({"orders": formatted_orders}, status=status.HTTP_200_OK)

#         except Exception as e:
#             print("Error fetching orders:", str(e))
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#############################################################


from django.utils import timezone
from datetime import timedelta, datetime, time
from django.db.models import Sum, F
from bson import Decimal128
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# ============ Helper Functions ============

def convert_decimal128(value):
    """Safely convert Decimal128 to float"""
    if value is None:
        return 0
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    if isinstance(value, Decimal):
        return float(value)
    return float(value) if value else 0


def serialize_mongo_data(data):
    """Convert MongoDB types (like Decimal128) to JSON-serializable types"""
    if isinstance(data, Decimal128):
        return float(data.to_decimal())
    elif isinstance(data, dict):
        return {key: serialize_mongo_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    return data


def get_dashboard_stats(unique_url):
    """
    Returns today's, yesterday's stats and overall totals for orders, revenue,
    customers, and printed pages.
    """
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)

    # Create datetime ranges for filtering
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)
    yesterday_start = datetime.combine(yesterday, time.min)
    yesterday_end = datetime.combine(yesterday, time.max)

    # Make timezone-aware if needed
    if timezone.is_aware(now):
        today_start = timezone.make_aware(today_start)
        today_end = timezone.make_aware(today_end)
        yesterday_start = timezone.make_aware(yesterday_start)
        yesterday_end = timezone.make_aware(yesterday_end)

    stats = {}

    # ---------------- Querysets ----------------
    today_qs = UploadFiles.objects.filter(
        Unique_url=unique_url,
        Created_at__gte=today_start,
        Created_at__lte=today_end
    )
    yesterday_qs = UploadFiles.objects.filter(
        Unique_url=unique_url,
        Created_at__gte=yesterday_start,
        Created_at__lte=yesterday_end
    )
    all_qs = UploadFiles.objects.filter(Unique_url=unique_url)

    # ---------------- Orders ----------------
    today_orders = today_qs.count()
    yesterday_orders = yesterday_qs.count()
    overall_orders = all_qs.count()

    orders_percent_change = (
        ((today_orders - yesterday_orders) / yesterday_orders * 100) 
        if yesterday_orders else (100 if today_orders > 0 else 0)
    )
    stats['orders'] = {
        "today": today_orders,
        "yesterday": yesterday_orders,
        "percent_change": round(orders_percent_change, 2),
        "overall": overall_orders
    }

    # ---------------- Revenue ----------------
    # METHOD 1: Calculate manually to avoid aggregate() issues
    today_revenue = sum(
        convert_decimal128(obj.PaymentAmount) 
        for obj in today_qs.only('PaymentAmount')
    )
    yesterday_revenue = sum(
        convert_decimal128(obj.PaymentAmount) 
        for obj in yesterday_qs.only('PaymentAmount')
    )
    overall_revenue = sum(
        convert_decimal128(obj.PaymentAmount) 
        for obj in all_qs.only('PaymentAmount')
    )

    revenue_percent_change = (
        ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) 
        if yesterday_revenue else (100 if today_revenue > 0 else 0)
    )
    stats['revenue'] = {
        "today": round(today_revenue, 2),
        "yesterday": round(yesterday_revenue, 2),
        "percent_change": round(revenue_percent_change, 2),
        "overall": round(overall_revenue, 2)
    }

    # ---------------- Customers ----------------
    # Use Python sets to count distinct customers (Djongo doesn't handle .distinct().count() well)
    today_customer_names = set(
        obj.CustomerName for obj in today_qs.only('CustomerName') 
        if obj.CustomerName
    )
    yesterday_customer_names = set(
        obj.CustomerName for obj in yesterday_qs.only('CustomerName') 
        if obj.CustomerName
    )
    overall_customer_names = set(
        obj.CustomerName for obj in all_qs.only('CustomerName') 
        if obj.CustomerName
    )
    
    today_customers = len(today_customer_names)
    yesterday_customers = len(yesterday_customer_names)
    overall_customers = len(overall_customer_names)

    customers_percent_change = (
        ((today_customers - yesterday_customers) / yesterday_customers * 100) 
        if yesterday_customers else (100 if today_customers > 0 else 0)
    )
    stats['customers'] = {
        "today": today_customers,
        "yesterday": yesterday_customers,
        "percent_change": round(customers_percent_change, 2),
        "overall": overall_customers
    }

    # ---------------- Printed Pages ----------------
    # Calculate in Python since Djongo doesn't support F() expressions in aggregation
    today_pending = today_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
    today_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in today_pending
    )

    yesterday_pending = yesterday_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
    yesterday_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in yesterday_pending
    )

    all_pending = all_qs.filter(PrintStatus='Pending').only('NoOfPages', 'NumberOfCopies')
    total_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in all_pending
    )

    pages_percent_change = (
        ((today_pages - yesterday_pages) / yesterday_pages * 100) 
        if yesterday_pages else (100 if today_pages > 0 else 0)
    )
    stats['printed_pages'] = {
        "today": int(today_pages),
        "yesterday": int(yesterday_pages),
        "percent_change": round(pages_percent_change, 2),
        "overall": int(total_pages)
    }

    return stats


def get_total_revenue(unique_url):
    """Get total revenue for a unique_url"""
    # Calculate manually to avoid Decimal128 conversion issues
    total_revenue = sum(
        convert_decimal128(obj.PaymentAmount)
        for obj in UploadFiles.objects.filter(Unique_url=unique_url).only('PaymentAmount')
    )
    return round(total_revenue, 2)


def get_total_printed_pages(unique_url):
    """
    Returns total printed pages for a specific owner
    where PrintStatus is 'Pending'.
    Formula: Total Pages = Σ(NoOfPages × NumberOfCopies)
    """
    pending_files = UploadFiles.objects.filter(
        Unique_url=unique_url, 
        PrintStatus="Pending"
    ).only('NoOfPages', 'NumberOfCopies')
    
    total_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in pending_files
    )
    
    return int(total_pages)


# ============ API Views ============

class OrdersOverview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
       
        print("this is user unique url:", user.unique_url)
        print("this is user:", user)
        
        dashboard_stats = get_dashboard_stats(user.unique_url)
        
        # Serialize the data to handle Decimal128
        dashboard_stats = serialize_mongo_data(dashboard_stats)
        
        formatted_OrderOverview = [{
            "unique_url": user.unique_url,
            "dashboard_stats": dashboard_stats
        }]
        
        return Response({"OrderOverview": formatted_OrderOverview})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user)
        
        # Get user data and serialize
        user_data = {
            "username": user.username,
            "email": user.email,
            "unique_url": user.unique_url,
            "total_orders": user.total_orders,
            "total_revenue": serialize_mongo_data(user.total_revenue),
            "total_customers": user.total_customers,
        }
        
        return Response({
            "message": "Welcome to your dashboard",
            "user": user_data
        })

# import localtime
from django.utils.timezone import localtime
class RecentOrdersView(APIView):
    """
    Return all recent orders for the logged-in user (shop owner),
    including full file path and public file URL.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print("Logged-in user:", user)

        if not user or user.is_anonymous:
            return Response({"error": "User not authenticated"}, status=401)

        try:
            # Get all orders belonging to this owner
            all_orders = UploadFiles.objects.filter(Owner=user).order_by('-Created_at')
            formatted_orders = []

            for order in all_orders:
                formatted_orders.append({
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
                })

            return Response({"orders": formatted_orders}, status=200)

        except Exception as e:
            print("Error fetching orders:", str(e))
            return Response({"error": str(e)}, status=500)



































# from django.db.models import Sum, Count
# from django.utils import timezone
# from datetime import timedelta, datetime
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

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
#                 daily_qs = qs.filter(Created_at__date=day)
#                 revenue = daily_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 orders = daily_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

#         # elif filter_type == "week":
#         #     # Last 4 weeks
#         #     for i in range(3, -1, -1):
#         #         start_week = now - timedelta(weeks=i, days=now.weekday())
#         #         end_week = start_week + timedelta(days=6)
#         #         labels.append(f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b')}")
#         #         weekly_qs = qs.filter(Created_at__date=[start_week.date(), end_week.date()])
#         #         revenue = weekly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#         #         orders = weekly_qs.count()
#         #         revenue_data.append(round(revenue, 2))
#         #         orders_data.append(orders)
#         elif filter_type == "week":
#             # Last 4 weeks
#             for i in range(3, -1, -1):
#                 start_week = now - timedelta(weeks=i, days=now.weekday())
#                 end_week = start_week + timedelta(days=6)
#                 labels.append(f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b')}")

#                 # ✅ Correct range filter
#                 weekly_qs = qs.filter(Created_at__date__range=[start_week.date(), end_week.date()])

#                 revenue = weekly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 orders = weekly_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)


#         elif filter_type == "month":
#             # Current year, 12 months
#             year = now.year
#             for month in range(1, 13):
#                 labels.append(datetime(year, month, 1).strftime("%b"))
#                 monthly_qs = qs.filter(Created_at__year=year, Created_at__month=month)
#                 revenue = monthly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 orders = monthly_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

#         elif filter_type == "overall":
#             # All time grouped by month
#             qs_all = qs.order_by('Updated_at')
#             months = qs_all.dates('Updated_at', 'month')
#             for dt in months:
#                 labels.append(dt.strftime("%b %Y"))
#                 month_qs = qs.filter(Created_at__year=dt.year, Created_at__month=dt.month)
#                 revenue = month_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
#                 orders = month_qs.count()
#                 revenue_data.append(round(revenue, 2))
#                 orders_data.append(orders)

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


from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime, time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class OrdersChartData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns chart data based on 'filter' query param: day, week, month, overall
        """
        filter_type = request.GET.get("filter", "day")  # default day
        user = request.user
        now = timezone.now()
        labels = []
        revenue_data = []
        orders_data = []

        qs = UploadFiles.objects.filter(Unique_url=user.unique_url)

        if filter_type == "day":
            # Last 7 days
            for i in range(6, -1, -1):
                day = now - timedelta(days=i)
                labels.append(day.strftime("%d %b"))
                
                # ✅ FIXED: Use date range instead of __date lookup
                day_start = datetime.combine(day.date(), time.min)
                day_end = datetime.combine(day.date(), time.max)
                
                # Make timezone-aware if using timezone
                if timezone.is_aware(now):
                    day_start = timezone.make_aware(day_start)
                    day_end = timezone.make_aware(day_end)
                
                daily_qs = qs.filter(Created_at__gte=day_start, Created_at__lte=day_end)
                # revenue = daily_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
                revenue = sum(
                    convert_decimal128(obj.PaymentAmount) 
                    for obj in daily_qs.only('PaymentAmount')
                )
                orders = daily_qs.count()
                revenue_data.append(round(revenue, 2))
                orders_data.append(orders)

        elif filter_type == "week":
            # Last 4 weeks
            for i in range(3, -1, -1):
                start_week = now - timedelta(weeks=i, days=now.weekday())
                end_week = start_week + timedelta(days=6)
                labels.append(f"{start_week.strftime('%d %b')} - {end_week.strftime('%d %b')}")

                # ✅ FIXED: Use datetime range with time bounds
                week_start = datetime.combine(start_week.date(), time.min)
                week_end = datetime.combine(end_week.date(), time.max)
                
                if timezone.is_aware(now):
                    week_start = timezone.make_aware(week_start)
                    week_end = timezone.make_aware(week_end)

                weekly_qs = qs.filter(Created_at__gte=week_start, Created_at__lte=week_end)

                # revenue = weekly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
                revenue = sum(
                    convert_decimal128(obj.PaymentAmount) 
                    for obj in weekly_qs.only('PaymentAmount')
                )
                orders = weekly_qs.count()
                revenue_data.append(round(revenue, 2))
                orders_data.append(orders)

        elif filter_type == "month":
            # Current year, 12 months
            year = now.year
            for month in range(1, 13):
                labels.append(datetime(year, month, 1).strftime("%b"))
                
                # ✅ FIXED: Use date range for month
                month_start = datetime(year, month, 1)
                if month == 12:
                    month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
                
                if timezone.is_aware(now):
                    month_start = timezone.make_aware(month_start)
                    month_end = timezone.make_aware(month_end)
                
                monthly_qs = qs.filter(Created_at__gte=month_start, Created_at__lte=month_end)
                # revenue = monthly_qs.aggregate(total=Sum('PaymentAmount')).get('total') or 0
                revenue = sum(
                    convert_decimal128(obj.PaymentAmount) 
                    for obj in monthly_qs.only('PaymentAmount')
                )
                orders = monthly_qs.count()
                revenue_data.append(round(revenue, 2))
                orders_data.append(orders)

        elif filter_type == "overall":
            # All time grouped by month
            # ✅ FIXED: Use Python grouping instead of .dates() which doesn't work well with Djongo
            all_records = qs.order_by('Created_at')
            
            # Group records by month manually
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
                    
                    # month_data[month_key]['revenue'] += (record.PaymentAmount or 0)
                    month_data[month_key]['revenue'] += convert_decimal128(record.PaymentAmount)
                    month_data[month_key]['orders'] += 1
            
            # Sort by month and prepare data
            for month_key in sorted(month_data.keys()):
                data = month_data[month_key]
                labels.append(data['label'])
                revenue_data.append(round(data['revenue'], 2))
                orders_data.append(data['orders'])

        chart_data = {
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

        return Response(chart_data)


class UpdatePrintStatusAPIView(APIView):
    """
    API to update the print status of a specific order to 'Complete'.
    """
    permission_classes = [AllowAny]  # or [AllowAny] if not using auth
    def post(self, request):
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = UploadFiles.objects.get(OrderId=order_id)
            order.PrintStatus = "Complete"
            print("Updating order:", order_id, "to Complete")
            order.save()
            return Response({"message": f"Order {order_id} marked as Complete"}, status=status.HTTP_200_OK)
        except UploadFiles.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)




from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
# from .models import UploadFiles
# from .serializers import UploadFilesSerializer  # assuming you already have this serializer
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_owner_orders(request):
    """
    Returns orders for a specific owner with pagination, search, and date filtering
    """
    owner = request.user
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    print("This is owner from request user : ", owner)
    orders = UploadFiles.objects.filter(Owner=owner).order_by('-Created_at')
    # print("This is orders before filtering : ", orders[1])
    # 🔍 Apply search filter
    if search:
        orders = orders.filter(
            Q(CustomerName__icontains=search) |
            Q(id__icontains=search)
        )

    # 🗓️ Apply date range filter
    if date_from:
        orders = orders.filter(Created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(Created_at__date__lte=date_to)

    # ⚙️ Status filter
    if status and status != "all":
        orders = orders.filter(PrintStatus__iexact=status)

    # 📄 Pagination
    paginator = Paginator(orders, per_page)
    page_obj = paginator.get_page(page)

    serializer = UploadFilesSerializer(page_obj, many=True)

    return Response({
        "orders": serializer.data,
        "total_orders": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })
