# Quick Start Deployment Guide

## Deployment Plan Overview

1. **Deploy Backend First** (Render) - Get the backend URL
2. **Deploy Frontend Second** (Vercel) - Connect it to the backend URL

---

## Step 1: Deploy Backend to Render (5-10 minutes)

### 1.1 Create Render Account
- Go to https://render.com
- Sign up with GitHub (recommended) or email

### 1.2 Create New Web Service
1. Click **"New +"** button → Select **"Web Service"**
2. Connect your GitHub repository:
   - Click **"Connect account"** if not connected
   - Select your repository: `MAJOR-PROJECT2`
   - Click **"Connect"**

### 1.3 Configure Backend Service
Fill in these settings:

- **Name**: `file-protector-backend` (or any name)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend` ⚠️ **IMPORTANT: Set this!**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 1.4 Set Environment Variables
Click **"Advanced"** → **"Add Environment Variable"** and add:

```
MONGO_URI = mongodb+srv://nishanthck09072004_db_user:b9hoRGMqNCbGSK98@cluster0.yyhfish.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

```
DB_NAME = file_backups
```

```
PORT = 10000
```

### 1.5 Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. **Copy the service URL** (looks like: `https://file-protector-backend-xxxx.onrender.com`)
   - ⚠️ **SAVE THIS URL** - You'll need it for the frontend!

### 1.6 Test Backend
- Visit: `https://your-backend-url.onrender.com/api/status`
- You should see JSON response with status information
- If it works, backend is ready! ✅

---

## Step 2: Deploy Frontend to Vercel (5-10 minutes)

### 2.1 Create Vercel Account
- Go to https://vercel.com
- Sign up with GitHub (recommended)

### 2.2 Import Project
1. Click **"Add New..."** → **"Project"**
2. Import from GitHub:
   - Select your repository: `MAJOR-PROJECT2`
   - Click **"Import"**

### 2.3 Configure Frontend Project
Vercel should auto-detect React. Verify:

- **Framework Preset**: `Create React App` (auto-detected)
- **Root Directory**: Leave empty (or set to `frontend` if needed)
- **Build Command**: `cd frontend && npm run build` (auto-set)
- **Output Directory**: `frontend/build` (auto-set)

### 2.4 Set Environment Variable
**BEFORE DEPLOYING**, click **"Environment Variables"** and add:

```
REACT_APP_API_URL = https://your-backend-url.onrender.com
```

⚠️ **Replace `your-backend-url.onrender.com` with your actual Render backend URL!**
⚠️ **NO trailing slash!**

Example:
```
REACT_APP_API_URL = https://file-protector-backend-xxxx.onrender.com
```

### 2.5 Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes for build and deployment
3. Vercel will give you a URL (e.g., `https://your-project.vercel.app`)

### 2.6 Test Frontend
1. Visit your Vercel URL
2. Open browser console (F12)
3. Check for errors:
   - ✅ No CORS errors = Good!
   - ✅ API calls working = Perfect!
   - ❌ CORS errors = Check backend URL
   - ❌ 404 errors = Check environment variable

---

## Step 3: Verify Everything Works

### Test Checklist:
- [ ] Backend accessible at `/api/status`
- [ ] Frontend loads without errors
- [ ] Dashboard shows data from backend
- [ ] Settings page works
- [ ] Backups page loads
- [ ] Logs page loads

---

## Troubleshooting

### Backend Issues

**Problem**: Build fails
- **Check**: Render logs for error messages
- **Common fix**: Ensure `requirements.txt` has all dependencies

**Problem**: Service won't start
- **Check**: Start command is `gunicorn app:app`
- **Check**: `app.py` exists in `backend/` folder

**Problem**: MongoDB connection fails
- **Check**: `MONGO_URI` environment variable is set correctly
- **Check**: MongoDB Atlas allows connections from anywhere (0.0.0.0/0)

**Problem**: First request is slow (30-60 seconds)
- **Normal**: Render free tier spins down after 15 min inactivity
- **Solution**: First request wakes it up (takes time)

### Frontend Issues

**Problem**: API calls fail with CORS error
- **Fix**: Backend already has CORS enabled
- **Check**: `REACT_APP_API_URL` is set correctly in Vercel

**Problem**: API calls return 404
- **Check**: Backend URL is correct (no trailing slash)
- **Check**: Backend is deployed and running
- **Test**: Visit `https://your-backend.onrender.com/api/status` directly

**Problem**: Environment variable not working
- **Check**: Variable name is exactly `REACT_APP_API_URL`
- **Check**: No trailing slash in the URL
- **Fix**: Redeploy after changing environment variables

---

## Important Notes

### Render Free Tier Limitations:
- ⚠️ Services spin down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes 30-60 seconds
- ⚠️ 750 hours/month free (enough for one service 24/7)

### Vercel Free Tier:
- ✅ Generous limits for personal projects
- ✅ Automatic deployments on git push
- ✅ Fast CDN

### Security:
- 🔒 Never commit MongoDB URI to GitHub
- 🔒 Use environment variables for all secrets
- 🔒 Backend CORS allows all origins (consider restricting for production)

---

## Updating Your Deployment

### Update Backend:
1. Make changes to `backend/` files
2. Push to GitHub
3. Render auto-deploys (or manually trigger in dashboard)

### Update Frontend:
1. Make changes to `frontend/` files
2. Push to GitHub
3. Vercel auto-deploys

### Change Backend URL:
1. Update `REACT_APP_API_URL` in Vercel environment variables
2. Redeploy frontend (or push a commit)

---

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Monitor logs for errors
3. ✅ Set up custom domains (optional)
4. ✅ Configure MongoDB Atlas IP whitelist if needed
5. ✅ Consider upgrading to paid plans for production use

---

## Quick Reference

### Backend URL Format:
```
https://your-service-name.onrender.com
```

### Frontend Environment Variable:
```
REACT_APP_API_URL=https://your-service-name.onrender.com
```

### Test Backend:
```
https://your-service-name.onrender.com/api/status
```

### Test Frontend:
```
https://your-project.vercel.app
```

---

**Need Help?** Check the full `DEPLOYMENT.md` for detailed troubleshooting!

