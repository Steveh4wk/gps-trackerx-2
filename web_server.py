#!/usr/bin/env python3
"""
Standalone Web Server for GPS Danger Zone Tracker

Runs a web dashboard to monitor and manage the GPS tracking system.
"""

import json
import math
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from pathlib import Path

# Initialize Flask app
app = Flask(__name__, 
            template_folder='src/web/templates',
            static_folder='src/web/static')
app.config['SECRET_KEY'] = 'gps_tracker_secret_key_2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to store current state
current_location = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'accuracy': 5.0,
    'speed': 0.0,
    'timestamp': datetime.now().isoformat()
}

# Simulation variables
simulation_step = 0
simulation_running = False

def load_zones():
    """Load zones from configuration file."""
    try:
        zones_file = Path('config/zones.json')
        if zones_file.exists():
            with open(zones_file, 'r') as f:
                zones_config = json.load(f)
                return zones_config.get('danger_zones', [])
    except Exception as e:
        print(f"Error loading zones: {e}")
    
    # Return default zones if loading fails
    return [
        {
            "id": "zone_001",
            "name": "Construction Site Alpha",
            "description": "Active construction zone with heavy machinery",
            "type": "construction",
            "geometry": {
                "type": "circle",
                "center": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "radius": 150
            },
            "severity": "high",
            "active": True
        }
    ]

def simulate_gps_movement():
    """Simulate GPS movement for demonstration."""
    global simulation_step, current_location
    
    # Base location (NYC area)
    base_lat = 40.7128
    base_lon = -74.0060
    
    # Create circular movement pattern
    radius = 0.01  # About 1km radius
    angle = (simulation_step * 0.05) % (2 * math.pi)
    
    lat = base_lat + radius * math.cos(angle) + random.uniform(-0.001, 0.001)
    lon = base_lon + radius * math.sin(angle) + random.uniform(-0.001, 0.001)
    
    current_location = {
        'latitude': lat,
        'longitude': lon,
        'altitude': 10.0 + random.uniform(-5, 15),
        'speed': 5.0 + random.uniform(-2, 5),  # m/s
        'heading': math.degrees(angle),
        'timestamp': datetime.now().isoformat(),
        'accuracy': 3.0 + random.uniform(0, 2),
        'source': 'simulation'
    }
    
    simulation_step += 1
    
    # Emit location update to all connected clients
    socketio.emit('location_update', current_location)

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status."""
    return jsonify({
        'status': 'running',
        'gps_connected': True,
        'zones_loaded': True,
        'alerts_enabled': True,
        'simulation_running': simulation_running
    })

@app.route('/api/location')
def get_current_location():
    """Get current GPS location."""
    return jsonify(current_location)

@app.route('/api/zones')
def get_zones():
    """Get all danger zones."""
    zones = load_zones()
    return jsonify({
        'zones': zones,
        'count': len(zones)
    })

@app.route('/api/zones', methods=['POST'])
def add_zone():
    """Add a new danger zone."""
    try:
        data = request.get_json()
        
        # Create new zone
        new_zone = {
            'id': f"zone_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': data['name'],
            'description': data.get('description', ''),
            'type': data['type'],
            'geometry': {
                'type': 'circle',
                'center': {
                    'latitude': data['latitude'],
                    'longitude': data['longitude']
                },
                'radius': data['radius']
            },
            'severity': data['severity'],
            'active': True,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'alerts': {
                'entry': True,
                'exit': False,
                'proximity': 50
            }
        }
        
        # Load current zones
        zones_file = Path('config/zones.json')
        if zones_file.exists():
            with open(zones_file, 'r') as f:
                zones_config = json.load(f)
        else:
            zones_config = {'danger_zones': []}
        
        # Add new zone
        zones_config['danger_zones'].append(new_zone)
        
        # Save updated zones
        with open(zones_file, 'w') as f:
            json.dump(zones_config, f, indent=2)
        
        return jsonify({'success': True, 'zone': new_zone})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/zones/<zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    """Delete a danger zone."""
    try:
        zones_file = Path('config/zones.json')
        if zones_file.exists():
            with open(zones_file, 'r') as f:
                zones_config = json.load(f)
            
            # Remove zone
            original_count = len(zones_config['danger_zones'])
            zones_config['danger_zones'] = [
                zone for zone in zones_config['danger_zones'] 
                if zone.get('id') != zone_id
            ]
            
            if len(zones_config['danger_zones']) < original_count:
                # Save updated zones
                with open(zones_file, 'w') as f:
                    json.dump(zones_config, f, indent=2)
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Zone not found'})
        else:
            return jsonify({'success': False, 'message': 'Zones file not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts."""
    # Mock alerts for demonstration
    sample_alerts = [
        {
            'timestamp': datetime.now().isoformat(),
            'zone_name': 'Construction Site Alpha',
            'severity': 'high',
            'message': 'Entered danger zone'
        }
    ]
    
    return jsonify({
        'alerts': sample_alerts,
        'count': len(sample_alerts)
    })

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f'Client connected: {request.sid}')
    # Send current location immediately
    socketio.emit('location_update', current_location)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f'Client disconnected: {request.sid}')

@socketio.on('start_simulation')
def handle_start_simulation():
    """Start GPS simulation."""
    global simulation_running
    simulation_running = True
    print("GPS simulation started")

@socketio.on('stop_simulation')
def handle_stop_simulation():
    """Stop GPS simulation."""
    global simulation_running
    simulation_running = False
    print("GPS simulation stopped")

def start_background_simulation():
    """Start background GPS simulation."""
    global simulation_running
    simulation_running = True
    
    def simulate():
        while simulation_running:
            simulate_gps_movement()
            socketio.sleep(2)  # Update every 2 seconds
    
    socketio.start_background_task(simulate)

if __name__ == '__main__':
    import os
    
    # Get port from environment variable (Render uses this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("🛰️ Starting GPS Danger Zone Tracker Web Dashboard")
    print(f"📊 Dashboard will be available at: http://localhost:{port}")
    print("🗺️  Features available:")
    print("   - Live GPS simulation")
    print("   - Interactive map with danger zones")
    print("   - Zone management")
    print("   - Real-time alerts")
    print("   - System monitoring")
    print()
    
    # Start background simulation
    start_background_simulation()
    
    # Run the web server
    is_production = os.environ.get('RENDER')
    socketio.run(app, debug=not is_production, host='0.0.0.0', port=port)
