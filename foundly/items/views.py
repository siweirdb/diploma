from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer
from django.shortcuts import redirect
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = User.objects.get(username=request.data["username"])
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]

            # Store tokens in cookies
            redirect_response = redirect(f"/profile/{user.id}/")
            redirect_response.set_cookie("access_token", access_token, httponly=True)
            redirect_response.set_cookie("refresh_token", refresh_token, httponly=True)

            return redirect_response

        return response


class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def get(self, request, id):
        # Extract token from Authorization header OR cookies
        auth = get_authorization_header(request).split()
        if not auth and "access_token" in request.COOKIES:
            request.META["HTTP_AUTHORIZATION"] = f'Bearer {request.COOKIES["access_token"]}'

        # Check if authentication is successful
        # if not request.user.is_authenticated:
        #     return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch user profile
        try:
            user = User.objects.get(id=id)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)