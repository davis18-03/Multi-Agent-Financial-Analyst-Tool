# Deployment Checklist for Render.com

## Pre-Deployment

- [ ] Fork the repository to your GitHub account
- [ ] Obtain API keys (OpenRouter or OpenAI)
- [ ] Review `render.yaml` configuration
- [ ] Test locally with `python health_check.py`

## Render.com Setup

- [ ] Create account on [Render.com](https://render.com)
- [ ] Connect GitHub account
- [ ] Create new Web Service
- [ ] Select your forked repository
- [ ] Choose branch: `main`

## Environment Variables

Set these in Render dashboard under "Environment":

### Required
- [ ] `OPENROUTER_API_KEY` - Your OpenRouter API key
  - OR `OPENAI_API_KEY` - Your OpenAI API key

### Optional (with defaults)
- [ ] `LLM_PROVIDER` - Default: `fallback`
- [ ] `LLM_MODEL_NAME` - Default: `openai/gpt-3.5-turbo`
- [ ] `LLM_MAX_TOKENS` - Default: `200`
- [ ] `LLM_TEMPERATURE` - Default: `0.3`
- [ ] `CACHE_SIZE` - Default: `128`
- [ ] `REQUEST_TIMEOUT` - Default: `30`

## Deployment Settings

- [ ] **Build Command**: `pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r backend/requirements.txt`
- [ ] **Start Command**: `python start_render.py`
- [ ] **Environment**: `python`
- [ ] **Python Version**: `3.10`
- [ ] **Region**: Choose closest to your users
- [ ] **Plan**: `free` (or upgrade as needed)

## Post-Deployment

- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check deployment logs for errors
- [ ] Test health endpoint: `https://your-app-name.onrender.com/health`
- [ ] Test API docs: `https://your-app-name.onrender.com/docs`
- [ ] Run health check: `python health_check.py https://your-app-name.onrender.com`

## Frontend Deployment (Streamlit Cloud)

If deploying frontend separately:

- [ ] Deploy to [Streamlit Cloud](https://streamlit.io/cloud)
- [ ] Set `BACKEND_URL` to your Render backend URL
- [ ] Update CORS origins in `render.yaml`

## Troubleshooting

### Port Binding Issues
- Ensure `PORT` environment variable is used
- Check `start_render.py` script
- Verify `render.yaml` start command

### Build Failures
- Check Python version compatibility
- Verify all dependencies in `requirements.txt`
- Check build logs for specific errors

### Runtime Errors
- Check application logs in Render dashboard
- Verify environment variables are set
- Test API endpoints individually

### Performance Issues
- Consider upgrading from free tier
- Monitor resource usage
- Optimize agent configurations

## Monitoring

- [ ] Set up health check monitoring
- [ ] Monitor application logs
- [ ] Track API usage and performance
- [ ] Set up alerts for downtime

## Security

- [ ] Secure API keys (never commit to repository)
- [ ] Configure CORS properly for production
- [ ] Review and limit API access as needed
- [ ] Enable HTTPS (automatic on Render)

## Maintenance

- [ ] Regular dependency updates
- [ ] Monitor for security vulnerabilities
- [ ] Backup important data/configurations
- [ ] Plan for scaling if needed