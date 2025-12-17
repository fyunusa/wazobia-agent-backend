# Deployment Guide - Render

## Quick Deploy to Render

### Prerequisites
- GitHub account with the backend repository
- Groq API key (free at https://console.groq.com)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with your GitHub account
3. No credit card required for free tier

### Step 2: Deploy from GitHub
1. Click "New +" → "Web Service"
2. Connect your GitHub account
3. Select the `wazobia-agent-backend` repository
4. Render will auto-detect the `render.yaml` configuration

### Step 3: Configure Environment Variables
Add these environment variables in Render dashboard:
- `GROQ_API_KEY`: Your Groq API key
- `ENVIRONMENT`: production
- `API_HOST`: 0.0.0.0

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will:
   - Install Python 3.10
   - Install dependencies from requirements.txt
   - Start the server with uvicorn
3. Wait 3-5 minutes for initial deployment

### Step 5: Get Your API URL
- Your API will be available at: `https://wazobia-agent-backend.onrender.com`
- Health check: `https://wazobia-agent-backend.onrender.com/health`
- API docs: `https://wazobia-agent-backend.onrender.com/docs`

### Step 6: Update Frontend
Update your frontend environment variable:
```
VITE_API_URL=https://wazobia-agent-backend.onrender.com
```

## Free Tier Limitations
- **Sleep after 15 minutes**: App goes to sleep after inactivity
- **Wake-up time**: ~30 seconds to wake from sleep
- **750 hours/month**: Enough for 24/7 uptime
- **512 MB RAM**: Sufficient for this application

## Keeping Your App Awake (Optional)
To prevent sleep, use a cron job to ping your health endpoint every 10 minutes:
```bash
# Add to cron-job.org or similar service
curl https://wazobia-agent-backend.onrender.com/health
```

## Troubleshooting

### Build Fails
- Check that `groq` is uncommented in requirements.txt
- Verify Python version is 3.10+
- Check build logs in Render dashboard

### App Crashes on Start
- Ensure `GROQ_API_KEY` environment variable is set
- Check application logs in Render dashboard
- Verify `/health` endpoint returns 200

### Slow Response
- Free tier apps sleep after 15 min inactivity
- First request after sleep takes ~30s
- Consider upgrading to paid tier ($7/month) for always-on

## Manual Deployment (Alternative)

If you prefer manual setup instead of `render.yaml`:

1. **Create Web Service** manually
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
4. **Environment**: Python 3
5. Add environment variables as listed above

## Production Checklist
- ✅ Set `ENVIRONMENT=production` in Render
- ✅ Add `GROQ_API_KEY` environment variable
- ✅ Test `/health` endpoint after deployment
- ✅ Update frontend with production API URL
- ✅ Test all endpoints via `/docs` page
- ✅ Monitor logs for any errors
