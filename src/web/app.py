"""
Web Application for GPS Danger Zone Tracker

Provides a web interface for monitoring and managing the GPS tracker.
"""

import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from typing import Dict, Any


def create_web_app(config: Dict[str, Any]) -> Flask:
    """Create and configure the Flask web application.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    # Use secret key from config or environment
    secret_key = config.get('web_interface', {}).get('secret_key') or os.getenv('WEB_SECRET_KEY', 'gps_tracker_secret_key')
    app.config['SECRET_KEY'] = secret_key
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    web_config = config.get('web_interface', {})
    
    @app.route('/')
    def index():
        """Main dashboard page."""
        return render_template('index.html')
    
    @app.route('/api/status')
    def get_status():
        """Get current application status."""
        # This would be connected to the main application instance
        return jsonify({
            'status': 'running',
            'gps_connected': True,
            'zones_loaded': True,
            'alerts_enabled': True
        })
    
    @app.route('/api/location')
    def get_current_location():
        """Get current GPS location."""
        # Placeholder - would be connected to GPS tracker
        return jsonify({
            'latitude': 40.7128,
            'longitude': -74.0060,
            'accuracy': 5.0,
            'timestamp': '2024-01-01T12:00:00Z'
        })
    
    @app.route('/api/zones')
    def get_zones():
        """Get all danger zones."""
        # Placeholder - would be connected to zone manager
        return jsonify({
            'zones': [
                {
                    'id': 'zone_001',
                    'name': 'Construction Site Alpha',
                    'type': 'construction',
                    'active': True,
                    'severity': 'high'
                }
            ]
        })
    
    @app.route('/api/alerts')
    def get_alerts():
        """Get recent alerts."""
        # Placeholder - would be connected to alert system
        return jsonify({
            'alerts': [
                {
                    'timestamp': '2024-01-01T12:00:00Z',
                    'zone_name': 'Construction Site Alpha',
                    'severity': 'high',
                    'message': 'Entered danger zone'
                }
            ]
        })
    
    # SocketIO events for real-time updates
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print('Client disconnected')
    
    return app