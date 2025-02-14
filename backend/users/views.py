from rest_framework_simplejwt.views import TokenObtainPairView
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

User = get_user_model()

### User Registration View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Password Validation
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

        user = User.objects.create_user(email=email, password=password)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

### Protected View for Testing Authentication
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "You are authenticated!", "user": request.user.email})

### Custom Login View (Includes User Data in Response)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        try:
            user = User.objects.get(email=request.data["email"])
            response.data["user"] = {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_staff": user.is_staff
            }
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response

### Admin Panel - Get All Users
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().values("id", "email", "is_active", "is_staff")
        return Response(users, status=status.HTTP_200_OK)

### Admin Panel - Get, Update, or Delete a Specific User
class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"id": user.id, "email": user.email, "is_active": user.is_active, "is_staff": user.is_staff})

    def put(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        is_active = request.data.get("is_active")
        is_staff = request.data.get("is_staff")

        try:
            if is_active is not None:
                user.is_active = bool(is_active)
            if is_staff is not None:
                user.is_staff = bool(is_staff)
            user.save()
            return Response({"message": "User updated successfully"})
        except ValueError:
            return Response({"error": "Invalid value for user update"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully"})

    def get_user(self, user_id):
        """Helper function to fetch user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None