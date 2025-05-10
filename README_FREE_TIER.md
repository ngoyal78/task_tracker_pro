# Task Tracker Pro - Free Tier Deployment

This README provides a quick overview of deploying Task Tracker Pro on Render's free tier. For detailed instructions, please refer to [FREE_TIER_DEPLOYMENT.md](FREE_TIER_DEPLOYMENT.md).

## What's Included

- **Web Application**: Django-based task management system
- **Database**: PostgreSQL database for storing tasks and user data
- **AI Features**: Rule-based task extraction (fallback mode without Ollama)

## Quick Start

1. **Fork the Repository**
   - Create your own copy of the Task Tracker Pro repository

2. **Deploy to Render**
   - Use the one-click deployment button in [FREE_TIER_DEPLOYMENT.md](FREE_TIER_DEPLOYMENT.md)
   - Or follow the manual deployment instructions

3. **Configure Environment Variables**
   - Set up required environment variables in the Render dashboard
   - Create a superuser for admin access

4. **Start Using Task Tracker Pro**
   - Access your application at the provided Render URL
   - Log in and start managing your tasks

## Files for Deployment

- `render.yaml`: Configuration file for Render services
- `FREE_TIER_DEPLOYMENT.md`: Detailed deployment instructions
- `setup_render_deployment.py`: Helper script for local setup and testing

## Free Tier Limitations

- Web service spins down after 15 minutes of inactivity
- Database limited to 1 GB storage
- AI features use rule-based extraction instead of the full Ollama model

## Upgrading Later

If you later decide to enable the full AI features with Ollama:

1. Update the `render.yaml` file to include the Ollama service
2. Change your plan to a paid plan that supports Docker containers
3. Update the `OLLAMA_BASE_URL` to point to your Ollama service

## Troubleshooting

See the [Troubleshooting section](FREE_TIER_DEPLOYMENT.md#troubleshooting) in the detailed deployment guide for common issues and solutions.

## Local Development

To set up the project locally before deploying:

```bash
# Clone your forked repository
git clone https://github.com/yourusername/task-tracker-pro.git
cd task-tracker-pro

# Run the setup script
python setup_render_deployment.py

# Follow the prompts to set up your local environment
```

## Need Help?

If you encounter any issues during deployment, check the [FREE_TIER_DEPLOYMENT.md](FREE_TIER_DEPLOYMENT.md) file for detailed troubleshooting steps.
