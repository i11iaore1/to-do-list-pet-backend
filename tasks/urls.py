from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, UserTaskSingleView, UserTaskPluralView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"my-tasks/", UserTaskPluralView.as_view()),
    path(r"my-tasks/<int:pk>/", UserTaskSingleView.as_view())
]
