"""
Configuration Manager for GPS Danger Zone Tracker

Handles loading and managing application configuration from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Union
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration files."""
    
    def __init__(self, config_dir: str = None):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Path to configuration directory. If None, uses default.
        """
        if config_dir is None:
            # Get project root directory
            self.project_root = Path(__file__).parent.parent.parent
            self.config_dir = self.project_root / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / "config.json"
        self.zones_file = self.config_dir / "zones.json"
        
        # Load environment variables from .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    
    def _get_env_var(self, key: str, default: Any = None, var_type: type = str) -> Any:
        """Get environment variable with type conversion.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            var_type: Type to convert to (str, int, float, bool)
            
        Returns:
            Environment variable value converted to specified type
        """
        value = os.environ.get(key, default)
        
        if value is None or value == default:
            return default
            
        # Convert string to appropriate type
        if var_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif var_type == float:
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        elif var_type == list:
            if isinstance(value, str):
                return [item.strip() for item in value.split(',') if item.strip()]
            return value if isinstance(value, list) else default
        else:
            return str(value)
    
    def _merge_env_with_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge environment variables with configuration.
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Configuration with environment variables applied
        """
        # Create a deep copy to avoid modifying original
        import copy
        merged_config = copy.deepcopy(config)
        
        # Application settings
        merged_config['app']['name'] = self._get_env_var('APP_NAME', config['app']['name'])
        merged_config['app']['version'] = self._get_env_var('APP_VERSION', config['app']['version'])
        merged_config['app']['debug'] = self._get_env_var('APP_DEBUG', config['app']['debug'], bool)
        merged_config['app']['log_level'] = self._get_env_var('APP_LOG_LEVEL', config['app']['log_level'])
        
        # GPS settings
        merged_config['gps']['source_type'] = self._get_env_var('GPS_SOURCE_TYPE', config['gps']['source_type'])
        merged_config['gps']['serial_port'] = self._get_env_var('GPS_SERIAL_PORT', config['gps'].get('serial_port', 'COM3'))
        merged_config['gps']['baud_rate'] = self._get_env_var('GPS_BAUD_RATE', config['gps'].get('baud_rate', 9600), int)
        merged_config['gps']['timeout'] = self._get_env_var('GPS_TIMEOUT', config['gps'].get('timeout', 1), int)
        merged_config['gps']['update_interval'] = self._get_env_var('GPS_UPDATE_INTERVAL', config['gps']['update_interval'], float)
        merged_config['gps']['file_path'] = self._get_env_var('GPS_FILE_PATH', config['gps'].get('file_path', 'data/sample_track.gpx'))
        merged_config['gps']['api_url'] = self._get_env_var('GPS_API_URL', config['gps'].get('api_url', ''))
        merged_config['gps']['api_key'] = self._get_env_var('GPS_API_KEY', config['gps'].get('api_key', ''))
        
        # Zone settings
        merged_config['zones']['check_interval'] = self._get_env_var('ZONES_CHECK_INTERVAL', config['zones']['check_interval'], float)
        merged_config['zones']['buffer_distance'] = self._get_env_var('ZONES_BUFFER_DISTANCE', config['zones']['buffer_distance'], float)
        merged_config['zones']['units'] = self._get_env_var('ZONES_UNITS', config['zones']['units'])
        merged_config['zones']['default_radius'] = self._get_env_var('ZONES_DEFAULT_RADIUS', config['zones'].get('default_radius', 100.0), float)
        
        # Alert settings
        merged_config['alerts']['enabled'] = self._get_env_var('ALERTS_ENABLED', config['alerts']['enabled'], bool)
        merged_config['alerts']['types'] = self._get_env_var('ALERTS_TYPES', config['alerts']['types'], list)
        merged_config['alerts']['sound_file'] = self._get_env_var('ALERTS_SOUND_FILE', config['alerts'].get('sound_file', 'alerts/warning.wav'))
        merged_config['alerts']['cooldown_period'] = self._get_env_var('ALERTS_COOLDOWN_PERIOD', config['alerts'].get('cooldown_period', 60), int)
        
        # Email settings
        if 'email' not in merged_config['alerts']:
            merged_config['alerts']['email'] = {}
        merged_config['alerts']['email']['enabled'] = self._get_env_var('EMAIL_ENABLED', merged_config['alerts']['email'].get('enabled', False), bool)
        merged_config['alerts']['email']['smtp_server'] = self._get_env_var('EMAIL_SMTP_SERVER', merged_config['alerts']['email'].get('smtp_server', 'smtp.gmail.com'))
        merged_config['alerts']['email']['smtp_port'] = self._get_env_var('EMAIL_SMTP_PORT', merged_config['alerts']['email'].get('smtp_port', 587), int)
        merged_config['alerts']['email']['username'] = self._get_env_var('EMAIL_USERNAME', merged_config['alerts']['email'].get('username', ''))
        merged_config['alerts']['email']['password'] = self._get_env_var('EMAIL_PASSWORD', merged_config['alerts']['email'].get('password', ''))
        recipients = self._get_env_var('EMAIL_RECIPIENTS', merged_config['alerts']['email'].get('recipients', []), list)
        merged_config['alerts']['email']['recipients'] = recipients
        
        # Database settings
        merged_config['database']['type'] = self._get_env_var('DATABASE_TYPE', config['database']['type'])
        merged_config['database']['path'] = self._get_env_var('DATABASE_PATH', config['database']['path'])
        merged_config['database']['backup_interval'] = self._get_env_var('DATABASE_BACKUP_INTERVAL', config['database'].get('backup_interval', 3600), int)
        
        # Web interface settings
        merged_config['web_interface']['enabled'] = self._get_env_var('WEB_ENABLED', config['web_interface']['enabled'], bool)
        merged_config['web_interface']['host'] = self._get_env_var('WEB_HOST', config['web_interface']['host'])
        merged_config['web_interface']['port'] = self._get_env_var('WEB_PORT', config['web_interface']['port'], int)
        merged_config['web_interface']['auto_open_browser'] = self._get_env_var('WEB_AUTO_OPEN_BROWSER', config['web_interface'].get('auto_open_browser', True), bool)
        
        # Add secret key for Flask
        merged_config['web_interface']['secret_key'] = self._get_env_var('WEB_SECRET_KEY', 'gps_tracker_secret_key')
        
        # Mapping settings
        if 'mapping' not in merged_config:
            merged_config['mapping'] = {}
        merged_config['mapping']['default_zoom'] = self._get_env_var('MAP_DEFAULT_ZOOM', merged_config['mapping'].get('default_zoom', 15), int)
        merged_config['mapping']['tile_source'] = self._get_env_var('MAP_TILE_SOURCE', merged_config['mapping'].get('tile_source', 'OpenStreetMap'))
        merged_config['mapping']['cache_tiles'] = self._get_env_var('MAP_CACHE_TILES', merged_config['mapping'].get('cache_tiles', True), bool)
        merged_config['mapping']['offline_mode'] = self._get_env_var('MAP_OFFLINE_MODE', merged_config['mapping'].get('offline_mode', False), bool)
        
        # Logging settings
        merged_config['logging']['file'] = self._get_env_var('LOG_FILE', config['logging']['file'])
        merged_config['logging']['max_size_mb'] = self._get_env_var('LOG_MAX_SIZE_MB', config['logging'].get('max_size_mb', 10), int)
        merged_config['logging']['backup_count'] = self._get_env_var('LOG_BACKUP_COUNT', config['logging'].get('backup_count', 5), int)
        merged_config['logging']['format'] = self._get_env_var('LOG_FORMAT', config['logging'].get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Privacy settings
        merged_config['privacy']['store_location_history'] = self._get_env_var('PRIVACY_STORE_LOCATION_HISTORY', config['privacy']['store_location_history'], bool)
        merged_config['privacy']['data_retention_days'] = self._get_env_var('PRIVACY_DATA_RETENTION_DAYS', config['privacy'].get('data_retention_days', 30), int)
        merged_config['privacy']['anonymous_mode'] = self._get_env_var('PRIVACY_ANONYMOUS_MODE', config['privacy'].get('anonymous_mode', False), bool)
        
        # Development mode
        merged_config['dev_mode'] = self._get_env_var('DEV_MODE', False, bool)
        
        # Simulation settings
        if 'simulation' not in merged_config:
            merged_config['simulation'] = {}
        merged_config['simulation']['base_lat'] = self._get_env_var('SIMULATION_BASE_LAT', 40.7128, float)
        merged_config['simulation']['base_lon'] = self._get_env_var('SIMULATION_BASE_LON', -74.0060, float)
        merged_config['simulation']['radius'] = self._get_env_var('SIMULATION_RADIUS', 0.01, float)
        
        return merged_config
        
    def load_config(self) -> Dict[str, Any]:
        """Load the main application configuration.
        
        Returns:
            Dictionary containing configuration settings with environment variables applied
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    base_config = json.load(f)
            else:
                # Try to load from example file if config doesn't exist
                example_file = self.config_dir / "config.example.json"
                if example_file.exists():
                    with open(example_file, 'r') as f:
                        base_config = json.load(f)
                    # Save as actual config file
                    self.save_config(base_config)
                else:
                    base_config = self._get_default_config()
            
            # Merge with environment variables
            return self._merge_env_with_config(base_config)
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            base_config = self._get_default_config()
            return self._merge_env_with_config(base_config)
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_zones_config(self) -> Dict[str, Any]:
        """Load danger zones configuration.
        
        Returns:
            Dictionary containing zones configuration
        """
        try:
            if self.zones_file.exists():
                with open(self.zones_file, 'r') as f:
                    return json.load(f)
            else:
                # Try to load from example file
                example_file = self.config_dir / "zones.example.json"
                if example_file.exists():
                    with open(example_file, 'r') as f:
                        zones_config = json.load(f)
                    # Save as actual zones file
                    self.save_zones_config(zones_config)
                    return zones_config
                else:
                    return self._get_default_zones_config()
        except Exception as e:
            print(f"Error loading zones configuration: {e}")
            return self._get_default_zones_config()
    
    def save_zones_config(self, zones_config: Dict[str, Any]) -> bool:
        """Save zones configuration to file.
        
        Args:
            zones_config: Zones configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.zones_file, 'w') as f:
                json.dump(zones_config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving zones configuration: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "app": {
                "name": "GPS Danger Zone Tracker",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "gps": {
                "source_type": "serial",
                "update_interval": 1.0
            },
            "zones": {
                "check_interval": 5.0,
                "buffer_distance": 10.0,
                "units": "meters"
            },
            "alerts": {
                "enabled": True,
                "types": ["desktop"]
            },
            "database": {
                "type": "sqlite",
                "path": "data/tracker.db"
            },
            "web_interface": {
                "enabled": True,
                "host": "localhost",
                "port": 5000
            },
            "logging": {
                "file": "logs/gps_tracker.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "privacy": {
                "store_location_history": True,
                "data_retention_days": 30
            }
        }
    
    def _get_default_zones_config(self) -> Dict[str, Any]:
        """Get default zones configuration.
        
        Returns:
            Default zones configuration dictionary
        """
        return {
            "danger_zones": [],
            "zone_types": {
                "construction": {
                    "color": "#FF6B35",
                    "icon": "construction",
                    "default_radius": 100
                },
                "environmental": {
                    "color": "#4ECDC4",
                    "icon": "nature",
                    "default_radius": 150
                },
                "security": {
                    "color": "#FF4757",
                    "icon": "warning",
                    "default_radius": 200
                }
            },
            "global_settings": {
                "auto_activate_zones": True,
                "check_overlap": True,
                "max_active_zones": 50
            }
        }