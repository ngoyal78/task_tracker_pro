# Deploying Task Tracker Pro on Render

This guide provides detailed instructions for deploying Task Tracker Pro on Render, including both the web application and the AI model service for GenAI features.

## Overview

Task Tracker Pro on Render consists of three components:

1. **Web Application**: The Django application that serves the user interface and handles business logic
2. **PostgreSQL Database**: Stores all application data
3. **AI Model Service**: Runs Ollama to provide AI-powered task creation features

## Prerequisites

Before you begin, ensure you have:

- A [Render account](https://render.com/) (with billing information for the AI service)
- Your project code in a Git repository (GitHub, GitLab, etc.)
- Basic understanding of Docker and containerization (for the AI service)

## Deployment Options

You can deploy Task Tracker Pro on Render in two ways:

### Option 1: Blueprint Deployment (Recommended)

This option uses the `render.yaml` file to automatically configure all services.

1. Fork or clone the Task Tracker Pro repository
2. Push it to your own Git repository
3. In your Render dashboard, click "New" and select "Blueprint"
4. Connect your Git repository
5. Render will automatically detect the `render.yaml` file and configure all services
6. Review the configuration and click "Apply"

### Option 2: Manual Deployment

If you prefer to set up each service individually, follow the steps in the subsequent sections.

## Step 1: Set Up a PostgreSQL Database

1. Log in to your Render dashboard
2. Click on "New" and select "PostgreSQL"
3. Configure your database:
   - Name: `task-tracker-db` (or your preferred name)
   - Database: `task_tracker`
   - User: `task_user`
   - Region: Choose the region closest to your users
   - PostgreSQL Version: 14 or higher
4. Click "Create Database"
5. Once created, note the PostgreSQL Connection String for the next step

## Step 2: Deploy the Web Application

1. In your Render dashboard, click "New" and select "Web Service"
2. Connect your Git repository
3. Configure your web service:
   - Name: `task-tracker-pro` (or your preferred name)
   - Environment: Python
   - Region: Choose the region closest to your users (same as database)
   - Branch: `main` (or your deployment branch)
   - Build Command: 
     ```
     pip install -r requirements.txt
     python manage.py collectstatic --noinput
     python manage.py migrate
     ```
   - Start Command: 
     ```
     gunicorn task_tracker_pro.wsgi:application --bind 0.0.0.0:$PORT
     ```
4. Set up the required environment variables (see Step 4)
5. Click "Create Web Service"

## Step 3: Deploy the AI Model Service

The AI model service runs Ollama in a Docker container to provide AI-powered task creation.

1. In your Render dashboard, click "New" and select "Web Service"
2. Connect your Git repository
3. Configure your web service:
   - Name: `task-tracker-ai` (or your preferred name)
   - Environment: Docker
   - Region: Choose the region closest to your users (same as other services)
   - Branch: `main` (or your deployment branch)
   - Docker Build Context: `.` (root of repository)
   - Dockerfile Path: `Dockerfile.ollama`
   - Plan: Standard (minimum) - Ollama requires at least 2GB RAM
4. Under "Advanced" settings:
   - Add a disk:
     - Name: `ollama-models`
     - Mount Path: `/root/.ollama`
     - Size: 10 GB (adjust based on model size requirements)
5. Set environment variables:
   - `OLLAMA_HOST`: `0.0.0.0`
   - `OLLAMA_MODELS`: `mistral` (or comma-separated list of models to pull)
6. Click "Create Web Service"

**Important Notes about the AI Service:**

- The AI service requires a paid plan (minimum Standard) due to memory requirements
- Initial deployment may take several minutes as it needs to pull and set up the AI models
- The disk storage is necessary to persist models between deployments

## Step 4: Configure Environment Variables

### Web Application Variables

Set the following environment variables for the web application:

#### Required Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `task_tracker_pro.settings` |
| `SECRET_KEY` | Django secret key (use "Generate" in Render) | [auto-generated] |
| `DEBUG` | Debug mode (should be False in production) | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `task-tracker-pro.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | [From Step 1] |
| `RENDER` | Flag to indicate running on Render | `True` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF | `https://task-tracker-pro.onrender.com` |
| `OLLAMA_BASE_URL` | URL of your AI service | `https://task-tracker-ai.onrender.com` |
| `OLLAMA_MODEL` | Ollama model to use | `mistral` |
| `WHISPER_ENABLED` | Enable voice input | `False` |

#### Optional Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `EMAIL_HOST` | SMTP server for emails | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS for email | `True` |
| `EMAIL_HOST_USER` | Email username | `your-email@example.com` |
| `EMAIL_HOST_PASSWORD` | Email password | `your-app-password` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp number | `+14155238886` |

### AI Service Variables

Set the following environment variables for the AI service:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `OLLAMA_HOST` | Host to bind Ollama server | `0.0.0.0` |
| `OLLAMA_MODELS` | Comma-separated list of models to pull | `mistral` |

## Step 5: Create a Superuser

After deployment, create a superuser to access the admin interface:

1. In your Render dashboard, go to your web application service
2. Click on "Shell"
3. Run the following command:
   ```
   python manage.py createsuperuser
   ```
4. Follow the prompts to create a superuser

Alternatively, use the provided `create_superuser.py` script:

1. Set the following environment variables in your web application service:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`
2. In the Shell, run:
   ```
   python create_superuser.py
   ```

## Step 6: Verify Deployment

1. Access your web application at `https://task-tracker-pro.onrender.com` (or your custom domain)
2. Log in with the superuser credentials
3. Create a new task using the AI-powered task creation feature
4. Verify that the AI model is generating task details correctly

## Troubleshooting

### Web Application Issues

#### Database Connection Issues

If you encounter database connection issues:

1. Verify that the `DATABASE_URL` environment variable is correctly set
2. Check if your database is running and accessible
3. Ensure your IP is allowed in the database firewall rules

#### Static Files Not Loading

If static files are not loading:

1. Verify that `STATIC_URL` and `STATIC_ROOT` are correctly set in `settings.py`
2. Ensure that `whitenoise.middleware.WhiteNoiseMiddleware` is included in `MIDDLEWARE`
3. Run `python manage.py collectstatic --noinput` manually in the Shell

### AI Service Issues

#### AI Service Not Responding

If the AI service is not responding:

1. Check the logs of the AI service in your Render dashboard
2. Verify that the service has enough memory (at least 2GB)
3. Ensure the `OLLAMA_BASE_URL` in the web application points to the correct AI service URL
4. Check if the model was pulled successfully during deployment

#### Model Loading Errors

If you see model loading errors:

1. Verify that the disk is properly mounted at `/root/.ollama`
2. Check if the model specified in `OLLAMA_MODELS` is valid
3. Try manually pulling the model through the Shell:
   ```
   ollama pull mistral
   ```

#### Slow Response Times

If the AI service is responding slowly:

1. Consider upgrading to a higher plan with more resources
2. Use a smaller model (e.g., `mistral:7b` instead of larger variants)
3. Implement caching for common AI requests

## Scaling and Performance

### Web Application Scaling

To scale your web application:

1. In your Render dashboard, go to your web service
2. Click on "Settings"
3. Under "Instance Type", select a larger instance type
4. Optionally, enable auto-scaling for handling traffic spikes
5. Click "Save Changes"

### AI Service Scaling

To scale your AI service:

1. In your Render dashboard, go to your AI service
2. Click on "Settings"
3. Under "Instance Type", select a larger instance type (more memory is better for AI workloads)
4. Increase the disk size if needed for larger models
5. Click "Save Changes"

## Cost Optimization

### Free Tier Usage

The web application and database can run on Render's free tier with limitations:

1. **Web Service Limitations**:
   - Free web services are automatically spun down after 15 minutes of inactivity
   - They take a few seconds to spin up when a new request comes in
   - Limited to 750 hours of runtime per month
   - 512 MB RAM and 0.5 CPU

2. **Database Limitations**:
   - Free PostgreSQL databases are limited to 1 GB storage
   - Automatically suspended after 90 days of inactivity
   - No automatic backups (you should create manual backups regularly)
   - Limited to shared CPU and 256 MB RAM

### AI Service Costs

The AI service requires a paid plan due to memory requirements:

1. **Minimum Requirements**:
   - Standard plan ($7/month) with 2GB RAM
   - 10GB disk storage ($0.15/GB/month = $1.50/month)
   - Total minimum cost: ~$8.50/month

### Cost Reduction Strategies

1. **Suspend AI Service When Not Needed**:
   - If you don't need AI features constantly, you can suspend the AI service
   - Implement a fallback in the web application to handle AI service unavailability
   - Resume the service when needed

2. **Use Smaller Models**:
   - Smaller models require less memory and disk space
   - Consider using `mistral:7b-instruct-v0.2-q4_0` for a smaller quantized model

3. **Optimize Database Usage**:
   - Regularly clean up unnecessary data
   - Implement efficient queries to reduce database load

## Security Considerations

1. **Web Application Security**:
   - Ensure `DEBUG` is set to `False` in production
   - Use a strong, unique `SECRET_KEY`
   - Keep your database credentials secure
   - Enable HTTPS-only cookies by setting `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` to `True`

2. **AI Service Security**:
   - The AI service is publicly accessible by default
   - Consider implementing authentication between the web application and AI service
   - Monitor the AI service for unusual activity or abuse

3. **Regular Updates**:
   - Keep all dependencies updated to patch security vulnerabilities
   - Regularly update the Ollama image to get the latest security fixes

## Backup and Recovery

### Database Backups

Render automatically creates daily backups of your PostgreSQL database on paid plans. To restore a backup:

1. In your Render dashboard, go to your database
2. Click on "Backups"
3. Select the backup you want to restore
4. Click "Restore"

For free plans, create manual backups regularly:

1. In your Render dashboard, go to your database
2. Click on "Backups"
3. Click "Create Backup"

### AI Model Backups

The AI models are stored on the persistent disk. If you need to back up custom models:

1. Use the Shell to access your AI service
2. Copy the models from `/root/.ollama/models`
3. Store them in a secure location

## Custom Domain Configuration

To use a custom domain:

1. In your Render dashboard, go to your web service
2. Click on "Settings"
3. Under "Custom Domain", click "Add Custom Domain"
4. Enter your domain name and follow the instructions to configure DNS
5. Update the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment variables to include your custom domain

If you want to use a custom domain for the AI service as well:

1. Follow the same steps for the AI service
2. Update the `OLLAMA_BASE_URL` environment variable in the web application to point to the new domain

## Monitoring and Logging

Render provides built-in monitoring and logging for all services:

1. In your Render dashboard, go to your service
2. Click on "Metrics" to view CPU, memory, and network usage
3. Click on "Logs" to view application logs

For more advanced monitoring:

1. Consider integrating with a third-party monitoring service
2. Implement custom logging in your application
3. Set up alerts for critical events

## Updating Your Application

To update your application:

1. Push changes to your Git repository
2. Render will automatically detect the changes and redeploy your application
3. Monitor the deployment in your Render dashboard

For manual redeployment:

1. In your Render dashboard, go to your service
2. Click on "Manual Deploy"
3. Select "Deploy latest commit" or "Clear build cache & deploy"

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Docker Documentation](https://docs.docker.com/)
