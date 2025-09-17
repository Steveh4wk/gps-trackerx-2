"""
Logging utility for GPS Danger Zone Tracker

Provides structured logging configuration for the application.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any


def setup_logger(logging_config: Dict[str, Any]) -> logging.Logger:
    """Set up the application logger with the given configuration.
    
    Args:
        logging_config: Dictionary containing logging configuration
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("gps_tracker")
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set logging level
    log_level = getattr(logging, logging_config.get('log_level', 'INFO').upper())
    logger.setLevel(log_level)
    
    # Create formatter
    log_format = logging_config.get(
        'format',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    log_file = logging_config.get('file')
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        max_bytes = logging_config.get('max_size_mb', 10) * 1024 * 1024
        backup_count = logging_config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class GPSTrackerLogger:
    """Enhanced logger class with GPS-specific functionality."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize the GPS tracker logger.
        
        Args:
            name: Logger name
            config: Logging configuration
        """
        self.logger = setup_logger(config)
        self.name = name
        
    def log_location(self, location: Dict[str, Any], context: str = ""):
        """Log location data with proper formatting.
        
        Args:
            location: Location dictionary with lat/lon data
            context: Additional context information
        """
        lat = location.get('latitude', 0.0)
        lon = location.get('longitude', 0.0)
        timestamp = location.get('timestamp', 'unknown')
        
        message = f"Location: {lat:.6f}, {lon:.6f} at {timestamp}"
        if context:
            message += f" ({context})"
            
        self.logger.info(message)
    
    def log_zone_event(self, event_type: str, zone_name: str, location: Dict[str, Any]):
        """Log zone-related events.
        
        Args:
            event_type: Type of zone event (enter, exit, proximity)
            zone_name: Name of the danger zone
            location: Location data
        """
        lat = location.get('latitude', 0.0)
        lon = location.get('longitude', 0.0)
        
        message = f"Zone {event_type}: {zone_name} at {lat:.6f}, {lon:.6f}"
        
        if event_type.lower() in ['enter', 'entered']:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def log_alert(self, alert_type: str, zone_name: str, severity: str):
        """Log alert events.
        
        Args:
            alert_type: Type of alert
            zone_name: Name of the zone triggering the alert
            severity: Severity level of the alert
        """
        message = f"Alert triggered: {alert_type} for zone {zone_name} (severity: {severity})"
        
        if severity.lower() == 'high':
            self.logger.error(message)
        elif severity.lower() == 'medium':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)