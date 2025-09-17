"""
Alert System Module

Handles various types of alerts when danger zones are triggered.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class AlertSystem:
    """Manages alerts for danger zone violations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the alert system.
        
        Args:
            config: Alert configuration dictionary
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        self.alert_types = config.get('types', ['desktop'])
        self.cooldown_period = config.get('cooldown_period', 60)  # seconds
        
        # Track recent alerts to prevent spam
        self.recent_alerts = {}
        self.running = True
        
    async def trigger_alert(self, zone_status: Dict[str, Any], location: Dict[str, Any]):
        """Trigger appropriate alerts based on zone status.
        
        Args:
            zone_status: Zone status information
            location: Current location data
        """
        if not self.enabled:
            return
        
        # Process each triggered zone
        for zone_info in zone_status.get('zones', []):
            zone = zone_info['zone']
            zone_id = zone.get('id')
            
            # Check cooldown period
            if self._is_in_cooldown(zone_id):
                continue
            
            # Determine alert severity and message
            severity = zone.get('severity', 'medium')
            alert_message = self._create_alert_message(zone, location)
            
            # Trigger configured alert types
            await self._send_alerts(alert_message, severity, zone)
            
            # Record alert time for cooldown
            self._record_alert_time(zone_id)
    
    def stop(self):
        """Stop the alert system."""
        self.running = False
    
    def _is_in_cooldown(self, zone_id: str) -> bool:
        """Check if zone is in alert cooldown period.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            True if in cooldown, False otherwise
        """
        if zone_id not in self.recent_alerts:
            return False
        
        last_alert_time = self.recent_alerts[zone_id]
        cooldown_end = last_alert_time + timedelta(seconds=self.cooldown_period)
        
        return datetime.now() < cooldown_end
    
    def _record_alert_time(self, zone_id: str):
        """Record the time of an alert for cooldown tracking.
        
        Args:
            zone_id: Zone identifier
        """
        self.recent_alerts[zone_id] = datetime.now()
    
    def _create_alert_message(self, zone: Dict[str, Any], location: Dict[str, Any]) -> str:
        """Create alert message based on zone and location.
        
        Args:
            zone: Zone dictionary
            location: Location dictionary
            
        Returns:
            Alert message string
        """
        zone_name = zone.get('name', 'Unknown Zone')
        zone_type = zone.get('type', 'unknown')
        severity = zone.get('severity', 'medium')
        
        lat = location.get('latitude', 0.0)
        lon = location.get('longitude', 0.0)
        
        message = f"DANGER ZONE ALERT: You have entered '{zone_name}' ({zone_type})"
        message += f"\\nLocation: {lat:.6f}, {lon:.6f}"
        message += f"\\nSeverity: {severity.upper()}"
        
        description = zone.get('description')
        if description:
            message += f"\\nDetails: {description}"
        
        return message
    
    async def _send_alerts(self, message: str, severity: str, zone: Dict[str, Any]):
        """Send alerts using configured methods.
        
        Args:
            message: Alert message
            severity: Alert severity level
            zone: Zone dictionary
        """
        alert_tasks = []
        
        for alert_type in self.alert_types:
            if alert_type == 'desktop':
                alert_tasks.append(self._send_desktop_notification(message, severity))
            elif alert_type == 'sound':
                alert_tasks.append(self._play_alert_sound(severity))
            elif alert_type == 'email':
                alert_tasks.append(self._send_email_alert(message, severity, zone))
            elif alert_type == 'log':
                alert_tasks.append(self._log_alert(message, severity))
        
        # Execute all alert methods concurrently
        if alert_tasks:
            await asyncio.gather(*alert_tasks, return_exceptions=True)
    
    async def _send_desktop_notification(self, message: str, severity: str):
        """Send desktop notification.
        
        Args:
            message: Alert message
            severity: Alert severity level
        """
        try:
            # Try to use plyer for cross-platform notifications
            from plyer import notification
            
            title = "GPS Danger Zone Alert"
            if severity == 'high':
                title = "⚠️ URGENT: " + title
            elif severity == 'medium':
                title = "⚡ WARNING: " + title
            
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            
        except ImportError:
            # Fallback to print if plyer not available
            print(f"DESKTOP ALERT: {message}")
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
    
    async def _play_alert_sound(self, severity: str):
        """Play alert sound.
        
        Args:
            severity: Alert severity level
        """
        try:
            sound_file = self.config.get('sound_file', 'alerts/warning.wav')
            
            # Different sounds for different severities (if configured)
            if severity == 'high':
                sound_file = self.config.get('high_severity_sound', sound_file)
            elif severity == 'low':
                sound_file = self.config.get('low_severity_sound', sound_file)
            
            # Try to play sound using system command
            import os
            if os.name == 'nt':  # Windows
                import winsound
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:  # Linux/Mac
                os.system(f'paplay "{sound_file}" &')
                
        except Exception as e:
            print(f"Error playing alert sound: {e}")
            # Fallback to system beep
            try:
                import winsound
                winsound.Beep(1000, 500)  # 1000 Hz for 500ms
            except:
                print("\\a")  # Terminal bell
    
    async def _send_email_alert(self, message: str, severity: str, zone: Dict[str, Any]):
        """Send email alert.
        
        Args:
            message: Alert message
            severity: Alert severity level
            zone: Zone dictionary
        """
        email_config = self.config.get('email', {})
        if not email_config.get('enabled', False):
            return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Email configuration
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username', '')
            password = email_config.get('password', '')
            recipients = email_config.get('recipients', [])
            
            if not username or not password or not recipients:
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"GPS Danger Zone Alert - {severity.upper()}"
            
            # Email body
            body = f"GPS Danger Zone Alert\\n\\n{message}\\n\\n"
            body += f"Zone Information:\\n"
            body += f"- Name: {zone.get('name', 'Unknown')}\\n"
            body += f"- Type: {zone.get('type', 'Unknown')}\\n"
            body += f"- Severity: {severity}\\n"
            body += f"- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
    
    async def _log_alert(self, message: str, severity: str):
        """Log alert to file.
        
        Args:
            message: Alert message
            severity: Alert severity level
        """
        try:
            from pathlib import Path
            import json
            
            # Ensure logs directory exists
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / "alerts.log"
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'severity': severity,
                'message': message,
                'type': 'zone_alert'
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\\n')
                
        except Exception as e:
            print(f"Error logging alert: {e}")


class AlertHistory:
    """Manages alert history and statistics."""
    
    def __init__(self):
        """Initialize alert history."""
        self.alerts = []
        self.max_history = 1000
    
    def add_alert(self, zone_id: str, zone_name: str, severity: str, location: Dict[str, Any]):
        """Add alert to history.
        
        Args:
            zone_id: Zone identifier
            zone_name: Zone name
            severity: Alert severity
            location: Location data
        """
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'zone_id': zone_id,
            'zone_name': zone_name,
            'severity': severity,
            'location': location
        }
        
        self.alerts.append(alert_record)
        
        # Keep history limited
        if len(self.alerts) > self.max_history:
            self.alerts = self.alerts[-self.max_history:]
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alert records
        """
        return self.alerts[-limit:] if self.alerts else []
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics.
        
        Returns:
            Dictionary with alert statistics
        """
        if not self.alerts:
            return {'total': 0, 'by_severity': {}, 'by_zone': {}}
        
        # Count by severity
        severity_counts = {}
        zone_counts = {}
        
        for alert in self.alerts:
            severity = alert['severity']
            zone_name = alert['zone_name']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
        
        return {
            'total': len(self.alerts),
            'by_severity': severity_counts,
            'by_zone': zone_counts,
            'most_recent': self.alerts[-1]['timestamp'] if self.alerts else None
        }