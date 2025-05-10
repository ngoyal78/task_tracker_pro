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
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the task in detail'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add any additional comments or notes'
            }),
            'assigned_to': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
        }

class AITaskForm(forms.Form):
    """Form for creating tasks using AI from text prompts"""
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4, 
            'placeholder': 'Describe your task here...'
        }),
        label="Task Description",
        help_text="Describe the task in natural language. AI will extract the details."
    )
    
    # Optional fields that can override AI suggestions
    title = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank to use AI suggestion'
        })
    )
    
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Leave blank to use AI suggestion'
        }),
        initial=lambda: date.today() + forms.fields.datetime.timedelta(days=1),  # Set initial value to tomorrow
        help_text="Optional: Leave blank to use AI-suggested due date based on task description"
    )
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today() + forms.fields.datetime.timedelta(days=1):
            tomorrow = date.today() + forms.fields.datetime.timedelta(days=1)
            raise forms.ValidationError(f"Value must be {tomorrow.strftime('%m/%d/%Y')} or later.")
        return due_date
    
    priority = forms.ChoiceField(
        choices=[('', 'Use AI suggestion')] + PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5
        })
    )
    
    # For voice input
    audio_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }),
        help_text="Upload an audio file to transcribe instead of typing (optional)"
    )

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number (optional)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to the password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit)
        phone = self.cleaned_data.get('phone_number')
        if commit:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = phone
            profile.save()
        return user
