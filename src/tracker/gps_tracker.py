"""
GPS Tracker Module

Handles GPS data acquisition from various sources (serial, file, API).
"""

import asyncio
import json
import serial
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class GPSTracker:
    """Main GPS tracking class that handles location data acquisition."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the GPS tracker.
        
        Args:
            config: GPS configuration dictionary
        """
        self.config = config
        self.source_type = config.get('source_type', 'serial')
        self.update_interval = config.get('update_interval', 1.0)
        self.running = False
        
        # Initialize based on source type
        self.serial_port = None
        self.current_location = None
        self.location_history = []
        
        # Database/logging setup
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    async def start(self):
        """Start the GPS tracking based on configured source."""
        self.running = True
        
        if self.source_type == 'serial':
            await self._start_serial_tracking()
        elif self.source_type == 'file':
            await self._start_file_tracking()
        elif self.source_type == 'api':
            await self._start_api_tracking()
        else:
            # Default to simulation mode for testing
            await self._start_simulation_tracking()
    
    async def stop(self):
        """Stop GPS tracking and cleanup resources."""
        self.running = False
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
    
    async def get_current_location(self) -> Optional[Dict[str, Any]]:
        """Get the current GPS location.
        
        Returns:
            Dictionary with location data or None if unavailable
        """
        return self.current_location
    
    def log_location(self, location: Dict[str, Any], zone_status: Dict[str, Any]):
        """Log location data to file.
        
        Args:
            location: Location dictionary
            zone_status: Zone status information
        """
        if not location:
            return
            
        # Add to in-memory history
        self.location_history.append({
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'zone_status': zone_status
        })
        
        # Keep history limited to prevent memory issues
        if len(self.location_history) > 1000:
            self.location_history = self.location_history[-1000:]
        
        # Write to file periodically or based on configuration
        self._write_location_log(location, zone_status)
    
    async def _start_serial_tracking(self):
        """Start tracking GPS data from serial port."""
        try:
            port = self.config.get('serial_port', 'COM3')
            baud_rate = self.config.get('baud_rate', 9600)
            timeout = self.config.get('timeout', 1)
            
            self.serial_port = serial.Serial(port, baud_rate, timeout=timeout)
            
            while self.running:
                try:
                    if self.serial_port.in_waiting > 0:
                        nmea_sentence = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                        location = self._parse_nmea(nmea_sentence)
                        if location:
                            self.current_location = location
                    
                    await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
                    
                except Exception as e:
                    print(f"Error reading from serial port: {e}")
                    await asyncio.sleep(1.0)
                    
        except Exception as e:
            print(f"Failed to open serial port: {e}")
            # Fall back to simulation mode
            await self._start_simulation_tracking()
    
    async def _start_file_tracking(self):
        """Start tracking GPS data from file (GPX, KML, etc.)."""
        file_path = self.config.get('file_path', 'data/sample_track.gpx')
        
        # This is a placeholder implementation
        # In a real implementation, you'd parse GPX/KML files
        await self._start_simulation_tracking()
    
    async def _start_api_tracking(self):
        """Start tracking GPS data from API source."""
        api_url = self.config.get('api_url', '')
        
        # This is a placeholder implementation
        # In a real implementation, you'd connect to a GPS API
        await self._start_simulation_tracking()
    
    async def _start_simulation_tracking(self):
        """Start simulation tracking for testing purposes."""
        # Simulate movement around New York City area
        base_lat = 40.7128
        base_lon = -74.0060
        
        step = 0
        while self.running:
            # Simulate GPS movement in a circular pattern
            import math
            radius = 0.01  # About 1km radius
            angle = (step * 0.1) % (2 * math.pi)
            
            lat = base_lat + radius * math.cos(angle)
            lon = base_lon + radius * math.sin(angle)
            
            self.current_location = {
                'latitude': lat,
                'longitude': lon,
                'altitude': 10.0,
                'speed': 5.0,  # m/s
                'heading': math.degrees(angle),
                'timestamp': datetime.now().isoformat(),
                'accuracy': 3.0,  # meters
                'source': 'simulation'
            }
            
            step += 1
            await asyncio.sleep(self.update_interval)
    
    def _parse_nmea(self, sentence: str) -> Optional[Dict[str, Any]]:
        """Parse NMEA sentence to extract GPS data.
        
        Args:
            sentence: NMEA sentence string
            
        Returns:
            Dictionary with GPS data or None if invalid
        """
        if not sentence.startswith('$'):
            return None
        
        parts = sentence.split(',')
        
        # Handle GPGGA sentences (Global Positioning System Fix Data)
        if parts[0] == '$GPGGA':
            try:
                if len(parts) >= 15 and parts[2] and parts[4]:
                    # Extract latitude
                    lat_raw = float(parts[2])
                    lat_deg = int(lat_raw / 100)
                    lat_min = lat_raw - (lat_deg * 100)
                    lat = lat_deg + lat_min / 60.0
                    if parts[3] == 'S':
                        lat = -lat
                    
                    # Extract longitude
                    lon_raw = float(parts[4])
                    lon_deg = int(lon_raw / 100)
                    lon_min = lon_raw - (lon_deg * 100)
                    lon = lon_deg + lon_min / 60.0
                    if parts[5] == 'W':
                        lon = -lon
                    
                    # Extract other data
                    altitude = float(parts[9]) if parts[9] else 0.0
                    
                    return {
                        'latitude': lat,
                        'longitude': lon,
                        'altitude': altitude,
                        'timestamp': datetime.now().isoformat(),
                        'accuracy': 5.0,  # Default accuracy
                        'source': 'nmea'
                    }
            except (ValueError, IndexError):
                pass
        
        return None
    
    def _write_location_log(self, location: Dict[str, Any], zone_status: Dict[str, Any]):
        """Write location data to log file.
        
        Args:
            location: Location dictionary
            zone_status: Zone status information
        """
        log_file = self.data_dir / "location_log.jsonl"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'zone_status': zone_status
        }
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\\n')
        except Exception as e:
            print(f"Error writing to location log: {e}")
    
    def get_location_history(self, limit: int = 100) -> list:
        """Get recent location history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of location records
        """
        return self.location_history[-limit:] if self.location_history else []