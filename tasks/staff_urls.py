from django.urls import path

from .views import UserTaskListView


app_name = "staff-tasks"
urlpatterns = [
    path("users/<int:pk>/tasks/", UserTaskListView.as_view(), name="user-task-list")
]
