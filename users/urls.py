from django.urls import path
# from rest_framework.routers import DefaultRouter

from .views import RegisterView, LoginView

# router = DefaultRouter()
# router.register("/register")

urlpatterns = [
    path(r"register/", RegisterView.as_view()),
    path(r"login/", LoginView.as_view())
]
