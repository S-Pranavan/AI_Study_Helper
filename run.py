#!/usr/bin/env python3
"""
AI Study Helper - Run Script
Simple script to start the Flask application
"""

from app import app, init_db

if __name__ == '__main__':
    print("🚀 Starting AI Study Helper...")
    print("📚 Initializing database...")
    init_db()
    print("📚 Database initialized successfully!")
    print("📚 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)



