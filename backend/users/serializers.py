from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
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
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Manually set the username field for JWT compatibility
        attrs["username"] = user.email  
        return super().validate(attrs)