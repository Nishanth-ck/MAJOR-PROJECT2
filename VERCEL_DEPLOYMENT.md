# Vercel Deployment Guide

This guide will help you deploy your File Protector application to Vercel.

## Prerequisites

1. A GitHub account with your code pushed to a repository
2. A Vercel account (sign up at https://vercel.com)
3. MongoDB Atlas connection string (for cloud backups)

## Deployment Steps

### 1. Connect Your Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository (`Nishanth-ck/MAJOR-PROJECT2`)
4. Vercel will automatically detect the project settings

### 2. Configure Environment Variables

1. In your Vercel project settings, go to **Settings > Environment Variables**
2. Add the following variables:
   - `MONGO_URI`: Your MongoDB Atlas connection string
     - Example: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0`
   - `DB_NAME`: Database name (default: `file_backups`)

### 3. Configure Build Settings

Vercel should automatically detect:
- **Framework Preset**: Other (or React)
- **Root Directory**: Leave as root (`.`)
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/build`
- **Install Command**: `cd frontend && npm install`

### 4. Deploy

1. Click "Deploy" button
2. Wait for the build to complete
3. Your app will be live at `https://your-project.vercel.app`

## Project Structure

```
.
├── api/                    # Vercel serverless functions
│   ├── state/
│   ├── status/
│   ├── logs/
│   ├── backups/
│   └── helpers.py
├── frontend/               # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                # Original Flask backend (for local dev)
├── vercel.json            # Vercel configuration
└── .env.example           # Environment variables template
```

## API Endpoints

All API endpoints are available at `/api/*`:

- `GET /api/state` - Get current state
- `POST /api/state` - Update state
- `GET /api/status` - Get system status
- `GET /api/logs` - Get recent logs
- `GET /api/backups/cloud` - Get cloud backups
- `GET /api/backups/local` - Get local backups (not available in serverless)

## Important Notes

### Limitations in Serverless Environment

1. **File System Access**: Vercel serverless functions don't have persistent file system access. Local file monitoring and backups won't work in the deployed version.

2. **State Persistence**: The current implementation uses in-memory state storage. For production, consider using:
   - MongoDB for state storage
   - Vercel KV (Redis) for state
   - External database

3. **File Monitoring**: Real-time file monitoring requires a persistent server. Consider:
   - Running the monitoring service separately
   - Using a cloud service (AWS Lambda, Google Cloud Functions)
   - Using a dedicated server for file monitoring

### What Works in Vercel

✅ Cloud backup management (MongoDB)
✅ State management (in-memory)
✅ API endpoints
✅ Frontend React application
✅ Logs viewing

### What Doesn't Work in Vercel

❌ Local file system monitoring
❌ Local file backups
❌ Persistent file storage
❌ Long-running processes

## Local Development

For local development with full file system access:

1. Run the Flask backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   python api.py
   ```

2. Run the React frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Troubleshooting

### Build Fails

- Check that all dependencies are in `frontend/package.json`
- Ensure Node.js version is compatible (Vercel uses Node 18+ by default)

### API Endpoints Return 500

- Check environment variables are set correctly
- Verify MongoDB connection string is valid
- Check Vercel function logs in the dashboard

### CORS Errors

- All API functions include CORS headers
- If issues persist, check the `Access-Control-Allow-Origin` header in function responses

## Next Steps

1. Set up MongoDB Atlas for cloud backups
2. Configure environment variables in Vercel
3. Deploy and test the application
4. Consider adding authentication for production use
5. Implement persistent state storage (database)

## Support

For issues or questions:
- Check Vercel logs in the dashboard
- Review API function logs
- Check MongoDB connection status

