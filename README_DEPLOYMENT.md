# Task Tracker Pro Deployment Guide

This document provides a quick overview of how to deploy Task Tracker Pro on Render, including both the web application and the AI model service.

## Deployment Architecture

Task Tracker Pro on Render consists of three components:

1. **Web Application** - Django application serving the user interface
2. **PostgreSQL Database** - Stores all application data
3. **AI Model Service** - Runs Ollama to provide AI-powered task creation

## Quick Start

### Option 1: One-Click Deployment (Recommended)

1. Fork this repository to your GitHub account
2. Sign up for a [Render account](https://render.com/)
3. In your Render dashboard, click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically configure all services based on the `render.yaml` file
6. Review the configuration and click "Apply"

### Option 2: Manual Deployment

Follow the detailed instructions in [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) to set up each service individually.

## Cost Considerations

- **Web Application**: Can run on Render's free tier
- **PostgreSQL Database**: Can run on Render's free tier
- **AI Model Service**: Requires a paid plan (minimum Standard - $7/month) due to memory requirements

## Free Tier Deployment

If you want to deploy Task Tracker Pro on Render's free tier, you have the following options:

### Option 1: Deploy without AI features

1. Comment out or remove the AI model service section in `render.yaml`
2. Set `OLLAMA_BASE_URL` to a placeholder value like `http://localhost:11434`
3. Deploy only the web application and database
4. The application will work normally, but AI-powered task creation will fall back to rule-based extraction

### Option 2: Use an external Ollama instance

1. Comment out or remove the AI model service section in `render.yaml`
2. Set up Ollama on your local machine or another server
3. Update `OLLAMA_BASE_URL` in your Render environment variables to point to your external Ollama instance
4. Ensure your Ollama instance is publicly accessible with proper security measures

### Option 3: Use a different AI service

1. Comment out or remove the AI model service section in `render.yaml`
2. Modify the application code to use a different AI service that's compatible with free accounts
3. Update the environment variables accordingly

## Key Files

- `render.yaml` - Blueprint configuration for all services
- `Dockerfile.ollama` - Docker configuration for the AI service
- `entrypoint.sh` - Script to initialize the AI service
- `RENDER_DEPLOYMENT.md` - Detailed deployment instructions

## Post-Deployment Steps

1. Create a superuser account
2. Configure any optional features (email, WhatsApp notifications)
3. Test the AI-powered task creation feature

## Troubleshooting

See the [Troubleshooting section](RENDER_DEPLOYMENT.md#troubleshooting) in the detailed deployment guide for common issues and solutions.

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Task Tracker Pro Documentation](README.md)
