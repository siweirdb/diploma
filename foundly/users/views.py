from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import VerificationCode, User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ForgotPasswordSerializer, \
    VerifyResetCodeSerializer, ResetPasswordSerializer, LogoutSerializer, QrCodeSerializer, EditProfileSerializer, \
    ChangePasswordSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from rest_framework import generics
import random

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class EditProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = EditProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        response = super().update(request, *args, **kwargs)
        return Response({
            'message': 'User information successfully updated',
            'user': response.data
        })


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "User password successfully updated"})


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email and password are required"}, status=400)

        print(email, password)

        user = authenticate(request, username=email, password=password)  # Authenticate with email

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=401)



EXPIRE_TIME = timedelta(minutes=10)

class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        # Check if email and code are provided
        if not email or not code:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get user associated with email
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already verified
        if user.is_active:
            return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)

        # Get verification code for user
        verification = VerificationCode.objects.filter(user=user, code=code).first()
        if not verification:
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the verification code has expired
        if verification.created_at < now() - EXPIRE_TIME:
            verification.delete()  # Cleanup expired code
            return Response({"error": "Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Activate user and delete verification code
        user.is_active = True
        user.save()
        verification.delete()

        return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)


class QrCodeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = QrCodeSerializer(user)
        return Response(serializer.data, status=200)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        email = request.data.get('email')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a random 6-digit reset code
        reset_code = str(random.randint(100000, 999999))

        # Store the reset code
        VerificationCode.objects.create(user=user, code=reset_code)

        # Send the reset code via email
        send_mail(
            "Password Reset Code - Foundly",
            f"Your password reset code is: {reset_code}",
            "foundly@yandex.kz",
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Reset code sent to email"}, status=status.HTTP_200_OK)

class VerifyResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyResetCodeSerializer

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()  # Now correctly placed
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        verification = VerificationCode.objects.filter(user=user, code=code).first()
        if not verification:
            return Response({"error": "Invalid or expired reset code"}, status=status.HTTP_400_BAD_REQUEST)

        if verification.created_at < now() - EXPIRE_TIME:
            verification.delete()
            return Response({"error": "Reset code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        verification.delete()

        return Response({"message": "Code verified successfully"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        user = User.objects.filter(email=email).first()

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)





