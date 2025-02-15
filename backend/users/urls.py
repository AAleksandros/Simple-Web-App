from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, AdminUserListView, AdminUserDetailView, VerifyEmailView, ForgotPasswordView, ResetPasswordView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Admin Management
    path("admin/users/", AdminUserListView.as_view(), name="admin_users"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin_user_detail"),

    # Email Service
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]