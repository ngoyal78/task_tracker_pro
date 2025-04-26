from django.contrib import admin
from .models import Task, Category, Role
from .models import Profile

admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Role)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Profile, ProfileAdmin)
