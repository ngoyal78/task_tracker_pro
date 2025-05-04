import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_tracker_pro.settings')
django.setup()

from django.contrib.auth.models import User

# Check if superuser already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created with password 'admin123'")
else:
    print("Superuser 'admin' already exists")
