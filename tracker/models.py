from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def number_of_tasks(self):
        return self.task_set.count()

    def __str__(self):
        return self.name

PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
STATUS_CHOICES = [
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Submitted for Approval', 'Submitted for Approval'),
    ('Approved', 'Approved'),
    ('Reassigned', 'Reassigned')
]

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    due_date = models.DateField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES)
    attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
    comments = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    assigned_to = models.ManyToManyField(User, related_name='tasks')
    history_log = models.TextField(blank=True)

    def __str__(self):
        return self.title

ROLE_CHOICES = [
    ('Owner', 'Owner'),
    ('Team Leader', 'Team Leader'),
    ('Team Member', 'Team Member')
]

class Role(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role_type}"
