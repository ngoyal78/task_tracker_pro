# Task Tracker Pro - Free Tier Deployment Guide

This guide provides step-by-step instructions for deploying Task Tracker Pro on Render using only the free tier. This deployment will include the web application and database, with the AI features falling back to rule-based extraction.

## Prerequisites

Before you begin, ensure you have:

- A [Render account](https://render.com/) (free tier is sufficient)
- A GitHub account (to fork the repository)
- Basic familiarity with Git and GitHub

## Step 1: Fork the Repository

1. Go to the Task Tracker Pro GitHub repository
2. Click the "Fork" button in the top-right corner
3. Wait for the repository to be forked to your GitHub account

## Step 2: Deploy to Render

### Option A: One-Click Deployment (Recommended)

1. Log in to your Render account
2. Click the button below to deploy directly from your forked repository:

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

3. Select your forked repository
4. Render will automatically detect the `render.yaml` file and configure the services
5. Review the configuration and click "Apply"
6. Wait for the deployment to complete (this may take a few minutes)

### Option B: Manual Deployment

If you prefer to set up the services manually or the one-click deployment doesn't work:

1. **Create a PostgreSQL Database**:
   - Log in to your Render dashboard
   - Click "New" and select "PostgreSQL"
   - Configure your database:
     - Name: `task-tracker-db`
     - Database: `task_tracker`
     - User: `task_tracker_user`
     - Region: Choose the region closest to your users
     - Plan: Free
   - Click "Create Database"
   - Once created, note the Internal Database URL for the next step

2. **Deploy the Web Application**:
   - In your Render dashboard, click "New" and select "Web Service"
   - Connect your forked GitHub repository
   - Configure your web service:
     - Name: `task-tracker-pro`
     - Environment: Python
     - Region: Same as your database
     - Branch: `main` (or your deployment branch)
     - Build Command: 
       ```
       pip install -r requirements.txt
       python manage.py collectstatic --noinput
       python manage.py makemigrations tracker
       python manage.py migrate
       python manage.py createsuperuser --noinput || true
       ```
     - Start Command: 
       ```
       gunicorn task_tracker_pro.wsgi:application --bind 0.0.0.0:$PORT
       ```
   - Set up the required environment variables (see Step 3)
   - Click "Create Web Service"

## Step 3: Configure Environment Variables

If you used the one-click deployment, most environment variables will be set automatically. However, you should verify and set the following variables in your web service settings:

### Required Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `SECRET_KEY` | Django secret key | [auto-generated] |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `.onrender.com` |
| `RENDER` | Flag for Render | `True` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins | `https://*.onrender.com` |
| `DATABASE_URL` | Database connection string | [From your database service] |
| `OLLAMA_BASE_URL` | URL for Ollama API | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `mistral` |

### Superuser Creation (Optional)

To automatically create a superuser during deployment, set these variables:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `DJANGO_SUPERUSER_USERNAME` | Admin username | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | `your-secure-password` |

## Step 4: Verify Deployment

1. Once deployment is complete, click on the generated URL to access your application
2. You should see the Task Tracker Pro login page
3. Log in with your superuser credentials
4. Verify that you can create and manage tasks

## Understanding Free Tier Limitations

### Web Service Limitations

- Free web services are automatically spun down after 15 minutes of inactivity
- They take a few seconds to spin up when a new request comes in
- Limited to 750 hours of runtime per month
- 512 MB RAM and 0.5 CPU

### Database Limitations

- Free PostgreSQL databases are limited to 1 GB storage
- Automatically suspended after 90 days of inactivity
- No automatic backups (you should create manual backups regularly)
- Limited to shared CPU and 256 MB RAM

### AI Feature Limitations

Since we're not deploying the Ollama service (which requires a paid plan), the AI features will fall back to rule-based extraction. This means:

- AI-powered task creation will use simpler rule-based extraction
- The quality of extracted task details may be lower than with the full AI service
- Voice input features (if enabled) will not work

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. **Verify database service creation**:
   - In your Render dashboard, ensure the PostgreSQL database service is created and running
   - Wait a few minutes after creating the database before deploying the web service

2. **Check environment variables**:
   - Verify that the `DATABASE_URL` environment variable is correctly set in your web service
   - The URL should be in the format: `postgres://username:password@hostname:port/database_name`
   - You can copy this directly from the database service's "Connection" tab in the Render dashboard

3. **Manual connection string setup**:
   - If using the `fromDatabase` property in `render.yaml` isn't working, try setting the `DATABASE_URL` manually:
     ```
     - key: DATABASE_URL
       value: "postgres://username:password@hostname:port/database_name"
     ```

4. **Restart services**:
   - Try restarting both the database and web service
   - In the Render dashboard, go to each service and click "Manual Deploy" → "Clear build cache & deploy"

### Migration Issues

If you encounter migration issues:

1. **Check the build logs** for any errors during the migration process
2. **Verify that the database exists** and is accessible
3. **Try running migrations manually** through the Render shell:
   ```
   python manage.py makemigrations tracker
   python manage.py migrate
   ```

### Static Files Not Loading

If static files are not loading:

1. Verify that `STATIC_URL` and `STATIC_ROOT` are correctly set in `settings.py`
2. Ensure that `whitenoise.middleware.WhiteNoiseMiddleware` is included in `MIDDLEWARE`
3. Run `python manage.py collectstatic --noinput` manually in the Shell

## Upgrading Later

If you later decide to enable the full AI features:

1. Update the `render.yaml` file to include the Ollama service
2. Change your plan to a paid plan that supports Docker containers
3. Update the `OLLAMA_BASE_URL` to point to your Ollama service

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Task Tracker Pro Documentation](README.md)
