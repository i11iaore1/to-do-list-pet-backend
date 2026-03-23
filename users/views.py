from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse_lazy
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from core.pagination import NormalDataPagination
from .serializers import (
    RegisterRequestSerializer,
    LoginRequestSerializer,
    UserProfileInfoSerializer,
)
from .permissions import IsAccountOwnerOrAdmin


User = get_user_model()


refresh_cookie_config = settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE"]
REFRESH_COOKIE_SETTINGS = {
    "httponly": refresh_cookie_config["HTTP_ONLY"],
    "secure": refresh_cookie_config["SECURE"],
    "samesite": refresh_cookie_config["SAMESITE"],
    "path": reverse_lazy(refresh_cookie_config["PATH_NAME"]),
}


def set_refresh_token_cookie(response: Response, token_value: str) -> None:
    response.set_cookie(
        # key is a positional arg
        key=refresh_cookie_config["KEY"],
        value=token_value,
        **REFRESH_COOKIE_SETTINGS
    )


class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "user": UserProfileInfoSerializer(user).data,
                "access_token": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )
        set_refresh_token_cookie(response=response, token_value=str(refresh))

        return response


class LoginView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = LoginRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "user": UserProfileInfoSerializer(user).data,
                "access_token": str(refresh.access_token),
            }
        )
        set_refresh_token_cookie(response=response, token_value=str(refresh))

        return response


class RefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(refresh_cookie_config["KEY"])

        if refresh:
            # add refresh to data for standart SimpleJWT serializer
            request_data = request.data.copy()
            request_data["refresh"] = refresh
            request._full_data = request_data

        # call the standart refresh logic
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and "refresh" in response.data:
            # retreive access and refresh and replace response.data
            access = response.data.get("access")
            refresh = response.data.get("refresh")

            response.data = {"access_token": access}

            set_refresh_token_cookie(response=response, token_value=refresh)

        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Successfully logged out"}, status=200)
        response.delete_cookie(
            key=refresh_cookie_config["KEY"], path=REFRESH_COOKIE_SETTINGS["path"]
        )
        return response


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAccountOwnerOrAdmin,)
    serializer_class = UserProfileInfoSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserProfileInfoSerializer
    pagination_class = NormalDataPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AdminListView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserProfileInfoSerializer
    pagination_class = NormalDataPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=True)

        return queryset
