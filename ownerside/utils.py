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


# def get_last_modified_timestamp(user):
#     """Get the last modified timestamp for user's orders"""
#     try:
#         last_order = UploadFiles.objects.filter(
#             Owner=user
#         ).order_by('-Updated_at').first()
        
#         if last_order and last_order.Updated_at:
#             return last_order.Updated_at.isoformat()
#     except Exception as e:
#         print(f"Error getting last modified: {e}")
    
#     return timezone.now().isoformat()

def get_last_modified_timestamp(user):
    """Get last modified timestamp for user"""
    cache_key = f'last_modified_{user.id}'
    timestamp = cache.get(cache_key)
    
    if not timestamp:
        # Initialize with current time if not exists
        timestamp = timezone.now().isoformat()
        cache.set(cache_key, timestamp, None)
    
    return timestamp


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

