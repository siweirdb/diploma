from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import RegisterView, LoginView, LogoutView, ProfileView, VerifyEmailView, ForgotPasswordView, VerifyResetCodeView, ResetPasswordView, QrCodeView, EditProfileView, ChangePasswordView, RegisterEmailView



urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('verify-email/<str:email>/', VerifyEmailView.as_view(), name='verify-email'),
    # path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    # path('verify-reset-code/', VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path("qr-code/<uuid:user_id>/", QrCodeView.as_view(), name="qr_code"),
    path('edit/', EditProfileView.as_view(), name='edit_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('register-email/', RegisterEmailView.as_view(), name='register_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
