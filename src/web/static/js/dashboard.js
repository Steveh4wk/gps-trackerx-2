// Dashboard JavaScript for GPS Danger Zone Tracker

let map = null;
let currentLocationMarker = null;
let dangerZoneCircles = [];
let socket = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    initializeWebSocket();
    loadInitialData();
    startDataUpdates();
});

// Initialize Leaflet map
function initializeMap() {
    // Default center - will be updated with real GPS data
    const defaultLat = 40.7128;
    const defaultLng = -74.0060;
    
    map = L.map('map').setView([defaultLat, defaultLng], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add current location marker
    currentLocationMarker = L.marker([defaultLat, defaultLng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
        })
    }).addTo(map);
    
    currentLocationMarker.bindPopup('Current Location').openPopup();
}

// Initialize WebSocket connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('location_update', function(data) {
        updateLocation(data);
    });
    
    socket.on('zone_alert', function(data) {
        showAlert(data);
    });
}

// Load initial data
function loadInitialData() {
    // Load status
    fetch('/api/status')
        .then(response => response.json())
        .then(data => updateStatus(data))
        .catch(error => console.error('Error loading status:', error));
    
    // Load zones
    fetch('/api/zones')
        .then(response => response.json())
        .then(data => updateZones(data.zones))
        .catch(error => console.error('Error loading zones:', error));
    
    // Load alerts
    fetch('/api/alerts')
        .then(response => response.json())
        .then(data => updateAlerts(data.alerts))
        .catch(error => console.error('Error loading alerts:', error));
}

// Start periodic data updates
function startDataUpdates() {
    // Update location every 2 seconds
    setInterval(function() {
        fetch('/api/location')
            .then(response => response.json())
            .then(data => updateLocation(data))
            .catch(error => console.error('Error updating location:', error));
    }, 2000);
    
    // Update status every 10 seconds
    setInterval(function() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => updateStatus(data))
            .catch(error => console.error('Error updating status:', error));
    }, 10000);
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (connected) {
        statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
    } else {
        statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
    }
}

// Update GPS location
function updateLocation(location) {
    if (!location.latitude || !location.longitude) return;
    
    // Update map
    const latlng = [location.latitude, location.longitude];
    currentLocationMarker.setLatLng(latlng);
    map.setView(latlng, map.getZoom());
    
    // Update UI
    document.getElementById('current-lat').textContent = location.latitude.toFixed(6);
    document.getElementById('current-lng').textContent = location.longitude.toFixed(6);
    document.getElementById('current-accuracy').textContent = (location.accuracy || 0) + ' m';
    document.getElementById('current-speed').textContent = ((location.speed || 0) * 3.6).toFixed(1) + ' km/h';
    document.getElementById('last-update').textContent = new Date(location.timestamp).toLocaleTimeString();
}

// Update system status
function updateStatus(status) {
    document.getElementById('gps-status').textContent = status.gps_connected ? 'Connected' : 'Disconnected';
    
    const gpsCard = document.querySelector('.card.bg-primary');
    if (status.gps_connected) {
        gpsCard.classList.remove('bg-danger');
        gpsCard.classList.add('bg-primary');
    } else {
        gpsCard.classList.remove('bg-primary');
        gpsCard.classList.add('bg-danger');
    }
}

// Update danger zones
function updateZones(zones) {
    // Clear existing zone circles
    dangerZoneCircles.forEach(circle => map.removeLayer(circle));
    dangerZoneCircles = [];
    
    // Update zones count
    document.getElementById('active-zones-count').textContent = zones.filter(z => z.active).length;
    
    // Add zones to map and table
    const tableBody = document.getElementById('zones-table');
    tableBody.innerHTML = '';
    
    zones.forEach(zone => {
        // Add to map if it has geometry
        if (zone.geometry && zone.geometry.type === 'circle') {
            const center = [zone.geometry.center.latitude, zone.geometry.center.longitude];
            const radius = zone.geometry.radius;
            
            const circle = L.circle(center, {
                radius: radius,
                color: getZoneColor(zone.type),
                fillColor: getZoneColor(zone.type),
                fillOpacity: 0.2
            }).addTo(map);
            
            circle.bindPopup(`
                <strong>${zone.name}</strong><br>
                Type: ${zone.type}<br>
                Severity: ${zone.severity}<br>
                Radius: ${radius}m
            `);
            
            dangerZoneCircles.push(circle);
        }
        
        // Add to table
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${zone.name}</td>
            <td><span class="zone-badge zone-${zone.type}">${zone.type}</span></td>
            <td><span class="severity-${zone.severity}">${zone.severity.toUpperCase()}</span></td>
            <td>${zone.active ? '<i class="fas fa-check-circle status-active"></i> Active' : '<i class="fas fa-times-circle status-inactive"></i> Inactive'}</td>
            <td>${zone.geometry && zone.geometry.radius ? zone.geometry.radius + 'm' : 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary btn-action" onclick="editZone('${zone.id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger btn-action" onclick="deleteZone('${zone.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Update alerts
function updateAlerts(alerts) {
    document.getElementById('alerts-count').textContent = alerts.length;
    
    const alertsList = document.getElementById('alerts-list');
    if (alerts.length === 0) {
        alertsList.innerHTML = '<p class="text-muted">No recent alerts</p>';
        return;
    }
    
    alertsList.innerHTML = '';
    alerts.slice(-5).reverse().forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item alert-${alert.severity}`;
        alertDiv.innerHTML = `
            <div class="fw-bold">${alert.zone_name}</div>
            <div class="small">${alert.message}</div>
            <div class="small text-muted">${new Date(alert.timestamp).toLocaleString()}</div>
        `;
        alertsList.appendChild(alertDiv);
    });
}

// Show new alert
function showAlert(alert) {
    // Update current zone status
    document.getElementById('current-zone').textContent = alert.zone_name;
    
    // Show browser notification if supported
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('GPS Danger Zone Alert', {
            body: `Entered ${alert.zone_name}`,
            icon: '/static/images/alert-icon.png'
        });
    }
}

// Get zone color based on type
function getZoneColor(type) {
    const colors = {
        'construction': '#FF6B35',
        'environmental': '#4ECDC4',
        'security': '#FF4757',
        'traffic': '#FFA502'
    };
    return colors[type] || '#6c757d';
}

// Zone management functions
function addZone() {
    const formData = {
        name: document.getElementById('zoneName').value,
        type: document.getElementById('zoneType').value,
        severity: document.getElementById('zoneSeverity').value,
        latitude: parseFloat(document.getElementById('zoneLatitude').value),
        longitude: parseFloat(document.getElementById('zoneLongitude').value),
        radius: parseInt(document.getElementById('zoneRadius').value),
        description: document.getElementById('zoneDescription').value
    };
    
    fetch('/api/zones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal and refresh zones
            const modal = bootstrap.Modal.getInstance(document.getElementById('addZoneModal'));
            modal.hide();
            loadInitialData();
        } else {
            alert('Error adding zone: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error adding zone:', error);
        alert('Error adding zone');
    });
}

function editZone(zoneId) {
    alert('Edit zone functionality not yet implemented');
}

function deleteZone(zoneId) {
    if (confirm('Are you sure you want to delete this zone?')) {
        fetch(`/api/zones/${zoneId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadInitialData();
            } else {
                alert('Error deleting zone: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting zone:', error);
            alert('Error deleting zone');
        });
    }
}

// Request notification permission on load
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}