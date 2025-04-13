from rest_framework import viewsets, permissions
from .models import Task, Category, Role
from .serializers import TaskSerializer, CategorySerializer, RoleSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .forms import TaskForm  # We will create a form for this

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            role = user.role.role_type
        except:
            role = None

        if role == 'Team Member':
            return Task.objects.filter(assigned_to=user)
        elif role == 'Team Leader':
            return Task.objects.filter(assigned_by=user)
        return super().get_queryset()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'tracker/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tracker/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Check if the user is an admin
    is_admin = request.user.is_superuser

    # Filter tasks based on user role
    if is_admin:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    context = {
        'tasks': tasks,
        'is_admin': is_admin,
#        'status_choices': Task.STATUS_CHOICES,  # Add this line
    }
    return render(request, 'tracker/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
@require_POST
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.assigned_to.all():
        new_status = request.POST.get('status')
        task.status = new_status
        task.save()
    return redirect('dashboard')

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user not in task.assigned_to.all():
        return redirect('dashboard')  # Or return an error if the user is not assigned
    return render(request, 'tracker/task_detail.html', {'task': task})

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    categories = Category.objects.all()
    users = User.objects.all()
    
    if request.user not in task.assigned_to.all():
        return redirect('dashboard')  # Or return an error if the user is not assigned

    can_edit_assignee = request.user == task.assigned_by or request.user.is_superuser

    if request.method == 'POST':
        # Handle form submission (Save the task data)
        task.title = request.POST['title']
        task.description = request.POST['description']
        task.category = Category.objects.get(id=request.POST['category'])
        task.priority = request.POST['priority']
        task.due_date = request.POST['due_date']
        task.status = request.POST['status']
        if can_edit_assignee:
            task.assigned_to.set(request.POST.getlist('assigned_to'))
#        task.assigned_to.set(request.POST.getlist('assigned_to'))
        task.comments = request.POST['comments']
        
        # Handle file upload
        if request.FILES.get('attachments'):
            task.attachments = request.FILES['attachments']
        
        task.save()
        return redirect('task_detail', task_id=task.id)
    
    else:
        form = TaskForm(instance=task)

    return render(request, 'tracker/task_edit.html', {
        'form': form,
        'task': task,
        'categories': categories,
        'users': users,
        'can_edit_assignee': can_edit_assignee,
    })

# views.py
@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'tracker/task_form.html', {'form': form})

@login_required
def task_gallery_view(request):
    tasks = Task.objects.all()
    selected_id = request.GET.get("selected")
    selected_task = None
    if selected_id:
        selected_task = Task.objects.filter(id=selected_id).first() if selected_id else None
#        selected_task = get_object_or_404(Task, id=selected_id)
    return render(request, 'tracker/task_gallery.html', {
        'tasks': tasks,
        'selected_task': selected_task
    })
