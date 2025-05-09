import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test station endpoints
def test_get_stations():
    response = client.get("/stations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Check if we have at least one station
    assert len(response.json()) > 0
    
    # Check station structure
    station = response.json()[0]
    assert "name" in station
    assert "code" in station
    assert "location" in station
    assert "type" in station["location"]
    assert "coordinates" in station["location"]

def test_get_station_by_code():
    # First get all stations
    response = client.get("/stations")
    assert response.status_code == 200
    
    # Get the first station code
    first_station = response.json()[0]
    station_code = first_station["code"]
    
    # Get station by code
    response = client.get(f"/stations/{station_code}")
    assert response.status_code == 200
    assert response.json()["code"] == station_code

def test_get_nonexistent_station():
    response = client.get("/stations/NONEXISTENT")
    assert response.status_code == 404

# Test train endpoints
def test_get_trains():
    response = client.get("/trains")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Check if we have at least one train
    assert len(response.json()) > 0
    
    # Check train structure
    train = response.json()[0]
    assert "name" in train
    assert "number" in train
    assert "location" in train
    assert "speed" in train
    assert "direction" in train
    assert "coaches" in train
    assert isinstance(train["coaches"], list)

def test_get_train_by_number():
    # First get all trains
    response = client.get("/trains")
    assert response.status_code == 200
    
    # Get the first train number
    first_train = response.json()[0]
    train_number = first_train["number"]
    
    # Get train by number
    response = client.get(f"/trains/{train_number}")
    assert response.status_code == 200
    assert response.json()["number"] == train_number

def test_get_nonexistent_train():
    response = client.get("/trains/99999")
    assert response.status_code == 404

# Test object endpoints
def test_get_objects():
    response = client.get("/objects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Check if we have at least one object
    assert len(response.json()) > 0
    
    # Check object structure
    obj = response.json()[0]
    assert "id" in obj
    assert "type" in obj
    assert "ownerId" in obj
    assert "trainNumber" in obj
    assert "coachId" in obj
    assert "location" in obj

def test_get_object_by_id():
    # First get all objects
    response = client.get("/objects")
    assert response.status_code == 200
    
    # Get the first object id
    first_object = response.json()[0]
    object_id = first_object["id"]
    
    # Get object by id
    response = client.get(f"/objects/{object_id}")
    assert response.status_code == 200
    assert response.json()["id"] == object_id

def test_get_nonexistent_object():
    response = client.get("/objects/NONEXISTENT")
    assert response.status_code == 404

# Test alert endpoints
def test_get_alerts():
    response = client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Alerts might be empty if none have been generated yet
    if len(response.json()) > 0:
        # Check alert structure
        alert = response.json()[0]
        assert "id" in alert
        assert "type" in alert
        assert "trainNumber" in alert
        assert "trainName" in alert
        assert "timestamp" in alert
        assert "resolved" in alert

# Test simulation endpoints
def test_simulate_train_movement():
    response = client.post("/simulate/train-movement")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "updated_trains" in response.json()

def test_simulate_object_theft():
    # First get all objects
    response = client.get("/objects")
    assert response.status_code == 200
    
    if len(response.json()) > 0:
        # Get the first object id
        first_object = response.json()[0]
        object_id = first_object["id"]
        
        # Simulate theft
        response = client.post(f"/simulate/object-theft/{object_id}?distance=0.1")
        assert response.status_code == 200
        assert "message" in response.json()