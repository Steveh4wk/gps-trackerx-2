"""
Zone Manager Module

Manages danger zones and checks if GPS locations fall within them.
"""

import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from utils.config_manager import ConfigManager


class ZoneManager:
    """Manages danger zones and location checking."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the zone manager.
        
        Args:
            config: Zone configuration dictionary
        """
        self.config = config
        self.check_interval = config.get('check_interval', 5.0)
        self.buffer_distance = config.get('buffer_distance', 10.0)
        self.units = config.get('units', 'meters')
        
        # Load zones configuration
        config_manager = ConfigManager()
        self.zones_config = config_manager.load_zones_config()
        self.active_zones = self._load_active_zones()
        
        # Track current zone status
        self.current_zones = []
        self.zone_history = []
    
    def check_location(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Check if location falls within any danger zones.
        
        Args:
            location: GPS location dictionary
            
        Returns:
            Dictionary with zone status information
        """
        if not location:
            return {'in_danger_zone': False, 'zones': []}
        
        lat = location.get('latitude')
        lon = location.get('longitude')
        
        if lat is None or lon is None:
            return {'in_danger_zone': False, 'zones': []}
        
        # Check each active zone
        triggered_zones = []
        proximity_zones = []
        
        for zone in self.active_zones:
            if not self._is_zone_active(zone):
                continue
                
            distance = self._calculate_distance_to_zone(lat, lon, zone)
            
            if distance <= 0:  # Inside zone
                triggered_zones.append({
                    'zone': zone,
                    'distance': 0,
                    'status': 'inside'
                })
            elif distance <= zone.get('alerts', {}).get('proximity', 50):
                proximity_zones.append({
                    'zone': zone,
                    'distance': distance,
                    'status': 'proximity'
                })
        
        # Update zone history
        self._update_zone_history(triggered_zones, proximity_zones, location)
        
        return {
            'in_danger_zone': len(triggered_zones) > 0,
            'zones': triggered_zones,
            'proximity_zones': proximity_zones,
            'timestamp': datetime.now().isoformat()
        }
    
    def add_zone(self, zone_data: Dict[str, Any]) -> bool:
        """Add a new danger zone.
        
        Args:
            zone_data: Zone configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate zone data
            if not self._validate_zone_data(zone_data):
                return False
            
            # Add to zones configuration
            self.zones_config['danger_zones'].append(zone_data)
            
            # Save updated configuration
            config_manager = ConfigManager()
            config_manager.save_zones_config(self.zones_config)
            
            # Reload active zones
            self.active_zones = self._load_active_zones()
            
            return True
            
        except Exception as e:
            print(f"Error adding zone: {e}")
            return False
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove a danger zone by ID.
        
        Args:
            zone_id: ID of the zone to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find and remove zone
            zones = self.zones_config['danger_zones']
            self.zones_config['danger_zones'] = [z for z in zones if z.get('id') != zone_id]
            
            # Save updated configuration
            config_manager = ConfigManager()
            config_manager.save_zones_config(self.zones_config)
            
            # Reload active zones
            self.active_zones = self._load_active_zones()
            
            return True
            
        except Exception as e:
            print(f"Error removing zone: {e}")
            return False
    
    def get_zone_by_id(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get a zone by its ID.
        
        Args:
            zone_id: ID of the zone
            
        Returns:
            Zone dictionary or None if not found
        """
        for zone in self.zones_config.get('danger_zones', []):
            if zone.get('id') == zone_id:
                return zone
        return None
    
    def get_all_zones(self) -> List[Dict[str, Any]]:
        """Get all configured zones.
        
        Returns:
            List of zone dictionaries
        """
        return self.zones_config.get('danger_zones', [])
    
    def _load_active_zones(self) -> List[Dict[str, Any]]:
        """Load all active zones from configuration.
        
        Returns:
            List of active zone dictionaries
        """
        zones = self.zones_config.get('danger_zones', [])
        return [zone for zone in zones if zone.get('active', True)]
    
    def _is_zone_active(self, zone: Dict[str, Any]) -> bool:
        """Check if a zone is currently active based on time restrictions.
        
        Args:
            zone: Zone dictionary
            
        Returns:
            True if zone is active, False otherwise
        """
        if not zone.get('active', True):
            return False
        
        # Check time restrictions if they exist
        time_restrictions = zone.get('time_restrictions')
        if time_restrictions:
            now = datetime.now()
            active_hours = time_restrictions.get('active_hours')
            
            if active_hours:
                start_time = active_hours.get('start', '00:00')
                end_time = active_hours.get('end', '23:59')
                
                # Simple time check (could be enhanced for timezone support)
                current_time = now.strftime('%H:%M')
                if not (start_time <= current_time <= end_time):
                    return False
        
        # Check expiry date
        expiry_date = zone.get('expiry_date')
        if expiry_date:
            try:
                expiry = datetime.fromisoformat(expiry_date)
                if datetime.now() > expiry:
                    return False
            except ValueError:
                pass
        
        return True
    
    def _calculate_distance_to_zone(self, lat: float, lon: float, zone: Dict[str, Any]) -> float:
        """Calculate distance from point to zone boundary.
        
        Args:
            lat: Latitude
            lon: Longitude  
            zone: Zone dictionary
            
        Returns:
            Distance to zone boundary in meters (negative if inside)
        """
        geometry = zone.get('geometry', {})
        geom_type = geometry.get('type', 'circle')
        
        if geom_type == 'circle':
            return self._distance_to_circle(lat, lon, geometry)
        elif geom_type == 'polygon':
            return self._distance_to_polygon(lat, lon, geometry)
        else:
            return float('inf')  # Unknown geometry type
    
    def _distance_to_circle(self, lat: float, lon: float, geometry: Dict[str, Any]) -> float:
        """Calculate distance to circular zone.
        
        Args:
            lat: Point latitude
            lon: Point longitude
            geometry: Circle geometry dictionary
            
        Returns:
            Distance to circle boundary (negative if inside)
        """
        center = geometry.get('center', {})
        center_lat = center.get('latitude', 0)
        center_lon = center.get('longitude', 0)
        radius = geometry.get('radius', 100)  # meters
        
        # Calculate distance to center using Haversine formula
        distance_to_center = self._haversine_distance(lat, lon, center_lat, center_lon)
        
        # Return distance to boundary (negative if inside)
        return distance_to_center - radius
    
    def _distance_to_polygon(self, lat: float, lon: float, geometry: Dict[str, Any]) -> float:
        """Calculate distance to polygon zone.
        
        Args:
            lat: Point latitude
            lon: Point longitude
            geometry: Polygon geometry dictionary
            
        Returns:
            Distance to polygon boundary (negative if inside)
        """
        coordinates = geometry.get('coordinates', [])
        if not coordinates:
            return float('inf')
        
        # Simple point-in-polygon check
        # This is a basic implementation - could be enhanced with proper geospatial libraries
        inside = self._point_in_polygon(lat, lon, coordinates)
        
        if inside:
            return -1.0  # Inside polygon
        else:
            # Calculate distance to nearest edge (simplified)
            min_distance = float('inf')
            for i in range(len(coordinates)):
                p1 = coordinates[i]
                p2 = coordinates[(i + 1) % len(coordinates)]
                distance = self._distance_to_line_segment(lat, lon, p1[0], p1[1], p2[0], p2[1])
                min_distance = min(min_distance, distance)
            return min_distance
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _point_in_polygon(self, lat: float, lon: float, polygon: List[List[float]]) -> bool:
        """Check if point is inside polygon using ray casting algorithm.
        
        Args:
            lat, lon: Point coordinates
            polygon: List of [lat, lon] coordinates forming polygon
            
        Returns:
            True if point is inside polygon
        """
        inside = False
        j = len(polygon) - 1
        
        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            
            if ((yi > lon) != (yj > lon)) and (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
            
        return inside
    
    def _distance_to_line_segment(self, px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance from point to line segment.
        
        Args:
            px, py: Point coordinates
            x1, y1, x2, y2: Line segment endpoints
            
        Returns:
            Distance in meters (approximation)
        """
        # This is a simplified calculation
        # In a production system, you'd use proper geospatial distance calculations
        
        # Vector from line start to point
        dx1 = px - x1
        dy1 = py - y1
        
        # Vector of line segment
        dx2 = x2 - x1
        dy2 = y2 - y1
        
        # Length squared of line segment
        length_sq = dx2*dx2 + dy2*dy2
        
        if length_sq == 0:
            # Line segment is a point
            return self._haversine_distance(px, py, x1, y1)
        
        # Parameter t represents point on line segment (0 = start, 1 = end)
        t = max(0, min(1, (dx1*dx2 + dy1*dy2) / length_sq))
        
        # Closest point on line segment
        closest_x = x1 + t * dx2
        closest_y = y1 + t * dy2
        
        return self._haversine_distance(px, py, closest_x, closest_y)
    
    def _validate_zone_data(self, zone_data: Dict[str, Any]) -> bool:
        """Validate zone data structure.
        
        Args:
            zone_data: Zone configuration dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'name', 'type', 'geometry']
        
        for field in required_fields:
            if field not in zone_data:
                return False
        
        # Validate geometry
        geometry = zone_data.get('geometry', {})
        if 'type' not in geometry:
            return False
        
        geom_type = geometry['type']
        if geom_type == 'circle':
            if 'center' not in geometry or 'radius' not in geometry:
                return False
        elif geom_type == 'polygon':
            if 'coordinates' not in geometry:
                return False
        
        return True
    
    def _update_zone_history(self, triggered_zones: List, proximity_zones: List, location: Dict[str, Any]):
        """Update zone entry/exit history.
        
        Args:
            triggered_zones: List of triggered zones
            proximity_zones: List of proximity zones
            location: Current location
        """
        current_zone_ids = {zone['zone']['id'] for zone in triggered_zones}
        previous_zone_ids = {zone['id'] for zone in self.current_zones}
        
        # Check for zone entries
        entered_zones = current_zone_ids - previous_zone_ids
        for zone_id in entered_zones:
            zone = next(zone['zone'] for zone in triggered_zones if zone['zone']['id'] == zone_id)
            self.zone_history.append({
                'event': 'enter',
                'zone_id': zone_id,
                'zone_name': zone.get('name', zone_id),
                'location': location,
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for zone exits
        exited_zones = previous_zone_ids - current_zone_ids
        for zone_id in exited_zones:
            zone = next(zone for zone in self.current_zones if zone['id'] == zone_id)
            self.zone_history.append({
                'event': 'exit',
                'zone_id': zone_id,
                'zone_name': zone.get('name', zone_id),
                'location': location,
                'timestamp': datetime.now().isoformat()
            })
        
        # Update current zones
        self.current_zones = [zone['zone'] for zone in triggered_zones]
        
        # Keep history limited
        if len(self.zone_history) > 1000:
            self.zone_history = self.zone_history[-1000:]