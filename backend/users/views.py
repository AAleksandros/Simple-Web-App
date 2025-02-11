from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .serializers import CustomTokenObtainPairSerializer
import re

from .models import CustomUser

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

         # ✅ Use Django’s built-in email validator
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Password validation
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
            return Response({"error": "Password must contain at least one uppercase and one lowercase letter."}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"\d", password):
            return Response({"error": "Password must contain at least one number."}, status=status.HTTP_400_BAD_REQUEST)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return Response({"error": "Password must contain at least one special character."}, status=status.HTTP_400_BAD_REQUEST)
        if email.split("@")[0].lower() in password.lower():
            return Response({"error": "Password is too similar to the email."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(email=email, password=password)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """A protected view that requires authentication."""
    return Response({"message": "You are authenticated!", "user": request.user.email})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().values("id", "email", "is_active", "is_staff")
        return Response(users, status=status.HTTP_200_OK)

class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response({"id": user.id, "email": user.email, "is_active": user.is_active, "is_staff": user.is_staff})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = request.data.get("is_active", user.is_active)
            user.is_staff = request.data.get("is_staff", user.is_staff)
            user.save()
            return Response({"message": "User updated successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)