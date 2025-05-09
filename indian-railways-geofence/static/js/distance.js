/**
 * Distance calculation utilities for the Indian Railways Geo-Fencing System
 * 
 * This file contains JavaScript implementations of the Haversine formula
 * and other geo-spatial calculations used in the system.
 */

// Calculate the great circle distance between two points using the Haversine formula
function haversineDistance(lat1, lon1, lat2, lon2) {
    // Convert latitude and longitude from degrees to radians
    lat1 = toRadians(lat1);
    lon1 = toRadians(lon1);
    lat2 = toRadians(lat2);
    lon2 = toRadians(lon2);
    
    // Haversine formula
    const dlon = lon2 - lon1;
    const dlat = lat2 - lat1;
    const a = Math.sin(dlat/2)**2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon/2)**2;
    const c = 2 * Math.asin(Math.sqrt(a));
    
    // Earth's radius in kilometers
    const r = 6371;
    
    return c * r;
}

// Calculate the bearing between two points
function bearingBetweenPoints(lat1, lon1, lat2, lon2) {
    // Convert latitude and longitude from degrees to radians
    lat1 = toRadians(lat1);
    lon1 = toRadians(lon1);
    lat2 = toRadians(lat2);
    lon2 = toRadians(lon2);
    
    // Calculate bearing
    const y = Math.sin(lon2 - lon1) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - 
              Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    
    let bearing = Math.atan2(y, x);
    
    // Convert from radians to degrees
    bearing = toDegrees(bearing);
    
    // Normalize to 0-360
    bearing = (bearing + 360) % 360;
    
    return bearing;
}

// Calculate the destination point given a starting point, bearing, and distance
function destinationPoint(lat, lon, bearing, distance) {
    // Convert to radians
    lat = toRadians(lat);
    lon = toRadians(lon);
    bearing = toRadians(bearing);
    
    // Earth's radius in kilometers
    const R = 6371;
    
    // Angular distance
    const d = distance / R;
    
    // Calculate destination point
    const lat2 = Math.asin(Math.sin(lat) * Math.cos(d) + 
                         Math.cos(lat) * Math.sin(d) * Math.cos(bearing));
    
    const lon2 = lon + Math.atan2(Math.sin(bearing) * Math.sin(d) * Math.cos(lat),
                               Math.cos(d) - Math.sin(lat) * Math.sin(lat2));
    
    // Convert back to degrees
    return {
        lat: toDegrees(lat2),
        lon: toDegrees(lon2)
    };
}

// Check if a point is inside a geo-fence (circular)
function isPointInGeoFence(pointLat, pointLon, centerLat, centerLon, radiusKm) {
    const distance = haversineDistance(pointLat, pointLon, centerLat, centerLon);
    return distance <= radiusKm;
}

// Convert degrees to radians
function toRadians(degrees) {
    return degrees * Math.PI / 180;
}

// Convert radians to degrees
function toDegrees(radians) {
    return radians * 180 / Math.PI;
}

// Export functions for use in other scripts
window.haversineDistance = haversineDistance;
window.bearingBetweenPoints = bearingBetweenPoints;
window.destinationPoint = destinationPoint;
window.isPointInGeoFence = isPointInGeoFence;