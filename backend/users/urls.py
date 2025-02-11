from django.urls import path
from .views import RegisterView, protected_view, CustomTokenObtainPairView, AdminUserListView, AdminUserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("protected/", protected_view, name="protected"),
    
    # Admin Management
    path("admin/users/", AdminUserListView.as_view(), name="admin_users"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
]