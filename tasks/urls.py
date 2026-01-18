from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import StaffUserTaskViewSet, UserTaskSingleView, UserTaskPluralView, UserTaskClosureView, UserTaskReissueView

router = DefaultRouter()
router.register(r"staff/user-tasks", StaffUserTaskViewSet)

urlpatterns = [
    path(r"user-tasks/", UserTaskPluralView.as_view()),
    path(r"user-tasks/<int:pk>/", UserTaskSingleView.as_view()),
    path(r"user-tasks/<int:pk>/close/", UserTaskClosureView.as_view()),
    path(r"user-tasks/<int:pk>/reissue/", UserTaskReissueView.as_view())
]

urlpatterns += router.urls
