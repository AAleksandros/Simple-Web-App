from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser

User = get_user_model()

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
            # Checked after the password so the message can't be used to probe
            # which accounts are disabled.
            if not user.is_active:
                raise serializers.ValidationError("This account has been disabled.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["username"] = user.email  
        return super().validate(attrs)
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone_number", "country", "city", "address"]