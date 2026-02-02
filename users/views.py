from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.pagination import NormalDataPagination
from .serializers import RegisterRequestSerializer, LoginRequestSerializer, UserProfileInfoSerializer
from .permissions import IsAccountOwnerOrAdmin


User = get_user_model()


class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = RegisterRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileInfoSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = LoginRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileInfoSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }
        )


class UserDetailView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAccountOwnerOrAdmin, )
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
    permission_classes = (IsAdminUser, )
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
    permission_classes = (IsAdminUser, )
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
