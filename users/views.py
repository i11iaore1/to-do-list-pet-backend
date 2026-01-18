from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


User = get_user_model()


class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)

            },
            status=status.HTTP_200_OK
        )
