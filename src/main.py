#!/usr/bin/env python3
"""
GPS Danger Zone Tracker - Main Application Entry Point

This is the main entry point for the GPS Danger Zone Tracker application.
It initializes and coordinates all components of the system.
"""

import sys
import os
import json
import logging
import asyncio
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from tracker.gps_tracker import GPSTracker
from zones.zone_manager import ZoneManager
from alerts.alert_system import AlertSystem
from web.app import create_web_app


class GPSDangerZoneTracker:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the GPS Danger Zone Tracker application."""
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Set up logging
        self.logger = setup_logger(self.config.get('logging', {}))
        self.logger.info("Starting GPS Danger Zone Tracker v%s", 
                        self.config['app']['version'])
        
        # Initialize components
        self.gps_tracker = None
        self.zone_manager = None
        self.alert_system = None
        self.web_app = None
        self.running = False
        
    def initialize_components(self):
        """Initialize all application components."""
        try:
            self.logger.info("Initializing application components...")
            
            # Initialize GPS tracker
            self.gps_tracker = GPSTracker(self.config.get('gps', {}))
            
            # Initialize zone manager
            self.zone_manager = ZoneManager(self.config.get('zones', {}))
            
            # Initialize alert system
            self.alert_system = AlertSystem(self.config.get('alerts', {}))
            
            # Initialize web interface if enabled
            if self.config.get('web_interface', {}).get('enabled', False):
                self.web_app = create_web_app(self.config)
                
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize components: %s", str(e))
            return False
    
    async def start_tracking(self):
        """Start the GPS tracking and zone monitoring."""
        try:
            self.logger.info("Starting GPS tracking and zone monitoring...")
            self.running = True
            
            # Start GPS tracker
            await self.gps_tracker.start()
            
            # Main tracking loop
            while self.running:
                try:
                    # Get current location from GPS tracker
                    location = await self.gps_tracker.get_current_location()
                    
                    if location:
                        # Check for danger zone violations
                        zone_status = self.zone_manager.check_location(location)
                        
                        # Handle alerts if necessary
                        if zone_status.get('in_danger_zone', False):
                            await self.alert_system.trigger_alert(zone_status, location)
                        
                        # Log location data if configured
                        if self.config.get('privacy', {}).get('store_location_history', True):
                            self.gps_tracker.log_location(location, zone_status)
                    
                    # Wait for next update interval
                    await asyncio.sleep(self.config.get('gps', {}).get('update_interval', 1.0))
                    
                except KeyboardInterrupt:
                    self.logger.info("Received interrupt signal, stopping...")
                    break
                except Exception as e:
                    self.logger.error("Error in tracking loop: %s", str(e))
                    await asyncio.sleep(1.0)  # Brief pause before retrying
                    
        except Exception as e:
            self.logger.error("Failed to start tracking: %s", str(e))
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the application and clean up resources."""
        self.logger.info("Stopping GPS Danger Zone Tracker...")
        self.running = False
        
        # Stop GPS tracker
        if self.gps_tracker:
            await self.gps_tracker.stop()
        
        # Stop alert system
        if self.alert_system:
            self.alert_system.stop()
        
        self.logger.info("Application stopped successfully")
    
    def run(self):
        """Run the application."""
        try:
            if not self.initialize_components():
                self.logger.error("Failed to initialize components, exiting")
                return 1
            
            # Run the main tracking loop
            asyncio.run(self.start_tracking())
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return 0
        except Exception as e:
            self.logger.error("Unexpected error: %s", str(e))
            return 1


def main():
    """Main function to run the application."""
    app = GPSDangerZoneTracker()
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()