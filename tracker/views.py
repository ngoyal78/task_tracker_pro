import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from datetime import date, datetime, timedelta

from .models import Task, Category, Role
from .serializers import TaskSerializer, CategorySerializer, RoleSerializer, UserSerializer
from .forms import TaskForm, CustomUserCreationForm, AITaskForm
from .utils import send_whatsapp_message, generate_task_from_prompt, transcribe_audio

# Set up logger
logger = logging.getLogger('tracker')

class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tasks.
    
    Provides CRUD operations for tasks with role-based access control.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter tasks based on user role:
        - Team Members see only tasks assigned to them
        - Team Leaders see tasks they've assigned
        - Admins and Owners see all tasks
        """
        user = self.request.user
        
        try:
            role = user.role.role_type
        except (Role.DoesNotExist, AttributeError):
            role = None
            
        # Apply role-based filtering
        if role == 'Team Member':
            return Task.objects.filter(assigned_to=user)
        elif role == 'Team Leader':
            return Task.objects.filter(assigned_by=user)
        
        # Admins and Owners see all tasks
        return super().get_queryset()
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user when creating a task"""
        serializer.save(created_by=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for managing task categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class RoleViewSet(viewsets.ModelViewSet):
    """API endpoint for managing user roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]

def user_login(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'tracker/login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            
            # Redirect to the page the user was trying to access, or dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Invalid credentials')
            
    return render(request, 'tracker/login.html')

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('/api/login/')

def user_logout(request):
    """Handle user logout"""
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out")
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

@login_required
def dashboard(request):
    """
    Display the user dashboard with their assigned tasks.
    
    Shows all tasks for admins, and only assigned tasks for regular users.
    """
    # Get user role information
    is_admin = request.user.is_superuser
    
    try:
        user_role = request.user.role.role_type
    except (Role.DoesNotExist, AttributeError):
        user_role = None
    
    # Filter tasks based on user role
    if is_admin or user_role == 'Owner':
        tasks = Task.objects.all()
    elif user_role == 'Team Leader':
        tasks = Task.objects.filter(assigned_by=request.user)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)
    
    # Mark overdue tasks
    today = date.today()
    for task in tasks:
        task.is_overdue = task.due_date < today
    
    # Calculate task statistics in the view for better performance
    in_progress_count = tasks.filter(status='In Progress').count()
    completed_count = tasks.filter(status='Approved').count()
    overdue_count = sum(1 for task in tasks if task.due_date < today)
    
    context = {
        'tasks': tasks,
        'is_admin': is_admin,
        'user_role': user_role,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'overdue_count': overdue_count,
        'total_count': tasks.count(),
    }
    
    return render(request, 'tracker/dashboard.html', context)

def register(request):
    """
    Handle user registration with custom form that includes phone number.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"New user registered: {user.username}")
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            logger.warning(f"Registration failed: {form.errors}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'tracker/register.html', {'form': form})

def notify_assigned_users_on_status_change(task, old_status, new_status):
    """
    Send WhatsApp notifications to all assigned users when a task status changes.
    
    Args:
        task: The Task object that was updated
        old_status: Previous status value
        new_status: New status value
    """
    if old_status == new_status:
        return  # No change, no notification needed
        
    # Update task history log
    timestamp = date.today().strftime("%Y-%m-%d")
    history_entry = f"{timestamp}: Status changed from '{old_status}' to '{new_status}'\n"
    
    if task.history_log:
        task.history_log += history_entry
    else:
        task.history_log = history_entry
    
    task.save(update_fields=['history_log'])
    
    # Send notifications to all assigned users
    for user in task.assigned_to.all():
        try:
            profile = getattr(user, 'profile', None)
            if profile and profile.phone_number:
                message = f"Hi {user.username}, the task '{task.title}' status changed from {old_status} to {new_status}."
                logger.debug(f"Notifying {user.username} on status change: {old_status} → {new_status}")
                result = send_whatsapp_message(profile.phone_number, message)
                
                if result:
                    logger.info(f"WhatsApp notification sent to {user.username} ({profile.phone_number})")
                else:
                    logger.warning(f"Failed to send WhatsApp notification to {user.username}")
        except Exception as e:
            logger.error(f"Error notifying user {user.username}: {str(e)}")

@login_required
@require_POST
def update_task_status(request, task_id):
    """
    Update a task's status and notify assigned users of the change.
    
    Only users assigned to the task can update its status.
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user is authorized to update this task
    if request.user not in task.assigned_to.all() and not request.user.is_superuser:
        logger.warning(f"Unauthorized status update attempt by {request.user.username} for task {task_id}")
        messages.error(request, "You don't have permission to update this task's status")
        return redirect('dashboard')
    
    old_status = task.status
    new_status = request.POST.get('status')
    
    if not new_status:
        messages.error(request, "Status cannot be empty")
        return redirect('dashboard')
    
    # Update the task status
    task.status = new_status
    task.save()
    
    logger.info(f"Task {task_id} status updated from '{old_status}' to '{new_status}' by {request.user.username}")
    
    # Notify assigned users about the status change
    notify_assigned_users_on_status_change(task, old_status, new_status)
    
    messages.success(request, f"Task status updated to '{new_status}'")
    return redirect('dashboard')

@login_required
def task_detail(request, task_id):
    """
    Display detailed information about a specific task.
    
    Users can only view tasks they are assigned to, unless they are admins.
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user is authorized to view this task
    if (request.user not in task.assigned_to.all() and 
        request.user != task.assigned_by and 
        not request.user.is_superuser):
        
        logger.warning(f"Unauthorized task detail access attempt by {request.user.username} for task {task_id}")
        messages.error(request, "You don't have permission to view this task")
        return redirect('dashboard')
    
    return render(request, 'tracker/task_detail.html', {'task': task})

@login_required
def task_edit(request, task_id):
    """
    Edit a task with role-based permissions:
    - All assigned users can update status and comments
    - Only task creator, team leaders, and admins can edit other fields
    """
    task = get_object_or_404(Task, id=task_id)
    
    # Get current user and their role
    user = request.user
    try:
        user_role = user.role.role_type
    except (Role.DoesNotExist, AttributeError):
        user_role = None
    
    # Check if user is authorized to edit this task
    if user not in task.assigned_to.all() and user != task.assigned_by and not user.is_superuser:
        logger.warning(f"Unauthorized task edit attempt by {user.username} for task {task_id}")
        messages.error(request, "You don't have permission to edit this task")
        return redirect('dashboard')
    
    # Determine user permissions
    can_edit_assignee = user == task.assigned_by or user.is_superuser
    is_owner_or_leader = user_role in ['Owner', 'Team Leader'] or user.is_superuser
    
    # Get data for form
    categories = Category.objects.all()
    users = User.objects.all()
    old_status = task.status
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # All users can update status and comments
                new_status = request.POST.get('status')
                if new_status:
                    task.status = new_status
                
                task.comments = request.POST.get('comments', '')
                
                # Only owners/leaders can edit core task details
                if is_owner_or_leader:
                    task.title = request.POST.get('title', task.title)
                    task.description = request.POST.get('description', task.description)
                    
                    category_id = request.POST.get('category')
                    if category_id:
                        task.category = Category.objects.get(id=category_id)
                    
                    task.priority = request.POST.get('priority', task.priority)
                    task.due_date = request.POST.get('due_date', task.due_date)
                
                # Only task creator or admin can reassign
                if can_edit_assignee:
                    assigned_to_ids = request.POST.getlist('assigned_to')
                    if assigned_to_ids:
                        task.assigned_to.set(assigned_to_ids)
                
                # Handle file upload
                if request.FILES.get('attachments'):
                    task.attachments = request.FILES['attachments']
                
                task.save()
                
                # Notify about status changes
                if old_status != task.status:
                    notify_assigned_users_on_status_change(task, old_status, task.status)
                
                logger.info(f"Task {task_id} updated by {user.username}")
                messages.success(request, "Task updated successfully")
                return redirect('task_detail', task_id=task.id)
                
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            messages.error(request, f"Error updating task: {str(e)}")
    
    # Prepare form for GET request
    form = TaskForm(instance=task)
    
    return render(request, 'tracker/task_edit.html', {
        'form': form,
        'task': task,
        'categories': categories,
        'users': users,
        'can_edit_assignee': can_edit_assignee,
        'is_owner_or_leader': is_owner_or_leader,
    })

""" @login_required
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
 """
@login_required
def task_create(request):
    """
    Create a new task.
    
    Sets the current user as both created_by and assigned_by.
    """
    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    task = form.save(commit=False)
                    task.created_by = request.user
                    task.assigned_by = request.user
                    task.save()
                    form.save_m2m()  # Save the many-to-many field `assigned_to`
                    
                    logger.info(f"New task created: '{task.title}' by {request.user.username}")
                    messages.success(request, "Task created successfully")
                    return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error creating task: {str(e)}")
                messages.error(request, f"Error creating task: {str(e)}")
        else:
            logger.warning(f"Invalid task form: {form.errors}")
    else:
        form = TaskForm()
        
    return render(request, 'tracker/task_form.html', {'form': form})

@login_required
def task_gallery_view(request):
    """
    Display tasks in a gallery view with details panel.
    
    Shows all tasks for admins, and only relevant tasks for other users based on role.
    """
    user = request.user
    
    # Filter tasks based on user role
    if user.is_superuser:
        tasks = Task.objects.all()
    else:
        try:
            role = user.role.role_type
            if role == 'Owner':
                tasks = Task.objects.all()
            elif role == 'Team Leader':
                tasks = Task.objects.filter(assigned_by=user)
            else:  # Team Member or no role
                tasks = Task.objects.filter(assigned_to=user)
        except (Role.DoesNotExist, AttributeError):
            # Default to assigned tasks if no role
            tasks = Task.objects.filter(assigned_to=user)
    
    # Get selected task if any
    selected_id = request.GET.get("selected")
    selected_task = None
    if selected_id:
        try:
            selected_task = Task.objects.get(id=selected_id)
            # Check if user has permission to view this task
            if (not user.is_superuser and 
                user not in selected_task.assigned_to.all() and 
                user != selected_task.assigned_by):
                selected_task = None
                messages.error(request, "You don't have permission to view this task")
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
    
    return render(request, 'tracker/task_gallery.html', {
        'tasks': tasks,
        'selected_task': selected_task
    })

@login_required
def ai_task_create(request):
    """
    Create a new task using AI to extract details from a text prompt.
    
    This view handles both text prompts and voice input (if Whisper is installed).
    """
    categories = Category.objects.all()
    users = User.objects.all()
    
    if request.method == "POST":
        form = AITaskForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Process audio file if provided
                audio_file = request.FILES.get('audio_file')
                prompt = form.cleaned_data.get('prompt', '')
                
                if audio_file and not prompt:
                    # Transcribe audio to text
                    transcribed_text = transcribe_audio(audio_file)
                    if transcribed_text:
                        prompt = transcribed_text
                        messages.info(request, f"Transcribed audio: '{prompt[:100]}...'")
                    else:
                        messages.error(request, "Failed to transcribe audio. Please try again or enter text directly.")
                        return render(request, 'tracker/ai_task_form.html', {
                            'form': form,
                            'categories': categories,
                            'users': users
                        })
                
                # Generate task details from prompt
                if not prompt:
                    messages.error(request, "Please provide either text or audio input")
                    return render(request, 'tracker/ai_task_form.html', {
                        'form': form,
                        'categories': categories,
                        'users': users
                    })
                
                # Call Ollama to generate task details
                task_data = generate_task_from_prompt(prompt)
                
                if not task_data:
                    messages.error(request, "Failed to generate task from prompt. Please try again with a clearer description.")
                    return render(request, 'tracker/ai_task_form.html', {
                        'form': form,
                        'categories': categories,
                        'users': users
                    })
                
                # Create the task with generated data
                with transaction.atomic():
                    # Create a new task
                    task = Task()
                    
                    # Use user-provided values if available, otherwise use AI suggestions
                    task.title = form.cleaned_data.get('title') or task_data.get('title', 'Untitled Task')
                    task.description = task_data.get('description', prompt)
                    
                    # Get category from AI suggestion
                    category_id = task_data.get('category_id', 1)
                    try:
                        task.category = Category.objects.get(id=category_id)
                    except Category.DoesNotExist:
                        # Default to first category if suggested one doesn't exist
                        task.category = Category.objects.first()
                    
                    # Use user-provided priority if available, otherwise use AI suggestion
                    user_priority = form.cleaned_data.get('priority')
                    if user_priority:
                        task.priority = user_priority
                    else:
                        ai_priority = task_data.get('priority', 'Medium')
                        # Ensure priority is valid
                        from .models import PRIORITY_CHOICES
                        if ai_priority not in dict(PRIORITY_CHOICES):
                            ai_priority = 'Medium'
                        task.priority = ai_priority
                    
                    # Check if user explicitly provided a due date or cleared it
                    # If the form was submitted with an empty due_date field, form.cleaned_data['due_date'] will be None
                    # If the user didn't touch the field, it will have the default value (tomorrow)
                    user_due_date = form.cleaned_data.get('due_date')
                    default_due_date = date.today() + timedelta(days=1)
                    
                    # Check if the user explicitly cleared the due date field using the clear button
                    due_date_cleared = 'due_date_cleared' in request.POST
                    
                    # Check if the 'due_date' parameter was explicitly included in the POST data
                    due_date_in_post = 'due_date' in request.POST and request.POST['due_date']
                    
                    if due_date_cleared:
                        # User explicitly cleared the due date field, use AI suggestion
                        ai_due_date = task_data.get('due_date')
                        if ai_due_date:
                            task.due_date = ai_due_date
                            logger.info(f"Using AI-suggested due date (after user cleared field): {task.due_date}")
                        else:
                            # Default to 7 days from now if no AI suggestion
                            task.due_date = date.today() + timedelta(days=7)
                            logger.info(f"Using default due date (7 days) after user cleared field: {task.due_date}")
                    elif due_date_in_post:
                        # User explicitly set a due date
                        task.due_date = user_due_date
                        logger.info(f"Using user-provided due date: {task.due_date}")
                    else:
                        # Use AI-suggested date or default to 7 days from now
                        ai_due_date = task_data.get('due_date')
                        if ai_due_date:
                            task.due_date = ai_due_date
                            logger.info(f"Using AI-suggested due date: {task.due_date}")
                        else:
                            # Default to 7 days from now if no date is provided
                            task.due_date = date.today() + timedelta(days=7)
                            logger.info(f"Using default due date (7 days from now): {task.due_date}")
                    
                    logger.info(f"Setting task due date to: {task.due_date}")
                    
                    # Set default status
                    task.status = 'Not Started'
                    
                    # Set creator and assigner
                    task.created_by = request.user
                    task.assigned_by = request.user
                    
                    # Save the task
                    task.save()
                    
                    # Assign users
                    assigned_to = form.cleaned_data.get('assigned_to')
                    if assigned_to:
                        task.assigned_to.set(assigned_to)
                    else:
                        # Default to assigning the creator
                        task.assigned_to.add(request.user)
                    
                    logger.info(f"AI-generated task created: '{task.title}' by {request.user.username}")
                    messages.success(request, "Task created successfully using AI")
                    
                    # Redirect to the task detail page
                    return redirect('task_detail', task_id=task.id)
                    
            except Exception as e:
                logger.error(f"Error creating AI task: {str(e)}")
                messages.error(request, f"Error creating task: {str(e)}")
        else:
            logger.warning(f"Invalid AI task form: {form.errors}")
    else:
        form = AITaskForm()
    
    return render(request, 'tracker/ai_task_form.html', {
        'form': form,
        'categories': categories,
        'users': users
    })

@login_required
def task_gallery_view2(request):
    """
    Display tasks grouped by category with filtering.
    
    Shows pending tasks (not approved) for each category.
    """
    user = request.user
    selected_category_id = request.GET.get('category')
    
    # Get all categories
    categories = Category.objects.all()
    
    # Filter tasks by category and user permissions
    if selected_category_id:
        base_query = Task.objects.filter(category_id=selected_category_id)
        
        # Apply role-based filtering
        if not user.is_superuser:
            try:
                role = user.role.role_type
                if role == 'Owner':
                    # Owners see all tasks in the category
                    tasks = base_query
                elif role == 'Team Leader':
                    # Team Leaders see tasks they've assigned
                    tasks = base_query.filter(assigned_by=user)
                else:
                    # Team Members see tasks assigned to them
                    tasks = base_query.filter(assigned_to=user)
            except (Role.DoesNotExist, AttributeError):
                # Default to assigned tasks if no role
                tasks = base_query.filter(assigned_to=user)
        else:
            # Admins see all tasks
            tasks = base_query
    else:
        tasks = []
    
    # Prepare category data with pending task counts
    category_data = []
    for cat in categories:
        # Count pending tasks (not approved) for this category
        count_query = Task.objects.filter(category=cat).exclude(status='Approved')
        
        # Apply role-based filtering to counts as well
        if not user.is_superuser:
            try:
                role = user.role.role_type
                if role == 'Owner':
                    count = count_query.count()
                elif role == 'Team Leader':
                    count = count_query.filter(assigned_by=user).count()
                else:
                    count = count_query.filter(assigned_to=user).count()
            except (Role.DoesNotExist, AttributeError):
                count = count_query.filter(assigned_to=user).count()
        else:
            count = count_query.count()
            
        category_data.append({
            'id': cat.id,
            'name': cat.name,
            'pending_count': count
        })
    
    context = {
        'categories': category_data,
        'tasks': tasks,
        'selected_category_id': int(selected_category_id) if selected_category_id else None
    }
    
    return render(request, 'tracker/task_gallery2.html', context)
