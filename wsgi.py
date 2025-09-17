#!/usr/bin/env python3
"""
WSGI Entry Point for GPS Danger Zone Tracker
Render deployment configuration
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set environment variables for production
os.environ.setdefault('APP_DEBUG', 'false')
os.environ.setdefault('APP_LOG_LEVEL', 'INFO')
os.environ.setdefault('WEB_HOST', '0.0.0.0')
os.environ.setdefault('WEB_PORT', str(os.getenv('PORT', '10000')))

from web.app import create_web_app
from utils.config_manager import ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.load_config()

# Create Flask application
application = create_web_app(config)
app = application

if __name__ == "__main__":
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)