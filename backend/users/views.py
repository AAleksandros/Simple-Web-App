from users.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import status
from .models import CustomUser, UsedPasswordResetToken
from .serializers import UserProfileSerializer
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from users.utils.email_service import send_verification_email, send_password_reset_email, generate_verification_code
from django.utils.timezone import now, timedelta
from datetime import timedelta
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

        user = User.objects.filter(email=email).first()

        EMAIL_VERIFICATION_COOLDOWN = timedelta(seconds=60)

        if user and not user.is_active:
            last_sent = user.verification_code_sent_at
            if last_sent and now() - last_sent < EMAIL_VERIFICATION_COOLDOWN:
                return Response(
                    {"error": "User already exists but is not verified. Please wait before requesting another verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If cooldown has passed, generate and send a new code
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_sent_at = now()
            user.save()

            send_verification_email(email, verification_code)

            return Response(
                {"error": "User already exists but is not verified. A new verification code has been sent to your email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user:
            return Response({"error": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = generate_verification_code()
        user = User.objects.create_user(email=email, password=password)
        user.is_active = False
        user.verification_code = verification_code
        user.verification_code_sent_at = now()
        user.save()

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

### Resend Verification Code
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'resend_verification'

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({"message": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.can_request_verification_code():
                return Response({"error": "Please wait before requesting another verification code."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Generate and send the new code
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_sent_at = now()
            user.save()

            send_verification_email(email, verification_code)

            return Response({"message": "Verification email resent successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

### Forgot Password Request
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'forgot_password'

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            if not user.can_request_password_reset():
                return Response(
                    {"error": "Please wait before requesting another password reset."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Invalidate the old reset token by generating a new one
            user.password_reset_token = uuid.uuid4()  
            user.password_reset_requested_at = now()
            user.save()

            send_password_reset_email(email, str(user.password_reset_token)) 

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

        if not token or not new_password or not confirm_password:
            return Response({"error": "Token, new password, and confirmation are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if token has already been used (blacklist check)
            if UsedPasswordResetToken.objects.filter(token=token).exists():
                return Response({"error": "This reset link has already been used."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(password_reset_token=token)

            if not user.is_reset_token_valid():
                return Response({"error": "This password reset link has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)

            UsedPasswordResetToken.objects.create(token=token)

            user.password_reset_token = None
            user.password_reset_requested_at = None
            user.save()

            return Response({"message": "Password reset successfully. You can now log in."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_404_NOT_FOUND)
        
### Validate Password Reset Token Before Showing Form
class ValidateResetTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        try:
            user = User.objects.get(password_reset_token=token)

            if not user.is_reset_token_valid():
                return Response({"error": "This password reset link has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_404_NOT_FOUND)

### User Login
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is not active
        if not user.is_active:
            EMAIL_VERIFICATION_COOLDOWN = timedelta(seconds=60)
            last_sent = user.verification_code_sent_at

            if last_sent and now() - last_sent < EMAIL_VERIFICATION_COOLDOWN:
                return Response(
                    {"error": "Email not verified. Please check your email."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_sent_at = now()
            user.save()

            send_verification_email(email, verification_code)

            return Response(
                {"error": "Email not verified. A new verification code has been sent."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If user is verified, proceed with normal login
        response = super().post(request, *args, **kwargs)

        response.data["user"] = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_staff": user.is_staff
        }

        return response

### User profile    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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