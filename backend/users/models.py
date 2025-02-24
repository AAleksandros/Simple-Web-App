from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.db import models
import uuid
from datetime import datetime, timedelta
from django.utils.timezone import now

class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email authentication."""
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)  # Default to inactive until email verified

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Superusers always active

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email instead of username for authentication."""

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address.")],
        verbose_name="Email Address"
    )

    password = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(8, message="Password must be at least 8 characters long."),
            RegexValidator(r".*[A-Z].*", message="Password must contain at least one uppercase letter."),
            RegexValidator(r".*[a-z].*", message="Password must contain at least one lowercase letter."),
            RegexValidator(r".*\d.*", message="Password must contain at least one number."),
            RegexValidator(r".*[!@#$%^&*(),.?\":{}|<>].*", message="Password must contain at least one special character."),
        ],
        verbose_name="Password"
    )

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=False, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Staff Status")

    # Email Verification Code
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_sent_at = models.DateTimeField(null=True, blank=True)

    # Password Reset Token
    password_reset_token = models.UUIDField(default=None, null=True, blank=True, unique=True)
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def can_request_verification_code(self):
        """Check if the user can request a new verification code (rate limit: every 60 seconds)."""
        if self.verification_code_sent_at and (now() - self.verification_code_sent_at < timedelta(seconds=60)):
            return False
        return True

    def can_request_password_reset(self):
        """Check if the user can request a password reset (rate limit: every 5 minutes)."""
        if self.password_reset_requested_at and (now() - self.password_reset_requested_at < timedelta(minutes=5)):
            return False
        return True
    
    def is_reset_token_valid(self):
        """Check if the reset token is still valid (1-hour expiration)."""
        if not self.password_reset_token or not self.password_reset_requested_at:
            return False
        return now() - self.password_reset_requested_at < timedelta(hours=1)
    
    def is_reset_token_valid(self):
        """Check if the reset token is still valid (1-hour expiration)."""
        if not self.password_reset_token or not self.password_reset_requested_at:
            return False
        return now() - self.password_reset_requested_at < timedelta(hours=1)

class UsedPasswordResetToken(models.Model):
    token = models.UUIDField(unique=True)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)