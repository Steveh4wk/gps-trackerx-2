#!/usr/bin/env python3
"""
Start script for GPS Danger Zone Tracker on Render
"""

import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the web server
from web_server import app, socketio, start_background_simulation

if __name__ == '__main__':
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print("🛰️ GPS Danger Zone Tracker - Starting on Render")
    print(f"🌐 Port: {port}")
    print("🚀 Features: GPS Simulation, Interactive Maps, Zone Management")
    
    # Start background GPS simulation
    start_background_simulation()
    
    # Run the application
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port,
        debug=False,  # Disable debug mode in production
        allow_unsafe_werkzeug=True  # Required for Render deployment
    )
