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

from .views import  CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_logged_in, register, ChangePasswordView
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import UploadFilesViewSet
from . import views
# router = DefaultRouter()
# router.register(r'uploads', UploadFilesViewSet, basename='uploads')
from ownerside.views import DashboardView, OrdersOverview, RecentActivityView, RecentOrdersView, OrdersChartData, UpdatePrintStatusAPIView, get_owner_orders, DashboardSettings
from customerside.views import upload_file_view
from .views import SendOTPView, VerifyOTPView, ResetPasswordView
urlpatterns = [
    # path('', home, name='home'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    # path('notes/', get_notes, name='get_notes'),
    path('logout/', logout, name='logout'),
    path('auth/', is_logged_in, name='is_authenticated'),
    path('register/', register, name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('dashboards/', DashboardView.as_view(), name='dashboard'),
    # path('dashboardf/', dashboard, name='dashboard-func'),
    path('upload/<slug:unique_url>/', upload_file_view, name='upload-file'),
    path("create-order/", views.create_order, name="create_order"),
    path("recent-orders/", RecentOrdersView.as_view(), name="recent_orders"),
    path('orders/', OrdersOverview.as_view(), name='orders_overview'),
    path('chart-data/', OrdersChartData.as_view(), name='orders_chart_data'),
    path("update-print-status/", UpdatePrintStatusAPIView.as_view(), name="update-print-status"),
    path('filter-orders/', get_owner_orders, name='filtered_orders'),
    path('download-db/', views.download_database, name='download_database'),
    path('recent-activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('dashboard-settings/', DashboardSettings, name='dashboard-settings'),
    # path('upload-imagekit/', upload_file_to_imagekit, name='upload-imagekit'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
