"""Authentication views: register, login, refresh, logout, verify email, reset password."""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.models import User
from apps.users.serializers import (
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

from .models import PasswordResetToken
from .serializers import MITTokenObtainPairSerializer
from .utils import send_password_reset_email, send_verification_email


# ----- Lightweight inline serializers used purely for OpenAPI docs ------------
class LogoutInputSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class DetailMessageSerializer(serializers.Serializer):
    detail = serializers.CharField()


class RegisterView(generics.CreateAPIView):
    """Public endpoint allowing students or teachers to self-register."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.email_verification_token = get_random_string(64)
        user.save(update_fields=['email_verification_token'])
        send_verification_email(user)

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role

        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Registration successful. Please verify your email.',
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = MITTokenObtainPairSerializer
    permission_classes = (AllowAny,)
    throttle_scope = 'login'


class RefreshTokenView(TokenRefreshView):
    permission_classes = (AllowAny,)


@extend_schema(
    request=LogoutInputSerializer,
    responses={200: DetailMessageSerializer, 400: DetailMessageSerializer},
)
class LogoutView(APIView):
    """Blacklists the supplied refresh token."""

    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutInputSerializer

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token required.'},
                                status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'})
        except Exception:
            return Response({'detail': 'Invalid refresh token.'},
                            status=status.HTTP_400_BAD_REQUEST)


@extend_schema(responses={200: DetailMessageSerializer, 400: DetailMessageSerializer})
class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = DetailMessageSerializer

    def get(self, request, token: str):
        user = User.objects.filter(email_verification_token=token).first()
        if not user:
            return Response({'detail': 'Invalid or expired verification token.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.is_email_verified = True
        user.email_verification_token = ''
        user.save(update_fields=['is_email_verified', 'email_verification_token'])
        return Response({'detail': 'Email verified successfully.'})


@extend_schema(
    request=ForgotPasswordSerializer,
    responses={200: DetailMessageSerializer},
)
class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1),
            )
            send_password_reset_email(user, str(token.token))
        return Response({'detail': 'If an account exists, a reset link has been sent.'})


@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: DetailMessageSerializer, 400: DetailMessageSerializer},
)
class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        token = PasswordResetToken.objects.filter(token=token_value).first()
        if not token or not token.is_valid:
            return Response({'detail': 'Invalid or expired token.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        user.set_password(new_password)
        user.save()
        token.is_used = True
        token.save(update_fields=['is_used'])
        return Response({'detail': 'Password has been reset successfully.'})
