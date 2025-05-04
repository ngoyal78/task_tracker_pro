from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Task category for organizing tasks by type or department.
    
    Categories help organize tasks into logical groups for better management
    and filtering.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def number_of_tasks(self):
        """Return the count of tasks in this category"""
        return self.task_set.count()

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
STATUS_CHOICES = [
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Submitted for Approval', 'Submitted for Approval'),
    ('Approved', 'Approved'),
    ('Reassigned', 'Reassigned')
]

class Task(models.Model):
    """
    Core task model representing a work item to be completed.
    
    Tasks are the central entity in the system, containing all information
    about work items, their status, assignments, and history.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        help_text="The category this task belongs to"
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES,
        help_text="Task priority level"
    )
    due_date = models.DateField(help_text="Date when this task should be completed")
    status = models.CharField(
        max_length=25, 
        choices=STATUS_CHOICES,
        help_text="Current status of the task"
    )
    attachments = models.FileField(
        upload_to='attachments/', 
        blank=True, 
        null=True,
        help_text="Files related to this task"
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional notes or comments about the task"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_tasks',
        help_text="User who created this task"
    )
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_tasks',
        help_text="User who assigned this task"
    )
    assigned_to = models.ManyToManyField(
        User, 
        related_name='tasks',
        help_text="Users responsible for completing this task"
    )
    history_log = models.TextField(
        blank=True,
        help_text="Chronological record of changes to this task"
    )

    def __str__(self):
        return self.title
        
    def is_overdue(self):
        """Check if the task is past its due date"""
        from datetime import date
        return self.due_date < date.today()
        
    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-due_date', 'priority']

ROLE_CHOICES = [
    ('Owner', 'Owner'),
    ('Team Leader', 'Team Leader'),
    ('Team Member', 'Team Member')
]

class Role(models.Model):
    """
    User role for permission management.
    
    Defines the role of a user in the system, which determines their
    permissions and access levels.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="The user this role is assigned to"
    )
    role_type = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        help_text="Type of role determining user permissions"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role_type}"
        
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('tracker')

class Profile(models.Model):
    """
    Extended user profile with additional information.
    
    Stores user-specific data that is not part of the default User model,
    such as phone number for notifications.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=21, 
        blank=True, 
        help_text="Phone number for WhatsApp notifications (include country code, e.g., +1234567890)"
    )
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create or update a Profile when a User is saved.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
    """
    try:
        if created:
            Profile.objects.create(user=instance)
            logger.info(f"Profile created for user: {instance.username}")
        else:
            # Only save the profile if it exists
            if hasattr(instance, 'profile'):
                instance.profile.save()
                logger.info(f"Profile updated for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error in profile signal handler for {instance.username}: {str(e)}")
