# tracker/forms.py
from django import forms
from .models import Task, PRIORITY_CHOICES
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from datetime import date

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

class AITaskForm(forms.Form):
    """Form for creating tasks using AI from text prompts"""
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your task here...'}),
        label="Task Description",
        help_text="Describe the task in natural language. AI will extract the details."
    )
    
    # Optional fields that can override AI suggestions
    title = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Leave blank to use AI suggestion'})
    )
    
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'Use AI suggestion')] + PRIORITY_CHOICES,
        required=False
    )
    
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 5})
    )
    
    # For voice input
    audio_file = forms.FileField(
        required=False,
        help_text="Upload an audio file to transcribe instead of typing (optional)"
    )

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit)
        phone = self.cleaned_data.get('phone_number')
        if commit:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = phone
            profile.save()
        return user
