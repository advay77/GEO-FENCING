/**
 * Indian Railways Geo-Fencing System - Frontend Application
 * 
 * This file contains the main frontend application logic for the
 * Indian Railways Geo-Fencing System. It handles map visualization,
 * real-time updates, and user interactions.
 */

// Global variables
let map;
let trains = [];
let stations = [];
let objects = [];
let alerts = [];
let trainMarkers = {};
let stationMarkers = {};
let objectMarkers = {};
let selectedTrain = null;
let refreshInterval;

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    setupEventListeners();
    loadInitialData();
    startRealTimeUpdates();
});

// Initialize the map
function initializeMap() {
    // Center on India
    map = L.map('map').setView([20.5937, 78.9629], 5);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

// Set up event listeners
function setupEventListeners() {
    // Train selection
    document.getElementById('train-select').addEventListener('change', (e) => {
        selectedTrain = e.target.value;
        updateTrainDetails(selectedTrain);
    });
    
    // Simulation controls
    document.getElementById('simulate-movement').addEventListener('click', () => {
        simulateTrainMovement();
    });
    
    document.getElementById('simulate-theft').addEventListener('click', () => {
        if (selectedTrain) {
            simulateObjectTheft(selectedTrain);
        } else {
            showNotification('Please select a train first', 'error');
        }
    });
    
    document.getElementById('simulate-journey').addEventListener('click', () => {
        if (selectedTrain) {
            const destinationStation = document.getElementById('destination-station').value;
            if (destinationStation) {
                simulateFullJourney(selectedTrain, destinationStation);
            } else {
                showNotification('Please select a destination station', 'error');
            }
        } else {
            showNotification('Please select a train first', 'error');
        }
    });
    
    // Alert filters
    document.getElementById('alert-filter-form').addEventListener('submit', (e) => {
        e.preventDefault();
        loadAlerts();
    });
}

// Load initial data from the API
async function loadInitialData() {
    try {
        // Load stations
        const stationsResponse = await fetch(`${API_BASE_URL}/stations`);
        stations = await stationsResponse.json();
        renderStations();
        populateStationDropdown();
        
        // Load trains
        const trainsResponse = await fetch(`${API_BASE_URL}/trains`);
        trains = await trainsResponse.json();
        renderTrains();
        populateTrainDropdown();
        
        // Load objects
        const objectsResponse = await fetch(`${API_BASE_URL}/objects`);
        objects = await objectsResponse.json();
        renderObjects();
        
        // Load alerts
        loadAlerts();
        
    } catch (error) {
        console.error('Error loading initial data:', error);
        showNotification('Failed to load data from the server', 'error');
    }
}

// Render stations on the map
function renderStations() {
    stations.forEach(station => {
        if (stationMarkers[station.code]) {
            // Update existing marker
            stationMarkers[station.code].setLatLng([
                station.location.coordinates[1],
                station.location.coordinates[0]
            ]);
        } else {
            // Create new marker
            const marker = L.marker([
                station.location.coordinates[1],
                station.location.coordinates[0]
            ], {
                icon: L.divIcon({
                    className: 'station-marker',
                    html: `<div class="station-icon"><i class="fas fa-train-subway"></i></div>`,
                    iconSize: [30, 30]
                })
            }).addTo(map);
            
            // Add popup
            marker.bindPopup(`
                <strong>${station.name}</strong><br>
                Code: ${station.code}<br>
                Coordinates: ${station.location.coordinates[1]}, ${station.location.coordinates[0]}
            `);
            
            stationMarkers[station.code] = marker;
        }
    });
}

// Render trains on the map
function renderTrains() {
    trains.forEach(train => {
        if (trainMarkers[train.number]) {
            // Update existing marker
            trainMarkers[train.number].setLatLng([
                train.location.coordinates[1],
                train.location.coordinates[0]
            ]);
            
            // Update popup content
            trainMarkers[train.number].getPopup().setContent(`
                <strong>${train.name}</strong><br>
                Number: ${train.number}<br>
                Speed: ${train.speed} km/h<br>
                Direction: ${train.direction}°<br>
                Coaches: ${train.coaches.map(c => c.id).join(', ')}
            `);
            
            // Update tooltip
            trainMarkers[train.number].setTooltipContent(`${train.name} (${train.number})`);
        } else {
            // Create new marker
            const marker = L.marker([
                train.location.coordinates[1],
                train.location.coordinates[0]
            ], {
                icon: L.divIcon({
                    className: 'train-marker',
                    html: `<div class="train-icon"><i class="fas fa-train"></i></div>`,
                    iconSize: [40, 40]
                })
            }).addTo(map);
            
            // Add popup
            marker.bindPopup(`
                <strong>${train.name}</strong><br>
                Number: ${train.number}<br>
                Speed: ${train.speed} km/h<br>
                Direction: ${train.direction}°<br>
                Coaches: ${train.coaches.map(c => c.id).join(', ')}
            `);
            
            // Add tooltip
            marker.bindTooltip(`${train.name} (${train.number})`);
            
            trainMarkers[train.number] = marker;
        }
        
        // Draw geo-fence circle around train (1 km radius for station proximity)
        if (trainMarkers[train.number].circle) {
            trainMarkers[train.number].circle.setLatLng([
                train.location.coordinates[1],
                train.location.coordinates[0]
            ]);
        } else {
            const circle = L.circle([
                train.location.coordinates[1],
                train.location.coordinates[0]
            ], {
                color: 'blue',
                fillColor: 'rgba(0, 0, 255, 0.1)',
                fillOpacity: 0.2,
                radius: 1000 // 1 km
            }).addTo(map);
            
            trainMarkers[train.number].circle = circle;
        }
    });
}

// Render objects on the map
function renderObjects() {
    objects.forEach(obj => {
        if (objectMarkers[obj.id]) {
            // Update existing marker
            objectMarkers[obj.id].setLatLng([
                obj.location.coordinates[1],
                obj.location.coordinates[0]
            ]);
        } else {
            // Create new marker
            const marker = L.marker([
                obj.location.coordinates[1],
                obj.location.coordinates[0]
            ], {
                icon: L.divIcon({
                    className: 'object-marker',
                    html: `<div class="object-icon"><i class="fas fa-suitcase"></i></div>`,
                    iconSize: [20, 20]
                })
            }).addTo(map);
            
            // Add popup
            marker.bindPopup(`
                <strong>${obj.type}</strong><br>
                ID: ${obj.id}<br>
                Owner: ${obj.ownerId}<br>
                Train: ${obj.trainNumber}<br>
                Coach: ${obj.coachId}
            `);
            
            objectMarkers[obj.id] = marker;
        }
    });
}

// Populate train dropdown
function populateTrainDropdown() {
    const trainSelect = document.getElementById('train-select');
    trainSelect.innerHTML = '<option value="">Select a train</option>';
    
    trains.forEach(train => {
        const option = document.createElement('option');
        option.value = train.number;
        option.textContent = `${train.name} (${train.number})`;
        trainSelect.appendChild(option);
    });
}

// Populate station dropdown
function populateStationDropdown() {
    const stationSelect = document.getElementById('destination-station');
    stationSelect.innerHTML = '<option value="">Select a station</option>';
    
    stations.forEach(station => {
        const option = document.createElement('option');
        option.value = station.code;
        option.textContent = `${station.name} (${station.code})`;
        stationSelect.appendChild(option);
    });
}

// Update train details panel
function updateTrainDetails(trainNumber) {
    const detailsContainer = document.getElementById('train-details');
    
    if (!trainNumber) {
        detailsContainer.innerHTML = '<p>No train selected</p>';
        return;
    }
    
    const train = trains.find(t => t.number === trainNumber);
    if (!train) {
        detailsContainer.innerHTML = '<p>Train not found</p>';
        return;
    }
    
    // Find objects on this train
    const trainObjects = objects.filter(obj => obj.trainNumber === trainNumber);
    
    // Find alerts for this train
    const trainAlerts = alerts.filter(alert => alert.trainNumber === trainNumber && !alert.resolved);
    
    detailsContainer.innerHTML = `
        <h3>${train.name}</h3>
        <p><strong>Number:</strong> ${train.number}</p>
        <p><strong>Speed:</strong> ${train.speed} km/h</p>
        <p><strong>Direction:</strong> ${train.direction}°</p>
        <p><strong>Location:</strong> ${train.location.coordinates[1]}, ${train.location.coordinates[0]}</p>
        
        <h4>Coaches</h4>
        <ul>
            ${train.coaches.map(coach => `
                <li>${coach.id} (Geo-fence: ${coach.geofenceRadius * 1000} meters)</li>
            `).join('')}
        </ul>
        
        <h4>Objects (${trainObjects.length})</h4>
        ${trainObjects.length > 0 ? `
            <ul>
                ${trainObjects.map(obj => `
                    <li>${obj.type} (${obj.id}) - Coach: ${obj.coachId}</li>
                `).join('')}
            </ul>
        ` : '<p>No objects on this train</p>'}
        
        <h4>Active Alerts (${trainAlerts.length})</h4>
        ${trainAlerts.length > 0 ? `
            <ul class="alert-list">
                ${trainAlerts.map(alert => `
                    <li class="alert-item ${alert.type}">
                        <strong>${alert.type === 'station_proximity' ? 'Station Proximity' : 'Theft'}</strong>
                        <p>${formatAlertMessage(alert)}</p>
                        <small>${new Date(alert.timestamp).toLocaleString()}</small>
                    </li>
                `).join('')}
            </ul>
        ` : '<p>No active alerts</p>'}
    `;
    
    // Center map on train
    map.setView([
        train.location.coordinates[1],
        train.location.coordinates[0]
    ], 12);
}

// Load alerts from the API
async function loadAlerts() {
    try {
        // Get filter values
        const alertType = document.getElementById('alert-type').value;
        const resolved = document.getElementById('alert-resolved').value;
        const trainNumber = document.getElementById('alert-train').value;
        
        // Build query string
        let queryParams = [];
        if (alertType) queryParams.push(`alert_type=${alertType}`);
        if (resolved !== '') queryParams.push(`resolved=${resolved}`);
        if (trainNumber) queryParams.push(`train_number=${trainNumber}`);
        
        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        
        // Fetch alerts
        const alertsResponse = await fetch(`${API_BASE_URL}/alerts${queryString}`);
        alerts = await alertsResponse.json();
        
        // Render alerts
        renderAlerts();
        
        // Update train details if a train is selected
        if (selectedTrain) {
            updateTrainDetails(selectedTrain);
        }
        
    } catch (error) {
        console.error('Error loading alerts:', error);
        showNotification('Failed to load alerts from the server', 'error');
    }
}

// Render alerts in the alerts panel
function renderAlerts() {
    const alertsContainer = document.getElementById('alerts-container');
    
    if (alerts.length === 0) {
        alertsContainer.innerHTML = '<p>No alerts found</p>';
        return;
    }
    
    alertsContainer.innerHTML = `
        <ul class="alert-list">
            ${alerts.map(alert => `
                <li class="alert-item ${alert.type} ${alert.resolved ? 'resolved' : ''}">
                    <div class="alert-header">
                        <strong>${alert.type === 'station_proximity' ? 'Station Proximity' : 'Theft'}</strong>
                        <span class="alert-status">${alert.resolved ? 'Resolved' : 'Active'}</span>
                    </div>
                    <p>${formatAlertMessage(alert)}</p>
                    <div class="alert-footer">
                        <small>${new Date(alert.timestamp).toLocaleString()}</small>
                        ${!alert.resolved ? `
                            <button class="resolve-btn" data-alert-id="${alert.id}">Resolve</button>
                        ` : ''}
                    </div>
                </li>
            `).join('')}
        </ul>
    `;
    
    // Add event listeners to resolve buttons
    document.querySelectorAll('.resolve-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const alertId = btn.getAttribute('data-alert-id');
            await resolveAlert(alertId);
        });
    });
}

// Format alert message based on type
function formatAlertMessage(alert) {
    if (alert.type === 'station_proximity') {
        return `Train ${alert.trainName} (${alert.trainNumber}) is approaching ${alert.stationName} (${alert.stationCode}). Distance: ${alert.distance.toFixed(2)} km`;
    } else if (alert.type === 'theft') {
        return `Object ${alert.objectId} (${alert.objectType}) has moved outside of coach ${alert.coachId} on train ${alert.trainName} (${alert.trainNumber})`;
    }
    return '';
}

// Resolve an alert
async function resolveAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/resolve`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            showNotification('Alert resolved successfully', 'success');
            loadAlerts();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to resolve alert');
        }
    } catch (error) {
        console.error('Error resolving alert:', error);
        showNotification(`Failed to resolve alert: ${error.message}`, 'error');
    }
}

// Simulate train movement
async function simulateTrainMovement() {
    try {
        const response = await fetch(`${API_BASE_URL}/simulate/train-movement`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`${result.message} (${result.updated_trains} trains updated)`, 'success');
            
            // Refresh data
            loadInitialData();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to simulate train movement');
        }
    } catch (error) {
        console.error('Error simulating train movement:', error);
        showNotification(`Failed to simulate train movement: ${error.message}`, 'error');
    }
}

// Simulate object theft
async function simulateObjectTheft(trainNumber) {
    try {
        // Get objects for the selected train
        const trainObjects = objects.filter(obj => obj.trainNumber === trainNumber);
        
        if (trainObjects.length === 0) {
            showNotification('No objects found for this train', 'error');
            return;
        }
        
        // Select a random object
        const randomObject = trainObjects[Math.floor(Math.random() * trainObjects.length)];
        
        // Simulate theft
        const response = await fetch(`${API_BASE_URL}/simulate/object-theft/${randomObject.id}?distance=0.1`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`${result.message} (${result.actual_distance_km.toFixed(2)} km)`, 'success');
            
            // Refresh data
            loadInitialData();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to simulate object theft');
        }
    } catch (error) {
        console.error('Error simulating object theft:', error);
        showNotification(`Failed to simulate object theft: ${error.message}`, 'error');
    }
}

// Simulate full journey
async function simulateFullJourney(trainNumber, destinationStation) {
    try {
        const response = await fetch(`${API_BASE_URL}/simulate/full-journey/${trainNumber}?destination_station=${destinationStation}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`Journey simulation started: ${result.train} to ${result.destination} (${result.distance_km.toFixed(2)} km, ${result.duration_minutes} minutes)`, 'success');
            
            // Refresh data
            loadInitialData();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to simulate journey');
        }
    } catch (error) {
        console.error('Error simulating journey:', error);
        showNotification(`Failed to simulate journey: ${error.message}`, 'error');
    }
}

// Start real-time updates
function startRealTimeUpdates() {
    // Clear existing interval if any
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Set up new interval (every 5 seconds)
    refreshInterval = setInterval(() => {
        loadInitialData();
    }, 5000);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.getElementById('notifications').appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Calculate distance between two points
function calculateDistance(lat1, lon1, lat2, lon2) {
    return window.haversineDistance(lat1, lon1, lat2, lon2);
}