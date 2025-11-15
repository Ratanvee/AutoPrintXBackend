import json
from channels.generic.websocket import WebsocketConsumer

class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'GeeksforGeeks'
        }))
    
    def disconnect(self, close_code):
        pass
    
    def receive(self, text_data):
        pass


# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta, datetime, time


# ============================================
# BASE CONSUMER CLASS
# ============================================

class BaseAuthenticatedConsumer(AsyncWebsocketConsumer):
    """Base consumer with authentication"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user or self.user.is_anonymous:
            await self.close()
            return
        
        await self.accept()
    
    async def disconnect(self, close_code):
        pass


# ============================================
# ORDERS OVERVIEW CONSUMER
# ============================================

class OrdersOverviewConsumer(BaseAuthenticatedConsumer):
    """WebSocket consumer for dashboard statistics overview"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and not self.user.is_anonymous:
            # Join user-specific room
            self.room_name = f"overview_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            
            # Send initial data
            await self.send_overview_data()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle refresh requests"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_overview_data()
            else:
                await self.send(text_data=json.dumps({
                    'error': f'Unknown action: {action}'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def send_overview_data(self):
        """Fetch and send overview data"""
        try:
            dashboard_stats = await self.get_dashboard_stats()
            
            await self.send(text_data=json.dumps({
                "OrderOverview": [{
                    "unique_url": self.user.unique_url,
                    "dashboard_stats": dashboard_stats
                }]
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Failed to fetch dashboard overview: {str(e)}'
            }))
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        from ownerside.utils import get_dashboard_stats, serialize_mongo_data
        dashboard_stats = get_dashboard_stats(self.user.unique_url)
        return serialize_mongo_data(dashboard_stats)
    
    # Handler for broadcast updates
    async def overview_update(self, event):
        """Receive broadcast update from channel layer"""
        await self.send_overview_data()


# ============================================
# DASHBOARD VIEW CONSUMER
# ============================================

class DashboardConsumer(BaseAuthenticatedConsumer):
    """WebSocket consumer for user dashboard data"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and not self.user.is_anonymous:
            await self.send_dashboard_data()
    
    async def receive(self, text_data):
        """Handle refresh requests"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_dashboard_data()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def send_dashboard_data(self):
        user_data = {
            "username": self.user.username,
            "email": self.user.email,
            "unique_url": self.user.unique_url,
            'is_modified': self.user.info_modified,
            'owner_name': self.user.owner_fullname,
        }
        
        await self.send(text_data=json.dumps({
            "message": "Welcome to your dashboard",
            "user": user_data
        }))


# ============================================
# RECENT ORDERS CONSUMER
# ============================================

class RecentOrdersConsumer(BaseAuthenticatedConsumer):
    """WebSocket consumer for recent orders with real-time updates"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and not self.user.is_anonymous:
            # Join user-specific room
            self.room_name = f"orders_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            
            # Send initial data
            await self.send_orders_data()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle refresh requests"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_orders_data()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def send_orders_data(self):
        """Fetch and send orders data"""
        try:
            orders = await self.get_recent_orders()
            
            await self.send(text_data=json.dumps({
                "orders": orders
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Failed to fetch orders: {str(e)}'
            }))
    
    @database_sync_to_async
    def get_recent_orders(self):
        from your_app.models import UploadFiles
        from your_app.utils import format_order
        
        all_orders = UploadFiles.objects.filter(
            Owner=self.user
        ).order_by('-Created_at')
        
        return [format_order(order) for order in all_orders]
    
    # Handler for broadcast updates
    async def orders_update(self, event):
        """Receive broadcast update from channel layer"""
        await self.send_orders_data()


# ============================================
# CHART DATA CONSUMER
# ============================================

class OrdersChartDataConsumer(BaseAuthenticatedConsumer):
    """WebSocket consumer for chart data"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and not self.user.is_anonymous:
            # Join user-specific room
            self.room_name = f"chart_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            
            # Send initial data (default: day)
            await self.send_chart_data('day')
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle filter change requests"""
        try:
            data = json.loads(text_data)
            filter_type = data.get('filter', 'day')
            
            await self.send_chart_data(filter_type)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def send_chart_data(self, filter_type='day'):
        """Generate and send chart data"""
        try:
            chart_data = await self.generate_chart_data(filter_type)
            
            await self.send(text_data=json.dumps(chart_data))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Failed to generate chart data: {str(e)}'
            }))
    
    @database_sync_to_async
    def generate_chart_data(self, filter_type):
        from your_app.models import UploadFiles
        from your_app.utils import convert_decimal128
        
        now_time = timezone.now()
        labels = []
        revenue_data = []
        orders_data = []
        
        qs = UploadFiles.objects.filter(Unique_url=self.user.unique_url)
        
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
        from your_app.utils import convert_decimal128
        
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
        from your_app.utils import convert_decimal128
        
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
        from your_app.utils import convert_decimal128
        
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
        from your_app.utils import convert_decimal128
        
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
    
    # Handler for broadcast updates
    async def chart_update(self, event):
        """Receive broadcast update from channel layer"""
        filter_type = event.get('filter', 'day')
        await self.send_chart_data(filter_type)


# ============================================
# RECENT ACTIVITY CONSUMER
# ============================================

class RecentActivityConsumer(BaseAuthenticatedConsumer):
    """WebSocket consumer for recent activities"""
    
    async def connect(self):
        await super().connect()
        
        if self.user and not self.user.is_anonymous:
            # Join user-specific room
            self.room_name = f"activity_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            
            # Send initial data
            await self.send_activities_data(4)
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle limit change requests"""
        try:
            data = json.loads(text_data)
            limit = min(int(data.get('limit', 4)), 20)
            
            await self.send_activities_data(limit)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    async def send_activities_data(self, limit=4):
        """Fetch and send activities data"""
        try:
            activities = await self.get_activities(limit)
            
            await self.send(text_data=json.dumps({
                "activities": activities
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
    
    @database_sync_to_async
    def get_activities(self, limit):
        from your_app.models import UploadFiles
        from your_app.utils import get_time_ago, convert_decimal128
        from django.utils.timezone import now
        
        activities = []
        activity_id = 1
        recent_time = now() - timedelta(hours=24)
        
        # New Orders
        new_orders = UploadFiles.objects.filter(
            Owner=self.user,
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
        
        # Payment Activities
        paid_orders = UploadFiles.objects.filter(
            Owner=self.user,
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
        
        # Completed Orders
        completed_orders = UploadFiles.objects.filter(
            Owner=self.user,
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
        
        # New Customers
        try:
            recent_customer_names = UploadFiles.objects.filter(
                Owner=self.user,
                Created_at__gte=recent_time
            ).values_list('CustomerName', flat=True).distinct()
            
            for customer_name in recent_customer_names:
                if not customer_name:
                    continue
                
                previous_orders = UploadFiles.objects.filter(
                    Owner=self.user,
                    CustomerName=customer_name,
                    Created_at__lt=recent_time
                ).exists()
                
                if not previous_orders:
                    first_order = UploadFiles.objects.filter(
                        Owner=self.user,
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
        
        # Sort and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    # Handler for broadcast updates
    async def activity_update(self, event):
        """Receive broadcast update from channel layer"""
        limit = event.get('limit', 4)
        await self.send_activities_data(limit)