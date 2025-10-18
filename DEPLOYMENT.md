# 🚀 Deployment Guide: Multi-Agent Financial Analyst Tool

This guide walks you through deploying your Multi-Agent Financial Analyst Tool on free hosting platforms.

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ GitHub repository with your code
- ✅ OpenRouter API key (or OpenAI API key)
- ✅ GitHub account
- ✅ Render.com account (free)
- ✅ Streamlit Cloud account (free)

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Production Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Streamlit Cloud)     │  Backend (Render.com)        │
│  ┌─────────────────────────────┐ │  ┌─────────────────────────────┐ │
│  │ • https://your-app.streamlit.app │ │  │ • https://your-backend.onrender.com │ │
│  │ • Auto HTTPS                │ │  │ • Auto HTTPS                │ │
│  │ • Free hosting              │ │  │ • Free hosting              │ │
│  │ • Auto deployments          │ │  │ • Auto deployments          │ │
│  └─────────────────────────────┘ │  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Step 1: Deploy Backend on Render.com

### 1.1 Prepare Your Repository

Ensure your repository has these files:
- ✅ `render.yaml` (deployment configuration)
- ✅ `backend/requirements.txt` (backend dependencies)
- ✅ `backend/api.py` (FastAPI application)

### 1.2 Deploy on Render

1. **Go to Render.com**
   - Visit: https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Service**
   ```
   Name: multi-agent-fin-analyst-backend
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Build Command: pip install --upgrade pip && pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables**
   In the Render dashboard, add these environment variables:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   LLM_PROVIDER=openrouter
   LLM_MODEL_NAME=openai/gpt-3.5-turbo
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://your-service-name.onrender.com`

### 1.3 Verify Backend Deployment

Test your backend:
```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "uptime": 123.45
}
```

## 🎨 Step 2: Deploy Frontend on Streamlit Cloud

### 2.1 Prepare for Streamlit Cloud

1. **Update secrets configuration**
   - Your app already reads from `st.secrets`
   - No additional files needed

2. **Ensure requirements.txt is optimized**
   - The main `requirements.txt` includes all dependencies

### 2.2 Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub

2. **Deploy New App**
   - Click "New app"
   - Select your repository
   - Choose the main branch

3. **Configure App**
   ```
   Repository: your-username/multi-agent-fin-analyst
   Branch: main
   Main file path: app.py
   App URL: (will be auto-generated)
   ```

4. **Set Secrets**
   In the Streamlit Cloud dashboard, add these secrets:
   ```toml
   [api]
   backend_url = "https://your-service-name.onrender.com"
   
   [openrouter]
   api_key = "sk-or-v1-your-api-key-here"
   ```

5. **Deploy**
   - Click "Deploy!"
   - Wait for deployment (3-5 minutes)
   - Get your app URL: `https://your-app-name.streamlit.app`

### 2.3 Update CORS Settings

After deploying both services:

1. **Update Render Backend CORS**
   - Go to your Render service dashboard
   - Add environment variable:
   ```
   CORS_ORIGINS=https://your-app-name.streamlit.app
   ```
   - Redeploy the service

## 🔗 Step 3: Connect Frontend to Backend

### 3.1 Update Frontend Secrets

In Streamlit Cloud dashboard, update the secrets:
```toml
[api]
backend_url = "https://your-actual-backend-url.onrender.com"
```

### 3.2 Test the Connection

1. Visit your Streamlit app
2. Check the backend status in the sidebar
3. Try a sample query: "Analyze AAPL stock"

## 📊 Step 4: Verify Deployment

### 4.1 Test Backend Endpoints

```bash
# Health check
curl https://your-backend.onrender.com/health

# API documentation
# Visit: https://your-backend.onrender.com/docs
```

### 4.2 Test Frontend Features

1. **Chat Interface**: Send a stock analysis query
2. **Watchlist**: Add stocks to watchlist
3. **Charts**: Verify charts are generated
4. **Export**: Test export functions

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
- **Issue**: Build fails on Render
- **Solution**: Check `backend/requirements.txt` for version conflicts
- **Fix**: Update requirements.txt with compatible versions

#### Frontend Can't Connect to Backend
- **Issue**: CORS errors in browser console
- **Solution**: Update `CORS_ORIGINS` environment variable in Render
- **Fix**: Add your Streamlit Cloud URL to CORS origins

#### API Keys Not Working
- **Issue**: LLM calls failing
- **Solution**: Verify API keys are set correctly
- **Fix**: Double-check secret names match the code

#### Slow Performance
- **Issue**: Render free tier has cold starts
- **Solution**: This is normal for free tier
- **Fix**: Consider upgrading to paid plan for production

### Debug Commands

```bash
# Check backend logs
# Go to Render dashboard → Your service → Logs

# Check frontend logs  
# Go to Streamlit Cloud dashboard → Your app → Logs
```

## 📈 Monitoring & Maintenance

### 1. Monitor Usage
- **Render**: Check CPU/memory usage in dashboard
- **Streamlit Cloud**: Monitor app performance

### 2. Update Deployments
- **Automatic**: Both platforms auto-deploy on git push
- **Manual**: Trigger redeploy from dashboards

### 3. Scale Up (When Needed)
- **Render**: Upgrade to paid plan for better performance
- **Streamlit Cloud**: Free tier should handle moderate usage

## 🎉 Success!

Your Multi-Agent Financial Analyst Tool is now live at:
- **Frontend**: https://your-app-name.streamlit.app
- **Backend**: https://your-service-name.onrender.com
- **API Docs**: https://your-service-name.onrender.com/docs

## 🔄 Next Steps

1. **Custom Domain**: Add custom domain to your Streamlit app
2. **Database**: Add PostgreSQL for persistent storage
3. **Monitoring**: Set up error tracking and analytics
4. **Security**: Implement authentication and rate limiting

---

**Need Help?**
- 📚 [Render Documentation](https://render.com/docs)
- 📚 [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- 🐛 [GitHub Issues](https://github.com/your-username/multi-agent-fin-analyst/issues)