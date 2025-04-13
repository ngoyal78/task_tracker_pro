from rest_framework import serializers
from .models import Task, Category, Role
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    number_of_tasks = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']