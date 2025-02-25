from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.utils.email_service import generate_verification_code
from .models import CustomUser

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        """Ensure passwords match and email is unique."""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})

        return data

    def create(self, validated_data):
        """Create user with a verification code and inactive status."""
        validated_data.pop("confirm_password")
        verification_code = generate_verification_code()

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.is_active = False
        user.verification_code = verification_code
        user.save()
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Use email instead of username for JWT authentication."""    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise serializers.ValidationError("Email not verified. Please check your inbox.")
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["username"] = user.email  
        return super().validate(attrs)
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone_number", "country", "city", "address"]