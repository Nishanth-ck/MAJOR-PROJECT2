# File Protector - Split Deployment

This project has been split into two separate parts for deployment:
- **Frontend**: React app deployed on Vercel
- **Backend**: Python Flask API deployed on Render

## Project Structure

```
MAJOR-PROJECT2/
├── frontend/          # React frontend (Vercel)
│   ├── src/
│   ├── package.json
│   └── .env.example
├── backend/          # Flask backend (Render)
│   ├── api.py
│   ├── app.py
│   ├── requirements.txt
│   ├── Procfile
│   └── render.yaml
└── api/              # Old Vercel serverless functions (can be removed)
```

## Frontend Deployment (Vercel)

1. **Set Environment Variable**:
   - In Vercel dashboard, go to your project settings
   - Add environment variable: `REACT_APP_API_URL` = `https://your-backend.onrender.com`
   - Make sure to include the full URL without trailing slash

2. **Deploy**:
   - Connect your repository to Vercel
   - Set root directory to `frontend` (or use the vercel.json configuration)
   - Vercel will automatically build and deploy

## Backend Deployment (Render)

1. **Create a new Web Service on Render**:
   - Connect your repository
   - Set root directory to `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`

2. **Set Environment Variables**:
   - `MONGO_URI`: Your MongoDB connection string
   - `DB_NAME`: Database name (default: `file_backups`)
   - `PORT`: Port number (Render sets this automatically, but you can set it to 10000)

3. **Deploy**:
   - Render will automatically deploy when you push to your repository
   - Note the backend URL (e.g., `https://your-backend.onrender.com`)

## Configuration

### Frontend Environment Variables

Create a `.env` file in the `frontend` directory (or set in Vercel):

```env
REACT_APP_API_URL=https://your-backend.onrender.com
```

### Backend Environment Variables

Set in Render dashboard:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=file_backups
PORT=10000
```

## API Endpoints

All API endpoints are prefixed with `/api`:

- `GET /api/state` - Get current state
- `POST /api/state` - Update state
- `GET /api/status` - Get system status
- `GET /api/logs` - Get logs
- `POST /api/monitoring/start` - Start monitoring
- `POST /api/monitoring/stop` - Stop monitoring
- `POST /api/upload` - Manual upload to cloud
- `GET /api/backups/local` - Get local backups
- `GET /api/backups/cloud` - Get cloud backups
- `POST /api/backups/cloud/download` - Download from cloud
- `POST /api/backups/local/delete` - Delete local backup
- `POST /api/backups/cloud/delete` - Delete cloud backup
- `POST /api/folders/validate` - Validate folder path

## Development

### Frontend (Local)

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000` and will use relative API paths (which will fail unless you have a proxy or backend running).

### Backend (Local)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`.

For local development, you can set `REACT_APP_API_URL=http://localhost:5000` in the frontend `.env` file.

## Notes

- The `api/` folder contains old Vercel serverless functions that are no longer used
- The frontend now uses environment variables to configure the backend URL
- CORS is enabled on the backend to allow requests from the frontend domain
- Make sure to update the `REACT_APP_API_URL` in Vercel after deploying the backend to Render
