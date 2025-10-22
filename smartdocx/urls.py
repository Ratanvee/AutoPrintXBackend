"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from smartdocx.views import home
# from .views import register, login_view, DashboardView, home
# from smartdocx.views import 
# from smartdocx.views import
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import get_notes, CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_logged_in, register
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import UploadFilesViewSet
from . import views
# router = DefaultRouter()
# router.register(r'uploads', UploadFilesViewSet, basename='uploads')
from ownerside.views import DashboardView, OrdersOverview, RecentOrdersView, OrdersChartData, UpdatePrintStatusAPIView, get_owner_orders
from customerside.views import upload_file_view
urlpatterns = [
    # path('', home, name='home'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('notes/', get_notes, name='get_notes'),
    path('logout/', logout, name='logout'),
    path('auth/', is_logged_in, name='is_authenticated'),
    path('register/', register, name='register'),
    path('dashboards/', DashboardView.as_view(), name='dashboard'),
    # path('dashboardf/', dashboard, name='dashboard-func'),
    path('upload/<slug:unique_url>/', upload_file_view, name='upload-file'),
    path("create-order/", views.create_order, name="create_order"),
    path("recent-orders/", RecentOrdersView.as_view(), name="recent_orders"),
    path('orders/', OrdersOverview.as_view(), name='orders_overview'),
    path('chart-data/', OrdersChartData.as_view(), name='orders_chart_data'),
    path("update-print-status/", UpdatePrintStatusAPIView.as_view(), name="update-print-status"),
    path('filter-orders/', get_owner_orders, name='filtered_orders'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
