from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
import re
from django.utils import timezone
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


class RegisterEmailView(APIView):

    def post(self, request):
        is_register = request.data.get('is_register')
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        if is_register:
            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            VerificationCode.objects.filter(email=email).delete()

            try:
                verification_code = VerificationCode.objects.create(email=email)
                return Response({"message": "Verification code sent successfully", "pk": verification_code.pk},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

            reset_code = str(random.randint(100000, 999999))
            VerificationCode.objects.create(user=user, code=reset_code)

            try:
                send_mail(
                    "Password Reset Code - Foundly",
                    f"Your password reset code is: {reset_code}",
                    "foundly@yandex.kz",
                    [user.email],
                    fail_silently=False,
                )
                return Response({"message": "Reset code sent to email"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        verified_email = request.session.get('verified_email')

        if not verified_email:
            return Response({"error": "Email verification is required"}, status=status.HTTP_400_BAD_REQUEST)

        mutable_data = request.data.copy()
        mutable_data['email'] = verified_email
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            del request.session['verified_email']

            user_data = self.serializer_class(user).data

            return Response({"message": "User registered successfully", "user": user_data},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditProfileView(generics.RetrieveUpdateDestroyAPIView):
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

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({'message': 'User account successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


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

class VerifyResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyResetCodeSerializer

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
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


class VerifyEmailView(APIView):
    def post(self, request, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        code = request.data.get('code')

        if not code:
            return Response({"error": "Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_code = VerificationCode.objects.get(email=email)
        except VerificationCode.DoesNotExist:
            return Response({"error": "Invalid email or code has expired"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > verification_code.created_at + timedelta(minutes=10):
            verification_code.delete()
            return Response({"error": "Verification code expired"}, status=status.HTTP_400_BAD_REQUEST)

        if verification_code.code == code:
            request.session['verified_email'] = verification_code.email
            verification_code.delete()
            return Response({"message": "Verification successful"}, status=status.HTTP_200_OK)


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

        reset_code = str(random.randint(100000, 999999))

        VerificationCode.objects.create(user=user, code=reset_code)

        send_mail(
            "Password Reset Code - Foundly",
            f"Your password reset code is: {reset_code}",
            "foundly@yandex.kz",
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Reset code sent to email"}, status=status.HTTP_200_OK)




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





