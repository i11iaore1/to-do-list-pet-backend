from django.urls import path
from .views import (
    LogoutView,
    RefreshTokenView,
    RegisterView,
    LoginView,
    UserDetailView,
    UserMeView,
)


app_name = "users"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path(
        "refresh/",
        RefreshTokenView.as_view(),
        name="token-refresh",
    ),
    path("users/me/", UserMeView.as_view(), name="user-me"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
