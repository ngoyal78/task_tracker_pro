#!/usr/bin/env python
"""
Setup script for Task Tracker Pro deployment on Render.
This script helps verify your environment and prepare for deployment.
"""

import os
import sys
import subprocess
import random
import string
import re
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=check, text=True, capture_output=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.returncode

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print_header("Checking Prerequisites")
    
    # Check Python version
    python_version, _ = run_command("python --version")
    if "Python 3" in python_version:
        print_success(f"Python installed: {python_version}")
    else:
        print_error(f"Python 3 required, found: {python_version}")
        return False
    
    # Check pip
    pip_version, pip_status = run_command("pip --version")
    if pip_status == 0:
        print_success(f"pip installed: {pip_version}")
    else:
        print_error("pip not found")
        return False
    
    # Check Git
    git_version, git_status = run_command("git --version")
    if git_status == 0:
        print_success(f"Git installed: {git_version}")
    else:
        print_error("Git not found")
        return False
    
    # Check if render.yaml exists
    if os.path.exists("render.yaml"):
        print_success("render.yaml found")
    else:
        print_error("render.yaml not found")
        return False
    
    return True

def check_django_project():
    """Check if the Django project is properly set up."""
    print_header("Checking Django Project")
    
    # Check if manage.py exists
    if os.path.exists("manage.py"):
        print_success("manage.py found")
    else:
        print_error("manage.py not found. Are you in the correct directory?")
        return False
    
    # Check if requirements.txt exists
    if os.path.exists("requirements.txt"):
        print_success("requirements.txt found")
    else:
        print_error("requirements.txt not found")
        return False
    
    # Check if the tracker app exists
    if os.path.exists("tracker"):
        print_success("tracker app found")
    else:
        print_error("tracker app not found")
        return False
    
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    print_header("Checking Environment Variables")
    
    # List of required environment variables
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "ALLOWED_HOSTS",
    ]
    
    # Optional but recommended variables
    optional_vars = [
        "DJANGO_SUPERUSER_USERNAME",
        "DJANGO_SUPERUSER_EMAIL",
        "DJANGO_SUPERUSER_PASSWORD",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
    ]
    
    # Check required variables
    missing_vars = []
    for var in required_vars:
        if var in os.environ:
            print_success(f"{var} is set")
        else:
            print_error(f"{var} is not set")
            missing_vars.append(var)
    
    # Check optional variables
    for var in optional_vars:
        if var in os.environ:
            print_success(f"{var} is set")
        else:
            print_warning(f"{var} is not set (optional)")
    
    if missing_vars:
        print_info("You need to set the following environment variables:")
        for var in missing_vars:
            if var == "SECRET_KEY":
                # Generate a random secret key
                chars = string.ascii_letters + string.digits + string.punctuation
                secret_key = ''.join(random.choice(chars) for _ in range(50))
                print(f"  {var}='{secret_key}'")
            elif var == "DATABASE_URL":
                print(f"  {var}='postgres://username:password@hostname:port/database_name'")
            elif var == "ALLOWED_HOSTS":
                print(f"  {var}='.onrender.com'")
            else:
                print(f"  {var}='your_value_here'")
        return False
    
    return True

def setup_local_database():
    """Set up a local database for testing."""
    print_header("Setting Up Local Database")
    
    # Check if PostgreSQL is installed
    pg_version, pg_status = run_command("psql --version")
    if pg_status != 0:
        print_error("PostgreSQL not found. Please install PostgreSQL first.")
        return False
    
    print_success(f"PostgreSQL installed: {pg_version}")
    
    # Create a local database
    db_name = "task_tracker"
    db_user = "task_tracker_user"
    db_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    print_info(f"Creating database '{db_name}' with user '{db_user}'...")
    
    # Create user
    _, user_status = run_command(f"psql -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\"", check=False)
    if user_status == 0:
        print_success(f"User '{db_user}' created")
    else:
        print_warning(f"User '{db_user}' may already exist")
    
    # Create database
    _, db_status = run_command(f"psql -c \"CREATE DATABASE {db_name} OWNER {db_user};\"", check=False)
    if db_status == 0:
        print_success(f"Database '{db_name}' created")
    else:
        print_warning(f"Database '{db_name}' may already exist")
    
    # Set DATABASE_URL environment variable
    db_url = f"postgres://{db_user}:{db_password}@localhost:5432/{db_name}"
    os.environ["DATABASE_URL"] = db_url
    print_info(f"Set DATABASE_URL to '{db_url}'")
    print_info("You should add this to your .env file or Render environment variables")
    
    return True

def create_superuser():
    """Create a superuser for the Django application."""
    print_header("Creating Superuser")
    
    # Check if superuser environment variables are set
    if not all(var in os.environ for var in ["DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_EMAIL", "DJANGO_SUPERUSER_PASSWORD"]):
        username = input("Enter superuser username [admin]: ") or "admin"
        email = input("Enter superuser email [admin@example.com]: ") or "admin@example.com"
        password = input("Enter superuser password: ")
        
        if not password:
            print_error("Password cannot be empty")
            return False
        
        os.environ["DJANGO_SUPERUSER_USERNAME"] = username
        os.environ["DJANGO_SUPERUSER_EMAIL"] = email
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = password
    
    # Create superuser
    print_info("Creating superuser...")
    output, status = run_command("python manage.py createsuperuser --noinput")
    
    if status == 0:
        print_success("Superuser created successfully")
    else:
        if "already exists" in output:
            print_warning("Superuser already exists")
        else:
            print_error(f"Failed to create superuser: {output}")
            return False
    
    return True

def prepare_for_render():
    """Prepare the project for deployment to Render."""
    print_header("Preparing for Render Deployment")
    
    # Check if Git repository is initialized
    _, git_status = run_command("git status")
    if git_status != 0:
        print_info("Initializing Git repository...")
        run_command("git init")
        print_success("Git repository initialized")
    else:
        print_success("Git repository already initialized")
    
    # Create .gitignore if it doesn't exist
    if not os.path.exists(".gitignore"):
        print_info("Creating .gitignore...")
        with open(".gitignore", "w") as f:
            f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media

# Environment variables
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS specific
.DS_Store
Thumbs.db
            """)
        print_success(".gitignore created")
    else:
        print_success(".gitignore already exists")
    
    # Check if .env file exists and add it to .gitignore
    if os.path.exists(".env"):
        with open(".gitignore", "r") as f:
            gitignore = f.read()
        
        if ".env" not in gitignore:
            with open(".gitignore", "a") as f:
                f.write("\n.env\n")
            print_success("Added .env to .gitignore")
    
    # Commit changes
    print_info("Committing changes...")
    run_command("git add .")
    run_command("git commit -m \"Prepare for Render deployment\"", check=False)
    print_success("Changes committed")
    
    # Instructions for pushing to GitHub
    print_info("Next steps:")
    print_info("1. Create a new repository on GitHub")
    print_info("2. Push your code to GitHub:")
    print_info("   git remote add origin https://github.com/yourusername/your-repo.git")
    print_info("   git branch -M main")
    print_info("   git push -u origin main")
    print_info("3. Deploy to Render using the instructions in FREE_TIER_DEPLOYMENT.md")
    
    return True

def main():
    """Main function to run the setup script."""
    print_header("Task Tracker Pro - Render Deployment Setup")
    
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix the issues and try again.")
        return
    
    if not check_django_project():
        print_error("Django project check failed. Please fix the issues and try again.")
        return
    
    # Set a default SECRET_KEY if not set
    if "SECRET_KEY" not in os.environ:
        chars = string.ascii_letters + string.digits + string.punctuation
        os.environ["SECRET_KEY"] = ''.join(random.choice(chars) for _ in range(50))
        print_info("Set a random SECRET_KEY for local development")
    
    # Set default ALLOWED_HOSTS if not set
    if "ALLOWED_HOSTS" not in os.environ:
        os.environ["ALLOWED_HOSTS"] = "localhost,127.0.0.1,.onrender.com"
        print_info("Set default ALLOWED_HOSTS for local development and Render")
    
    # Ask if user wants to set up a local database
    setup_db = input("Do you want to set up a local PostgreSQL database? (y/n) [n]: ").lower() == "y"
    if setup_db:
        if not setup_local_database():
            print_error("Database setup failed. Please fix the issues and try again.")
            return
    
    # Ask if user wants to create a superuser
    create_su = input("Do you want to create a superuser? (y/n) [y]: ")
    if create_su.lower() != "n":
        if not create_superuser():
            print_error("Superuser creation failed. Please fix the issues and try again.")
            return
    
    # Ask if user wants to prepare for Render deployment
    prepare = input("Do you want to prepare the project for Render deployment? (y/n) [y]: ")
    if prepare.lower() != "n":
        if not prepare_for_render():
            print_error("Preparation for Render deployment failed. Please fix the issues and try again.")
            return
    
    print_header("Setup Complete")
    print_success("Your project is now ready for deployment to Render!")
    print_info("Follow the instructions in FREE_TIER_DEPLOYMENT.md to deploy your application.")

if __name__ == "__main__":
    main()
