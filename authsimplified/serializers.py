from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "first_name", "last_name"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already in use."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(
        max_length=6,
        min_length=6,
        error_messages={
            "required": "Please enter the OTP.",
            "max_length": "OTP must be exactly 6 digits long.",
            "min_length": "OTP must be exactly 6 digits long.",
        },
    )

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return value
