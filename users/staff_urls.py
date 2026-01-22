from django.urls import path

from .views import UserListView, AdminListView


app_name = "staff-users"
urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("admins/", AdminListView.as_view(), name="admin-list"),
]
