# Indian Railways Geo-Fencing System

A real-time geo-fencing system for Indian Railways that provides alerts for station proximity and object theft detection.

## Features

- **Real-time Location Tracking**
  - Tracks train locations using GPS coordinates
  - Updates object locations within trains
  - Calculates distances using the Haversine formula

- **Geo-fencing Logic**
  - Station proximity detection (1 km radius)
  - Object theft detection based on coach geo-fence boundaries
  - Configurable geo-fence radius per coach

- **Alert System**
  - Station entry alerts when trains approach stations
  - Theft alerts when objects move outside their assigned coach
  - Alert resolution when conditions return to normal

- **Simulation Capabilities**
  - Simulates train movement along tracks
  - Simulates object movement (including potential theft)
  - Provides testing endpoints for system validation

## Technology Stack

- **Backend**: FastAPI
- **Database**: MongoDB
- **Geo-spatial Calculations**: Haversine Formula
- **API Documentation**: Swagger UI (via FastAPI)

## Installation

1. Clone the repository: