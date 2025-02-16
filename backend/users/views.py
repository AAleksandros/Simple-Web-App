from users.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from users.utils.email_service import send_verification_email, send_password_reset_email, generate_verification_code
from django.utils.timezone import now
import random
import uuid
import re

User = get_user_model()

### User Registration with Email Verification
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not email or not password or not confirm_password:
            return Response({"error": "Email, password, and confirmation are required."}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

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

        # Generate verification code
        verification_code = generate_verification_code()

        # Create user but set as inactive until verified
        user = User.objects.create_user(email=email, password=password)
        user.is_active = False
        user.verification_code = verification_code
        user.verification_code_sent_at = now()
        user.save()

        # Send email
        send_verification_email(email, verification_code)

        return Response({"message": "User registered successfully. Check your email for the verification code."}, status=status.HTTP_201_CREATED)

### Verify Email
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        verification_code = request.data.get("code")

        try:
            user = User.objects.get(email=email)
            if user.verification_code == verification_code:
                user.is_active = True
                user.verification_code = None
                user.save()
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

### Resend Verification Code (Rate-limited to 60s)
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.can_request_verification_code():
                return Response({"error": "Please wait before requesting another verification code."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_sent_at = now()
            user.save()

            send_verification_email(email, verification_code)

            return Response({"message": "Verification email resent successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

### Forgot Password Request (Rate-limited to 5 min)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

            if not user.can_request_password_reset():
                return Response({"error": "Please wait before requesting another password reset."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            reset_token = str(uuid.uuid4())
            user.password_reset_token = reset_token
            user.password_reset_requested_at = now()
            user.save()

            send_password_reset_email(email, reset_token)

            return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "If this email exists, a reset link has been sent."}, status=status.HTTP_404_NOT_FOUND)

### Reset Password
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Validate required fields
        if not token or not new_password or not confirm_password:
            return Response({"error": "Token, new password, and confirmation are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure passwords match
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_404_NOT_FOUND)

        # Validate new password length
        if len(new_password) < 8:
            return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password and remove token
        user.set_password(new_password)
        user.password_reset_token = None
        user.save()

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

### User Login
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        try:
            user = User.objects.get(email=request.data["email"])
            if not user.is_active:
                return Response({"error": "Email not verified. Please check your email."}, status=status.HTTP_400_BAD_REQUEST)

            response.data["user"] = {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_staff": user.is_staff
            }
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return response

### Admin: Get All Users
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().values("id", "email", "is_active", "is_staff")
        return Response(users, status=status.HTTP_200_OK)

### Admin: Manage Users
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

        if is_active is not None:
            user.is_active = bool(is_active)
        if is_staff is not None:
            user.is_staff = bool(is_staff)
        user.save()

        return Response({"message": "User updated successfully"})

    def delete(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully"})

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None