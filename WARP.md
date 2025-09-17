# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The GPS Danger Zone Tracker is a Python-based safety application that monitors GPS location data and provides alerts when users enter predefined danger zones. The application supports real-time GPS tracking, zone management, and multiple alert mechanisms.

## Architecture

The application follows a modular architecture with clear separation of concerns:

### Core Components

- **Main Application** (`src/main.py`): Entry point that orchestrates all components using async/await patterns
- **GPS Tracker** (`src/tracker/gps_tracker.py`): Handles GPS data acquisition from serial ports, files, or APIs with fallback to simulation mode
- **Zone Manager** (`src/zones/zone_manager.py`): Manages danger zone definitions and performs geospatial calculations for zone entry/exit detection
- **Alert System** (`src/alerts/alert_system.py`): Handles multiple alert types (desktop, sound, email) with cooldown mechanisms
- **Configuration Manager** (`src/utils/config_manager.py`): Centralized configuration handling with fallback to example configurations
- **Web Interface** (`src/web/app.py`): Flask-based web dashboard with SocketIO for real-time updates

### Data Flow

1. GPS Tracker continuously acquires location data
2. Zone Manager checks each location against active danger zones using geospatial calculations
3. Alert System triggers notifications when zone violations are detected
4. Location history and zone events are logged for analysis
5. Web interface provides real-time monitoring dashboard

### Key Design Patterns

- **Async Architecture**: Main tracking loop uses asyncio for non-blocking operations
- **Configuration-Driven**: All behavior controlled through JSON configuration files
- **Fallback Mechanisms**: Graceful degradation from real GPS to simulation mode
- **Geospatial Support**: Handles both circular and polygonal danger zones with proper distance calculations

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration templates
cp config/config.example.json config/config.json
cp config/zones.example.json config/zones.json

# Copy environment variables template
cp .env.example .env
# Edit .env with your specific settings
```

### Running the Application
```bash
# Run main application
python src/main.py

# Run with debug logging
python -c "
import sys, os
sys.path.append('src')
os.environ['DEBUG'] = '1'
exec(open('src/main.py').read())
"
```

### Testing and Development
```bash
# Run basic functionality test
python -c "
import sys
sys.path.append('src')
from utils.config_manager import ConfigManager
cm = ConfigManager()
config = cm.load_config()
print(f'Config loaded: {config[\"app\"][\"name\"]} v{config[\"app\"][\"version\"]}')
"

# Test GPS simulation mode
python -c "
import asyncio, sys
sys.path.append('src')
from tracker.gps_tracker import GPSTracker
async def test():
    gps = GPSTracker({'source_type': 'simulation', 'update_interval': 1.0})
    await gps.start()
    await asyncio.sleep(3)
    location = await gps.get_current_location()
    print(f'Simulated location: {location}')
    await gps.stop()
asyncio.run(test())
"

# Test zone detection
python -c "
import sys
sys.path.append('src')
from zones.zone_manager import ZoneManager
zm = ZoneManager({})
test_location = {'latitude': 40.7128, 'longitude': -74.0060}
status = zm.check_location(test_location)
print(f'Zone status: {status}')
"

# Test environment variables integration
python test_env.py
```

### Configuration Management
```bash
# Validate configuration files
python -c "
import json, sys
try:
    with open('config/config.json') as f:
        config = json.load(f)
    print('Main config is valid JSON')
    print(f'App: {config[\"app\"][\"name\"]} v{config[\"app\"][\"version\"]}')
except Exception as e:
    print(f'Config error: {e}')
"

# Test environment variable integration
python -c "
import sys, os
sys.path.append('src')
from utils.config_manager import ConfigManager
cm = ConfigManager()
config = cm.load_config()
print(f'Config with env vars: {config[\"app\"][\"name\"]} v{config[\"app\"][\"version\"]}')
print(f'GPS Source: {config[\"gps\"][\"source_type\"]}')
print(f'Web Port: {config[\"web_interface\"][\"port\"]}')
print(f'Debug Mode: {config[\"app\"][\"debug\"]}')
"

# Check environment variables
python -c "
import os
from pathlib import Path
env_file = Path('.env')
if env_file.exists():
    print('Environment file found')
    # Load and show some non-sensitive variables
    from dotenv import load_dotenv
    load_dotenv()
    print(f'GPS_SOURCE_TYPE: {os.getenv(\"GPS_SOURCE_TYPE\", \"not set\")}')
    print(f'WEB_PORT: {os.getenv(\"WEB_PORT\", \"not set\")}')
    print(f'APP_DEBUG: {os.getenv(\"APP_DEBUG\", \"not set\")}')
else:
    print('No .env file found - using config files only')
"

# Check zones configuration
python -c "
import json, sys
try:
    with open('config/zones.json') as f:
        zones = json.load(f)
    active_zones = [z for z in zones.get('danger_zones', []) if z.get('active', True)]
    print(f'Found {len(active_zones)} active zones')
    for zone in active_zones[:3]:
        print(f'  - {zone[\"name\"]} ({zone[\"type\"]})')
except Exception as e:
    print(f'Zones config error: {e}')
"
```

### Data and Logging
```bash
# Check location log
python -c "
import json
from pathlib import Path
log_file = Path('data/location_log.jsonl')
if log_file.exists():
    with open(log_file) as f:
        lines = f.readlines()
    print(f'Location log has {len(lines)} entries')
    if lines:
        latest = json.loads(lines[-1])
        print(f'Latest entry: {latest[\"timestamp\"]}')
else:
    print('No location log found')
"

# View alert log
python -c "
import json
from pathlib import Path
log_file = Path('logs/alerts.log')
if log_file.exists():
    with open(log_file) as f:
        lines = f.readlines()
    print(f'Alert log has {len(lines)} entries')
    if lines:
        latest = json.loads(lines[-1])
        print(f'Latest alert: {latest[\"severity\"]} - {latest[\"timestamp\"]}')
else:
    print('No alert log found')
"
```

## Configuration Files

### Environment Variables (`.env`)
The application supports environment variable configuration for sensitive data and deployment-specific settings. Environment variables take precedence over config file values.

**Key Environment Variables:**
- **Application**: `APP_DEBUG`, `APP_LOG_LEVEL`
- **GPS**: `GPS_SOURCE_TYPE`, `GPS_SERIAL_PORT`, `GPS_API_KEY`
- **Alerts**: `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_RECIPIENTS`
- **Web**: `WEB_PORT`, `WEB_HOST`, `WEB_SECRET_KEY`
- **Database**: `DATABASE_PATH`
- **External Services**: `WEATHER_API_KEY`, `TWILIO_ACCOUNT_SID`

### Main Configuration (`config/config.json`)
- **GPS Settings**: Source type (serial/file/api/simulation), ports, update intervals
- **Zone Settings**: Check intervals, buffer distances, units
- **Alert Settings**: Enable/disable alerts, types (desktop/sound/email), cooldown periods  
- **Web Interface**: Host, port, auto-open browser settings
- **Database**: SQLite path and backup settings
- **Logging**: File paths, rotation, log levels
- **Privacy**: Location history retention, anonymization options

### Zone Configuration (`config/zones.json`)
- **Danger Zones**: Individual zone definitions with geometry (circle/polygon)
- **Zone Types**: Visual styling, default radii for different zone categories
- **Global Settings**: Auto-activation, overlap checking, maximum active zones

## Development Notes

### GPS Data Sources
The application supports multiple GPS input methods:
- **Serial**: Direct connection to GPS hardware via COM/USB ports
- **File**: Playback from GPX/KML files for testing
- **API**: Integration with external GPS services
- **Simulation**: Built-in circular movement pattern for development

### Geospatial Calculations
- Uses Haversine formula for accurate distance calculations
- Supports circular zones (center + radius) and polygonal zones (coordinate arrays)
- Implements point-in-polygon detection using ray casting algorithm
- Buffer distances prevent alert spam near zone boundaries

### Alert System
- Multiple concurrent alert mechanisms (desktop notifications, sounds, email)
- Configurable cooldown periods prevent notification spam
- Severity-based message formatting and routing
- Persistent alert history with statistics

### Error Handling
- Graceful fallback from hardware GPS to simulation mode
- Configuration validation with fallback to example files
- Exception handling in tracking loops with automatic retry
- Logging of errors and status messages

### Performance Considerations
- Async architecture prevents blocking operations
- Limited in-memory history (1000 records) to prevent memory leaks
- Periodic file logging with configurable intervals
- Efficient geospatial calculations with early exit conditions