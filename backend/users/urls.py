from django.urls import path
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    AdminUserListView,
    AdminUserDetailView,
    VerifyEmailView,
    ForgotPasswordView,
    ResetPasswordView,
    ResendVerificationEmailView,
    UserProfileView,
    ValidateResetTokenView,
    ChangeEmailView, 
    VerifyNewEmailView, 
    ChangePasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # Admin Management
    path("admin/users/", AdminUserListView.as_view(), name="admin_users"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin_user_detail"),

    # Email Service
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("resend-verification/", ResendVerificationEmailView.as_view(), name="resend_verification"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("validate-reset-token/", ValidateResetTokenView.as_view(), name="validate-reset-token"),
    path("change-email/", ChangeEmailView.as_view(), name="change-email"),
    path("verify-new-email/", VerifyNewEmailView.as_view(), name="verify-new-email"),

    # Protected Route (For Testing Authentication)
    path("protected/", CustomTokenObtainPairView.as_view(), name="protected"),
]