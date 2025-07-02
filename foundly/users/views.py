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

from django.shortcuts import get_object_or_404, render

from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from rest_framework import generics
import random


class AllUsersView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)


class RegisterEmailView(APIView):

    def post(self, request):
        is_register = request.data.get('is_register')
        email = request.data.get('email')

        if not email:
            return Response({"error": "Почта обязательна"}, status=status.HTTP_400_BAD_REQUEST)

        if is_register:
            if User.objects.filter(email=email).exists():
                return Response({"error": "Такая почта уже существует"}, status=status.HTTP_400_BAD_REQUEST)

            # Delete any previous code
            VerificationCode.objects.filter(email=email).delete()

            # Create and save new code
            code = str(random.randint(100000, 999999))
            verification_code = VerificationCode.objects.create(email=email, code=code)

            # Send registration email
            try:
                send_mail(
                    'Email Verification - Foundly',
                    f"Добро пожаловать в Foundly!\n\n"
                    f"Ваш код подтверждения: {code}\n\n"
                    "Введите его в приложении в течение 5 минут, чтобы продолжить.\n\n"
                    "Если вы не запрашивали этот код, просто проигнорируйте сообщение.",
                    'foundly@yandex.kz',
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Verification code sent successfully", "pk": verification_code.pk},
                                status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "Пользователь с этим адресом электронной почты не существует."},
                                status=status.HTTP_404_NOT_FOUND)

            reset_code = str(random.randint(100000, 999999))
            VerificationCode.objects.update_or_create(email=email, defaults={"code": reset_code})

            # Send forgot password email
            try:
                send_mail(
                    "Password Reset Code - Foundly",
                    f"Вы запросили сброс пароля.\n\n"
                    f"Код для сброса: {reset_code}\n\n"
                    "Введите его в приложении, чтобы создать новый пароль.\n\n"
                    "Если вы не запрашивали сброс, просто проигнорируйте это сообщение.",
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
            return Response({"error": "Сначала подтвердите почту"}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"detail": "Почта и пароль обязательны"}, status=400)

        print(email, password)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"detail": "Неверные учетные данные"}, status=401)



EXPIRE_TIME = timedelta(minutes=10)

class VerifyResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyResetCodeSerializer

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Почта и код обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        verification = VerificationCode.objects.filter(user=user, code=code).first()
        if not verification:
            return Response({"error": "Неверный или просроченный код"}, status=status.HTTP_400_BAD_REQUEST)

        if verification.created_at < now() - EXPIRE_TIME:
            verification.delete()
            return Response({"error": "Просроченный код"}, status=status.HTTP_400_BAD_REQUEST)

        verification.delete()

        return Response({"message": "Код успешно подтвержден"}, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    def post(self, request, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return Response({"error": "Неверный формат почты"}, status=status.HTTP_400_BAD_REQUEST)
        code = request.data.get('code')

        if not code:
            return Response({"error": "Код обязательен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_code = VerificationCode.objects.get(email=email)
        except VerificationCode.DoesNotExist:
            return Response({"error": "Неверный код или почта"}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > verification_code.created_at + timedelta(minutes=10):
            verification_code.delete()
            return Response({"error": "Код подтверждения просрочен"}, status=status.HTTP_400_BAD_REQUEST)

        if verification_code.code == code:
            request.session['verified_email'] = verification_code.email
            verification_code.delete()
            return Response({"message": "Подтверждение прошло успешно"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)

def landing_page(request):
    return render(request, "page.html")

class QrCodeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

        if 'iphone' in user_agent or 'android' in user_agent:
            if 'safari' in user_agent or 'chrome' in user_agent or 'firefox' in user_agent:
                return render(request, 'file.html', {'user': user})

        serializer = QrCodeSerializer(user)
        return Response(serializer.data, status=200)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        email = request.data.get('email')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Пользователь с этим адресом электронной почты не существует."}, status=status.HTTP_404_NOT_FOUND)

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





