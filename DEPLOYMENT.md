# Deployment Guide

This guide will help you deploy the File Protector application with the frontend on Vercel and backend on Render.

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- Render account (free tier works)
- MongoDB Atlas account (for cloud storage)

## Step 1: Deploy Backend to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this project

3. **Configure the Service**:
   - **Name**: `file-protector-backend` (or any name you prefer)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Set Environment Variables**:
   - Click on "Environment" tab
   - Add the following variables:
     ```
     MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
     DB_NAME=file_backups
     PORT=10000
     ```
   - Replace `MONGO_URI` with your actual MongoDB connection string

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete
   - **Copy the service URL** (e.g., `https://file-protector-backend.onrender.com`)

## Step 2: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure Project**:
   - **Framework Preset**: Leave as default (Vercel will auto-detect)
   - **Root Directory**: Leave empty (or set to `frontend` if needed)
   - The `vercel.json` file will handle the configuration

4. **Set Environment Variables**:
   - Go to "Settings" → "Environment Variables"
   - Add:
     ```
     REACT_APP_API_URL=https://your-backend-url.onrender.com
     ```
   - Replace with your actual Render backend URL (no trailing slash)

5. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

## Step 3: Verify Deployment

1. **Test Backend**:
   - Visit: `https://your-backend-url.onrender.com/api/status`
   - Should return JSON with status information

2. **Test Frontend**:
   - Visit your Vercel deployment URL
   - Open browser console (F12)
   - Check for any CORS or API errors
   - Try using the application

## Troubleshooting

### Backend Issues

**Problem**: Backend returns 500 errors
- **Solution**: Check Render logs for errors. Common issues:
  - Missing environment variables
  - MongoDB connection string incorrect
  - Port configuration issues

**Problem**: Backend times out
- **Solution**: Render free tier services spin down after inactivity. First request may take 30-60 seconds to wake up.

**Problem**: CORS errors
- **Solution**: CORS is already enabled in the backend. Make sure your frontend URL is correct.

### Frontend Issues

**Problem**: API calls fail
- **Solution**: 
  - Verify `REACT_APP_API_URL` is set correctly in Vercel
  - Check that the backend URL is accessible
  - Ensure no trailing slash in the backend URL

**Problem**: Build fails
- **Solution**: 
  - Check Vercel build logs
  - Ensure all dependencies are in `package.json`
  - Verify Node.js version compatibility

### Common Configuration Mistakes

1. **Trailing Slash**: Don't include trailing slash in `REACT_APP_API_URL`
   - ✅ Correct: `https://backend.onrender.com`
   - ❌ Wrong: `https://backend.onrender.com/`

2. **Wrong Backend URL**: Make sure you're using the Render service URL, not the GitHub repo URL

3. **Environment Variables**: 
   - Frontend variables must start with `REACT_APP_`
   - Backend variables are case-sensitive

## Updating Deployments

### Update Backend
- Push changes to your repository
- Render will automatically redeploy

### Update Frontend
- Push changes to your repository
- Vercel will automatically redeploy
- If you change the backend URL, update the `REACT_APP_API_URL` environment variable in Vercel

## Cost Considerations

- **Vercel**: Free tier includes generous limits for personal projects
- **Render**: Free tier includes:
  - 750 hours/month (enough for one service running 24/7)
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down takes ~30-60 seconds

For production use, consider Render's paid plans for always-on services.

## Security Notes

1. **MongoDB URI**: Never commit your MongoDB connection string to the repository
2. **Environment Variables**: Always use environment variables for sensitive data
3. **CORS**: The backend allows all origins (`*`). For production, consider restricting to your frontend domain

## Next Steps

After successful deployment:
1. Test all features (monitoring, backups, uploads)
2. Monitor logs for any errors
3. Set up custom domains (optional)
4. Configure MongoDB Atlas IP whitelist if needed

