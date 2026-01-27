from django.urls import path

from .views import GroupListView, GroupDetailView, MemberListView, MemberDetailView, GroupTaskListView


app_name = "groups"
urlpatterns = [
    path("groups/", GroupListView.as_view(), name="group-list"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("groups/<int:pk>/members/", MemberListView.as_view(), name="member-list"),
    path("members/<int:pk>/", MemberDetailView.as_view(), name="member-detail"),
    path("groups/<int:pk>/tasks/", GroupTaskListView.as_view(), name="task-list"), # GET POST, IsMemberOrAdmin (список задач конкретної групи, на які є дозвіл у користувача, створення групової задачі)
    # path("group-tasks/<int:pk>/", GroupTaskDetailView.as_view(), name="task-detail"), # GET PATCH DELETE, HasTaskPermissionOrAdmin (отримання, редагування, видалення конкретної групової таски)
    # path("group-tasks/<int:pk>/permissions/", GroupTaskPermissionListView.as_view(), name="task-permission-list"), # GET POST, IsTaskCreatorOrAdmin (список дозволів на конкретну задачу учасникам, створення нового дозволу)
    # path("group-task-permissions/<int:pk>", GroupTaskPermissionDetailView.as_view(), name="task-permission-detail") # GET, IsPermissionOwnerOrTaskCreatorOrAdmin (отримання конкретного дозволу)
    #                                                                                                                 # PATCH DELETE, IsTaskCreatorOrAdmin (редагування, видалення конкретного дозволу)
]
