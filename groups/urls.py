from django.urls import path

from .views import GroupListView, GroupDetailView, GroupTaskCloseView, GroupTaskDetailView, GroupTaskReissueView, MemberListView, MemberDetailView, GroupTaskListView, MemberTaskRelationListView, MemberTaskRelationDetailView


app_name = "groups"
urlpatterns = [
    path("groups/", GroupListView.as_view(is_admin_route=False), name="my-group-list"),
    path("users/<int:pk>/groups/", GroupListView.as_view(is_admin_route=True), name="other-group-list"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("groups/<int:pk>/members/", MemberListView.as_view(), name="member-list"),
    path("members/<int:pk>/", MemberDetailView.as_view(), name="member-detail"),
    path("groups/<int:pk>/tasks/", GroupTaskListView.as_view(), name="task-list"),
    path("group-tasks/<int:pk>/", GroupTaskDetailView.as_view(), name="task-detail"),
    path("group-tasks/<int:pk>/close/", GroupTaskCloseView.as_view(), name="task-close"),
    path("group-tasks/<int:pk>/reissue/", GroupTaskReissueView.as_view(), name="task-reissue"),
    path("group-tasks/<int:pk>/permissions/", MemberTaskRelationListView.as_view(), name="task-permission-list"),
    path("group-task-permissions/<int:pk>/", MemberTaskRelationDetailView.as_view(), name="task-permission-detail")
]
