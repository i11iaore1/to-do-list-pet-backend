from django.urls import path

from .views import RegisterView, LoginView, UserDetailView
from rest_framework_simplejwt.views import TokenRefreshView


app_name = "users"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("refresh/", TokenRefreshView.as_view(), name='token-refresh'),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail")
]
