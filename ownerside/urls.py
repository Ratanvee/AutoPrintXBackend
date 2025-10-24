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


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardView, OrdersOverview, RecentOrdersView, OrdersChartData, UpdatePrintStatusAPIView
# router = DefaultRouter()
# router.register(r'uploads', UploadFilesViewSet, basename='uploads')

urlpatterns = [
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("api/update-print-status/", UpdatePrintStatusAPIView.as_view(), name="update-print-status"),
    # path('dashboard-func/', dashboard, name='dashboard-func'),
    # path('orders/', OrdersOverview.as_view(), name='orders_overview'),
    # path('recent-orders/', RecentOrdersView.as_view(), name='recent_orders'),
    # path('api/uploads/<slug:unique_url>/', upload_file_view, name='upload-file'),


]
