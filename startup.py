#!/usr/bin/env python3
"""
Startup script for Azure App Service
This file is used to start the Flask application in production
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the Flask app
from app import app, init_db

if __name__ == "__main__":
    # Initialize database
    print("📚 Initializing database...")
    init_db()
    print("📚 Database initialized successfully!")
    
    # Get port from environment variable (Azure requirement)
    port = int(os.environ.get('PORT', 5000))
    
    # Start the application
    print(f"🚀 Starting AI Study Helper on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
