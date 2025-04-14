from django.contrib import admin
from django.urls import path, include
from tracker.views import redirect_to_login  # <- import the redirect view

urlpatterns = [
    path('', redirect_to_login),  # <- root URL redirect
    path('admin/', admin.site.urls),
    path('api/', include('tracker.urls')),  # <- this line is critical
]
