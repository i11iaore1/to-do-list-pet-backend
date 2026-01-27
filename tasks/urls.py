from django.urls import path

from .views import UserTaskSingleView, UserTaskPluralView, UserTaskClosureView, UserTaskReissueView


app_name = "tasks"
urlpatterns = [
    path("user-tasks/", UserTaskPluralView.as_view(), name="task-list"),
    path("user-tasks/<int:pk>/", UserTaskSingleView.as_view(), name="task-detail"),
    path("user-tasks/<int:pk>/close/", UserTaskClosureView.as_view(), name="task-close"),
    path("user-tasks/<int:pk>/reissue/", UserTaskReissueView.as_view(), name="task-reissue")
]
