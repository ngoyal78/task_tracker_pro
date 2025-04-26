# tracker/forms.py
from django import forms
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

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
