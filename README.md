# Fog-Fire-Detection

A distributed fog computing system for real-time fire detection using computer vision and MQTT messaging architecture.

## Project Overview

This system implements an edge computing (fog) architecture for fire detection across IoT sensors. It processes video streams from sensor cameras at the fog node level, reducing latency and bandwidth by performing fire detection inference locally, then publishing results to a cloud platform (ThingsBoard).

## Architecture

The system consists of three main components:

### 1. **Sensor** (`sensor/`)
- Captures images from connected camera
- Encodes frames as base64 and sends to MQTT broker
- Receives fire detection results from fog node
- Triggers water pump activation on high-confidence fire detection

### 2. **Fog** (`fog/`)
- Receives image streams from sensors via MQTT
- Runs fire detection ML model locally (`fire_model.pt`)
- Publishes telemetry and results back to MQTT broker
- Sends data to ThingsBoard cloud platform
- Logs response times and confidence scores

### 3. **Cloud** (`cloud/`)
- Publishes detection results to ThingsBoard IoT platform
- Handles device authentication and telemetry transmission
- Manages cloud-side data storage and visualization

## Project Structure

```
Fog-Fire-Detection/
├── fog_config.py              # Fog node configuration
├── sensor_config.py           # Sensor configuration
├── requirements.txt           # Python dependencies
├── fog/
│   ├── main.py               # Fog processing main loop
│   ├── fire_detector.py      # Fire detection inference
│   ├── fire_model.pt         # Pre-trained fire detection model
├── sensor/
│   └── main.py               # Sensor capture and publish
└── cloud/
    └── mqtt_publisher.py     # ThingsBoard integration
```

## Dependencies

- **paho-mqtt** - MQTT client for message broker communication
- **ultralytics** - YOLOv8 framework for object detection
- **opencv-python** - Computer vision and image processing
- **python-dotenv** - Environment variable management

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Sensor Configuration (`sensor_config.py`)
- `SENSOR_ID`: Unique camera identifier (default: "Cam_1")
- `SENSOR_LAT`, `SENSOR_LON`: GPS coordinates
- `BROKER_IP`: MQTT broker address

### Fog Configuration (`fog_config.py`)
- `FOG_ID`: Fog node identifier (default: "Fog_1")
- `BROKER_IP`: MQTT broker address
- `THINGSBOARD_HOST`: Cloud platform address
- `THINGSBOARD_TOKEN`: Authentication token (from `.env` file)

## Getting Started

### Prerequisites
- Python 3.8+
- Camera device for sensor
- MQTT broker (e.g., Mosquitto)
- ThingsBoard account (optional, for cloud integration)

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
Create a `.env` file in the project root:
```
FOG_TOKEN=your_thingsboard_token
```

3. **Start MQTT broker**:
```bash
# Using Mosquitto (or configure your preferred broker)
mosquitto -c /etc/mosquitto/mosquitto.conf
```

4. **Run the fog node**:
```bash
cd fog
python main.py
```

5. **Run the sensor**:
```bash
cd sensor
python main.py
```

## MQTT Topics

- **Sensor → Fog**: `$share/foggroup/fire/image`
  - Payload: JSON with base64 encoded image, sensor_id, coordinates

- **Fog → Cloud**: `v1/devices/me/telemetry`
  - Telemetry: fire detection results, confidence, location, response time

- **Fog → Sensor**: `fire/result/{sensor_id}`
  - Result: fire boolean, confidence score, processing time

## Fire Detection

The fog node uses a pre-trained YOLO model (`fire_model.pt`) for real-time fire detection:
- **Input**: JPEG image stream from sensor
- **Output**: Fire probability, confidence score, processing time
- **Threshold**: Activates water pump when confidence > 0.6

## About


This project is part of ENIS 3-1 coursework.

