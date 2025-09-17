"""
Configuration Manager for GPS Danger Zone Tracker

Handles loading and managing application configuration from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


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
        
    def load_config(self) -> Dict[str, Any]:
        """Load the main application configuration.
        
        Returns:
            Dictionary containing configuration settings
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Try to load from example file if config doesn't exist
                example_file = self.config_dir / "config.example.json"
                if example_file.exists():
                    with open(example_file, 'r') as f:
                        config = json.load(f)
                    # Save as actual config file
                    self.save_config(config)
                    return config
                else:
                    return self._get_default_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self._get_default_config()
    
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