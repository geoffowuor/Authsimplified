from datetime import timedelta

import pyotp
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .utils import send_code_to_user
from .serializers import UserLoginSerializer, UserRegistrationSerializer, OTPSerializer

User = get_user_model()

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(request, user.email)
            return Response({"message": "User registered successfully. OTP sent."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    return Response({"error": "Incorrect password."}, status=status.HTTP_401_UNAUTHORIZED)
                if not user.is_active:
                    return Response({"error": "Account inactive. Verify email first."}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "message": "Login successful."
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "No refresh token found"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            OTP_INTERVAL = getattr(settings, "AUTHSIMPLIFIED_OTP_INTERVAL", 300)
            user_email = request.session.get("authsimplified_user_email")
            if not user_email:
                return Response({"error": "Session expired or not found. Start verification again."}, status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_404(User, email=user_email)

            if not user.otp_created_at:
                return Response({"error": "No OTP has been requested for this account."}, status=status.HTTP_400_BAD_REQUEST)

            otp_expiry_time = user.otp_created_at + timedelta(seconds=OTP_INTERVAL)
            if timezone.now() > otp_expiry_time:
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            otp_instance = pyotp.TOTP(user.secret_key, interval=OTP_INTERVAL)
            user_otp = serializer.validated_data["otp"]

            if otp_instance.verify(user_otp, valid_window=1):
                user.is_email_verified = True
                user.is_active = True
                user.save()
                try:
                    request.session.pop("authsimplified_user_email", None)
                except Exception:
                    pass
                return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(GenericAPIView):
    def post(self, request):
        user_email = request.session.get("authsimplified_user_email")
        if not user_email:
            return Response({"error": "Session expired. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            request.session.pop("authsimplified_user_email", None)
        except Exception:
            pass
        try:
            user = User.objects.get(email=user_email)
            send_code_to_user(request, user.email)
            return Response({"message": "A new OTP has been sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
