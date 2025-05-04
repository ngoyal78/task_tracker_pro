from django.contrib import admin
from django.utils.html import format_html
from .models import Task, Category, Role, Profile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'task_count')
    search_fields = ('name', 'description')
    
    def task_count(self, obj):
        count = obj.number_of_tasks()
        return format_html('<span style="color: {}">{}</span>', 
                          'green' if count > 0 else 'gray', 
                          count)
    task_count.short_description = 'Tasks'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'due_date', 'status', 'assigned_users', 'is_overdue_status')
    list_filter = ('status', 'priority', 'category', 'due_date')
    search_fields = ('title', 'description', 'comments')
    date_hierarchy = 'due_date'
    filter_horizontal = ('assigned_to',)
    readonly_fields = ('history_log',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'priority', 'status')
        }),
        ('Dates', {
            'fields': ('due_date',)
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_by', 'assigned_to')
        }),
        ('Additional Information', {
            'fields': ('comments', 'attachments', 'history_log'),
            'classes': ('collapse',)
        }),
    )
    
    def assigned_users(self, obj):
        return ", ".join([user.username for user in obj.assigned_to.all()])
    assigned_users.short_description = 'Assigned To'
    
    def is_overdue_status(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red;">Overdue</span>')
        return format_html('<span style="color: green;">On time</span>')
    is_overdue_status.short_description = 'Status'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_type')
    list_filter = ('role_type',)
    search_fields = ('user__username', 'user__email')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('user__is_active',)
