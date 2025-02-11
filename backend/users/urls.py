from django.urls import path
from .views import RegisterView, protected_view, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # 🔥 Fix applied
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("protected/", protected_view, name="protected"),
]