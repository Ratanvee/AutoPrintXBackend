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






################################################################################################

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

# # Initialise environment variables
# import environ
# env = environ.Env()
# environ.Env.read_env()
# from django.utils import timezone
# from datetime import timedelta, datetime, time
# from django.db.models import Sum, F
# from bson import Decimal128
# from decimal import Decimal
# from rest_framework.response import Response

# # ============ Helper Functions ============

# def convert_decimal128(value):
#     """Safely convert Decimal128 to float"""
#     if value is None:
#         return 0
#     if isinstance(value, Decimal128):
#         return float(value.to_decimal())
#     if isinstance(value, Decimal):
#         return float(value)
#     return float(value) if value else 0


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
#     # METHOD 1: Calculate manually to avoid aggregate() issues
#     today_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in today_qs.only('PaymentAmount')
#     )
#     yesterday_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in yesterday_qs.only('PaymentAmount')
#     )
#     overall_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in all_qs.only('PaymentAmount')
#     )

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
#     today_pending = today_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
#     today_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in today_pending
#     )

#     yesterday_pending = yesterday_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
#     yesterday_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in yesterday_pending
#     )

#     all_pending = all_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
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













from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, F, Max
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import timedelta, datetime, time
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import environ

from smartdocx.models import UploadFiles, CustomUser
from smartdocx.serializer import UploadFilesSerializer
from bson import Decimal128
from decimal import Decimal

# # Initialize environment variables
# env = environ.Env()
# environ.Env.read_env()


# # ============================================
# # HELPER FUNCTIONS
# # ============================================

# def convert_decimal128(value):
#     """Safely convert Decimal128 to float"""
#     if value is None:
#         return 0
#     if isinstance(value, Decimal128):
#         return float(value.to_decimal())
#     if isinstance(value, Decimal):
#         return float(value)
#     return float(value) if value else 0


# def serialize_mongo_data(data):
#     """Convert MongoDB types to JSON-serializable types"""
#     if isinstance(data, Decimal128):
#         return float(data.to_decimal())
#     elif isinstance(data, dict):
#         return {key: serialize_mongo_data(value) for key, value in data.items()}
#     elif isinstance(data, list):
#         return [serialize_mongo_data(item) for item in data]
#     return data


# def get_cache_key(user_id, endpoint):
#     """Generate consistent cache keys"""
#     return f"owner_{user_id}_{endpoint}"


# def get_last_modified_timestamp(user):
#     """Get the last modified timestamp for user's orders"""
#     last_order = UploadFiles.objects.filter(
#         Owner=user
#     ).order_by('-Updated_at').first()
    
#     if last_order and last_order.Updated_at:
#         return last_order.Updated_at.isoformat()
    
#     return None


# def invalidate_user_cache(user_id):
#     """Invalidate all cache for a specific user"""
#     cache_keys = [
#         get_cache_key(user_id, 'recent_orders'),
#         get_cache_key(user_id, 'orders_overview'),
#         get_cache_key(user_id, 'activity_4'),
#     ]
#     for key in cache_keys:
#         cache.delete(key)
#     print(f"✅ Cache invalidated for user {user_id}")


# def format_order(order):
#     """Format order object to consistent dictionary"""
#     return {
#         "id": order.OrderId or f"Order-{order.id}",
#         "customer": order.CustomerName or "Unknown Customer",
#         "date": localtime(order.Created_at).strftime("%b %d, %Y"),
#         "amount": f"₹{convert_decimal128(order.PaymentAmount):.2f}",
#         "status": order.PrintStatus or "Pending",
#         "file_url": order.FileUpload,
#         "file_path": order.FileUpload,
#         "paper_size": order.PaperSize,
#         "paper_type": order.PaperType,
#         "print_color": order.PrintColor,
#         "print_side": order.PrintSide,
#         "binding": order.Binding,
#         "no_of_copies": order.NumberOfCopies,
#         "no_of_pages": order.NoOfPages,
#         "transaction_id": order.Transaction_id,
#         "payment_status": order.PaymentStatus,
#         "payment_method": order.PaymentMethod,
#     }


# # ============================================
# # CACHE INVALIDATION SIGNALS
# # ============================================

# @receiver([post_save, post_delete], sender=UploadFiles)
# def invalidate_orders_cache(sender, instance, **kwargs):
#     """
#     Automatically invalidate cache when orders are created, updated, or deleted
#     """
#     if instance.Owner:
#         invalidate_user_cache(instance.Owner.id)







# # ============================================
# # UPDATED GET_DASHBOARD_STATS WITH CACHING
# # ============================================

# def get_dashboard_stats(unique_url):
#     """
#     Returns today's, yesterday's stats with caching
#     Cache key includes date to auto-invalidate daily
#     """
#     today = timezone.now().date()
#     cache_key = f"dashboard_stats_{unique_url}_{today}"
    
#     # Try cache first
#     cached_stats = cache.get(cache_key)
#     if cached_stats:
#         return cached_stats
    
#     # Calculate stats (existing logic)
#     now = timezone.now()
#     yesterday = today - timedelta(days=1)

#     today_start = datetime.combine(today, time.min)
#     today_end = datetime.combine(today, time.max)
#     yesterday_start = datetime.combine(yesterday, time.min)
#     yesterday_end = datetime.combine(yesterday, time.max)

#     if timezone.is_aware(now):
#         today_start = timezone.make_aware(today_start)
#         today_end = timezone.make_aware(today_end)
#         yesterday_start = timezone.make_aware(yesterday_start)
#         yesterday_end = timezone.make_aware(yesterday_end)

#     stats = {}

#     # Querysets
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

#     # Orders
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

#     # Revenue
#     today_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in today_qs.only('PaymentAmount')
#     )
#     yesterday_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in yesterday_qs.only('PaymentAmount')
#     )
#     overall_revenue = sum(
#         convert_decimal128(obj.PaymentAmount) 
#         for obj in all_qs.only('PaymentAmount')
#     )

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

#     # Customers
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

#     # Printed Pages
#     today_pending = today_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
#     today_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in today_pending
#     )

#     yesterday_pending = yesterday_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
#     yesterday_pages = sum(
#         (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
#         for obj in yesterday_pending
#     )

#     all_pending = all_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
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

#     # Cache for 5 minutes (auto-invalidates daily due to date in key)
#     cache.set(cache_key, stats, 300)
    
#     return stats



# Initialize environment variables
env = environ.Env()
environ.Env.read_env()


# ============================================
# HELPER FUNCTIONS
# ============================================

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
    """Convert MongoDB types to JSON-serializable types"""
    if isinstance(data, Decimal128):
        return float(data.to_decimal())
    elif isinstance(data, dict):
        return {key: serialize_mongo_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    return data


def get_cache_key(user_id, endpoint):
    """Generate consistent cache keys"""
    return f"owner_{user_id}_{endpoint}"


def get_last_modified_timestamp(user):
    """Get the last modified timestamp for user's orders"""
    try:
        last_order = UploadFiles.objects.filter(
            Owner=user
        ).order_by('-Updated_at').first()
        
        if last_order and last_order.Updated_at:
            return last_order.Updated_at.isoformat()
    except Exception as e:
        print(f"Error getting last modified: {e}")
    
    return timezone.now().isoformat()


def invalidate_user_cache(user_id):
    """Invalidate all cache for a specific user"""
    cache_keys = [
        get_cache_key(user_id, 'recent_orders'),
        get_cache_key(user_id, 'orders_overview'),
    ]
    
    # Also invalidate all activity caches (different limits)
    for limit in [4, 10, 20]:
        cache_keys.append(get_cache_key(user_id, f'activity_{limit}'))
    
    for key in cache_keys:
        cache.delete(key)
    
    print(f"✅ Cache invalidated for user {user_id}")


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


def get_dashboard_stats(unique_url):
    """
    Returns today's, yesterday's stats with caching
    Cache key includes date to auto-invalidate daily
    """
    today = timezone.now().date()
    cache_key = f"dashboard_stats_{unique_url}_{today}"
    
    # Try cache first (5 minute cache)
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return cached_stats
    
    # Calculate stats
    now_time = timezone.now()
    yesterday = today - timedelta(days=1)

    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)
    yesterday_start = datetime.combine(yesterday, time.min)
    yesterday_end = datetime.combine(yesterday, time.max)

    if timezone.is_aware(now_time):
        today_start = timezone.make_aware(today_start)
        today_end = timezone.make_aware(today_end)
        yesterday_start = timezone.make_aware(yesterday_start)
        yesterday_end = timezone.make_aware(yesterday_end)

    stats = {}

    # Querysets
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

    # Orders
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

    # Revenue
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

    # Customers
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

    # Printed Pages
    today_pending = today_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
    today_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in today_pending
    )

    yesterday_pending = yesterday_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
    yesterday_pages = sum(
        (obj.NoOfPages or 0) * (obj.NumberOfCopies or 0) 
        for obj in yesterday_pending
    )

    all_pending = all_qs.filter(PrintStatus='Complete').only('NoOfPages', 'NumberOfCopies')
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

    # Cache for 5 minutes (auto-invalidates daily due to date in key)
    cache.set(cache_key, stats, 300)
    
    return stats


# ============================================
# CACHE INVALIDATION SIGNALS
# ============================================

@receiver([post_save, post_delete], sender=UploadFiles)
def invalidate_orders_cache(sender, instance, **kwargs):
    """
    Automatically invalidate cache when orders are created, updated, or deleted
    """
    if instance.Owner:
        invalidate_user_cache(instance.Owner.id)
        
        # Also invalidate dashboard stats for this unique_url
        if instance.Unique_url:
            today = timezone.now().date()
            cache_key = f"dashboard_stats_{instance.Unique_url}_{today}"
            cache.delete(cache_key)
            print(f"✅ Dashboard stats cache invalidated for {instance.Unique_url}")

