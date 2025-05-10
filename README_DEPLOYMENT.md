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
