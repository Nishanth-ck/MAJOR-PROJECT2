# Entry point for Render deployment
# This file imports the Flask app from api.py
from api import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

