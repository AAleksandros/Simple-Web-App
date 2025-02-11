from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.db import models

class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email authentication."""
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

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

    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_staff = models.BooleanField(default=False, verbose_name="Staff Status")

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