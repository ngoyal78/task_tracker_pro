# tracker/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'category',
            'priority',
            'due_date',
            'status',
            'attachments',
            'comments',
            'assigned_to'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'assigned_to': forms.SelectMultiple(attrs={'size': 5}),
        }
