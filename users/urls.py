from django.urls import path

from .views import RegisterView, LoginView, UserSingularView


urlpatterns = [
    path(r"register/", RegisterView.as_view()),
    path(r"login/", LoginView.as_view()),
    path(r"users/<int:pk>/", UserSingularView.as_view())
]
