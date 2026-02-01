from django.urls import path

from .views import UserTaskListView, UserTaskDetailView, UserTaskClosureView, UserTaskReissueView


app_name = "tasks"
urlpatterns = [
    path("user-tasks/", UserTaskListView.as_view(is_admin_route=False), name="my-task-list"),
    path("users/<int:pk>/tasks/", UserTaskListView.as_view(is_admin_route=True), name="other-task-list"),
    path("user-tasks/<int:pk>/", UserTaskDetailView.as_view(), name="task-detail"),
    path("user-tasks/<int:pk>/close/", UserTaskClosureView.as_view(), name="task-close"),
    path("user-tasks/<int:pk>/reissue/", UserTaskReissueView.as_view(), name="task-reissue")
]
