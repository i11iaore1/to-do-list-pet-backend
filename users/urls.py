from django.urls import path

from .views import RegisterView, LoginView, UserSingularView


app_name = "users"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("users/<int:pk>/", UserSingularView.as_view(), name="user-detail")
]
