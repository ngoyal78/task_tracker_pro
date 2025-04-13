from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, RoleViewSet
from .views import user_login, user_logout, dashboard, register, update_task_status, task_detail, task_edit,task_create,task_gallery_view  # Add the register view

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'roles', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# Authentication paths
urlpatterns += [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),  # Dashboard for logged-in users
    path('register/', register, name='register'),  # Registration for new users (optional)
    path('task/<int:task_id>/update-status/', update_task_status, name='update_task_status'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('task/<int:task_id>/edit/', task_edit, name='task_edit'),
    path('task/create/', task_create, name='task_create'),
    path('task-gallery/', task_gallery_view, name='task_gallery'),
]
