# Task Tracker Pro

A comprehensive task management system built with Django and Django REST Framework.

## Features

- **User Authentication**: Secure login, registration, and role-based access control
- **Task Management**: Create, view, edit, and update tasks with detailed information
- **Role-Based Access Control**: Different permissions for Team Members, Team Leaders, and Owners
- **Real-time Notifications**: WhatsApp notifications for task status changes
- **File Attachments**: Upload and manage attachments for tasks
- **Task History**: Track changes to tasks with a detailed history log
- **Multiple Views**: Dashboard, gallery, and category-based views for tasks
- **RESTful API**: Complete API for integration with other systems

## Technology Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Notifications**: Twilio WhatsApp API
- **Deployment**: Render, Gunicorn, Whitenoise

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/task_tracker_pro.git
   cd task_tracker_pro
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Twilio settings (optional, for WhatsApp notifications)
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   TWILIO_WHATSAPP_FROM=your-twilio-whatsapp-number
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://localhost:8000

## Usage

1. **Login/Register**: Create an account or login with existing credentials
2. **Dashboard**: View all assigned tasks
3. **Task Creation**: Create new tasks with title, description, priority, etc.
4. **Task Management**: Update task status, add comments, upload attachments
5. **Gallery View**: Browse tasks in a visual gallery format
6. **Category View**: View tasks organized by category

## API Endpoints

- `/api/tasks/` - List and create tasks
- `/api/categories/` - List and create categories
- `/api/roles/` - Manage user roles (admin only)

## Testing

Run the test suite with:
```
pytest
```

## Deployment

The application is configured for deployment on Render with the included `render.yaml` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name - Initial work
