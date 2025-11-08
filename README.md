# File Protector - Split Deployment

This project has been split into two separate parts for deployment:
- **Frontend**: React app deployed on Vercel
- **Backend**: Python Flask API deployed on Render
- **Desktop Client**: Local application required for file monitoring (see [DESKTOP_CLIENT_GUIDE.md](DESKTOP_CLIENT_GUIDE.md))

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
├── api/              # Vercel serverless functions
└── desktop_client/   # Desktop client for local file monitoring
    ├── client.py
    ├── requirements.txt
    ├── install.bat
    ├── install.sh
    └── README.md
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
- `POST /api/client/heartbeat` - Client heartbeat (desktop client)
- `POST /api/client/state` - Sync client state (desktop client)

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

## Desktop Client (Required for File Monitoring)

**Important:** The web application cannot directly access your local file system. To enable file monitoring and cloud backup features, you must install and run the desktop client.

### Quick Start

1. Navigate to the `desktop_client` folder
2. Run the installer:
   - **Windows:** `install.bat`
   - **macOS/Linux:** `./install.sh`
3. Edit `client.py` and set `API_BASE_URL` to your deployed website URL
4. Run the client:
   - **Windows:** `python client.py`
   - **macOS/Linux:** `python3 client.py`
5. Verify connection in the web interface (Dashboard → Client status)

For detailed instructions, see [DESKTOP_CLIENT_GUIDE.md](DESKTOP_CLIENT_GUIDE.md)

### Why Desktop Client?

- Web browsers cannot access local file systems (security restriction)
- The deployed backend is serverless and has no file system access
- The desktop client runs locally and bridges the gap between your computer and the web app

## Notes

- The `api/` folder contains Vercel serverless functions for the deployed backend
- The frontend now uses environment variables to configure the backend URL
- CORS is enabled on the backend to allow requests from the frontend domain
- Make sure to update the `REACT_APP_API_URL` in Vercel after deploying the backend to Render
- **Desktop client must be running for file monitoring and cloud upload features to work**
