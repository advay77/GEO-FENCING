import pytest
from app.utils.distance import haversine_distance, bearing_between_points, destination_point

# Test haversine distance calculation
def test_haversine_distance():
    # New Delhi to Mumbai distance (approximately 1150 km)
    delhi_lat, delhi_lon = 28.6425, 77.2207
    mumbai_lat, mumbai_lon = 18.9712, 72.8213
    
    distance = haversine_distance(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
    
    # Check if distance is approximately correct (within 5% margin)
    assert 1100 <= distance <= 1200
    
    # Test zero distance
    assert haversine_distance(delhi_lat, delhi_lon, delhi_lat, delhi_lon) == 0
    
    # Test small distance (within a city)
    # India Gate to Rashtrapati Bhavan (approximately 2.5 km)
    india_gate_lat, india_gate_lon = 28.6129, 77.2295
    rashtrapati_bhavan_lat, rashtrapati_bhavan_lon = 28.6141, 77.1991
    
    small_distance = haversine_distance(
        india_gate_lat, india_gate_lon,
        rashtrapati_bhavan_lat, rashtrapati_bhavan_lon
    )
    
    assert 2.0 <= small_distance <= 3.0

# Test bearing calculation
def test_bearing_between_points():
    # New Delhi to Mumbai (approximately southwest)
    delhi_lat, delhi_lon = 28.6425, 77.2207
    mumbai_lat, mumbai_lon = 18.9712, 72.8213
    
    bearing = bearing_between_points(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
    
    # Should be roughly southwest (around 225 degrees)
    assert 200 <= bearing <= 250
    
    # Test north bearing
    north_lat, north_lon = delhi_lat + 1, delhi_lon
    north_bearing = bearing_between_points(delhi_lat, delhi_lon, north_lat, north_lon)
    assert 350 <= north_bearing <= 360 or 0 <= north_bearing <= 10
    
    # Test east bearing
    east_lat, east_lon = delhi_lat, delhi_lon + 1
    east_bearing = bearing_between_points(delhi_lat, delhi_lon, east_lat, east_lon)
    assert 80 <= east_bearing <= 100

# Test destination point calculation
def test_destination_point():
    # Start at New Delhi
    delhi_lat, delhi_lon = 28.6425, 77.2207
    
    # Move 100 km east
    east_bearing = 90
    east_distance = 100
    
    east_lat, east_lon = destination_point(delhi_lat, delhi_lon, east_bearing, east_distance)
    
    # Check if longitude increased and latitude stayed approximately the same
    assert east_lon > delhi_lon
    assert abs(east_lat - delhi_lat) < 0.1
    
    # Check if distance is approximately correct
    actual_distance = haversine_distance(delhi_lat, delhi_lon, east_lat, east_lon)
    assert 95 <= actual_distance <= 105
    
    # Move 100 km south
    south_bearing = 180
    south_distance = 100
    
    south_lat, south_lon = destination_point(delhi_lat, delhi_lon, south_bearing, south_distance)
    
    # Check if latitude decreased and longitude stayed approximately the same
    assert south_lat < delhi_lat
    assert abs(south_lon - delhi_lon) < 0.1
    
    # Check if distance is approximately correct
    actual_distance = haversine_distance(delhi_lat, delhi_lon, south_lat, south_lon)
    assert 95 <= actual_distance <= 105