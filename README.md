# MQTT Occupancy Sensor Monitor

This script monitors a Sonoff Occupancy Sensor (SNZB-06P) connected to a Zigbee2MQTT setup and outputs state changes with timestamps. It includes resilience measures to handle network interruptions and automatically reconnect when disconnected.

The script is designed to run on a Raspberry Pi with a Zigbee2MQTT setup. It utilizes the paho-mqtt library for MQTT communication and the built-in logging module for logging messages.

The scipt has been written with the help of Trae and Claude-3.7-Sonnet.

## Requirements

- Python 3.6+
- paho-mqtt library
- MQTT broker (Mosquitto) running at pi400.fritz.box
- Zigbee2MQTT with a connected Sonoff Occupancy Sensor

## Installation

1. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

2. Make the script executable (optional):

```bash
chmod +x mqtt_occupancy_monitor.py
```

## Configuration

Edit the `mqtt_occupancy_monitor.py` file to adjust the following settings if needed:

- `MQTT_BROKER`: The address of your MQTT broker (default: "pi400.fritz.box")
- `MQTT_PORT`: The port of your MQTT broker (default: 1883)
- `MQTT_TOPIC`: The topic to subscribe to (default: "zigbee2mqtt/SONOFF_SNZB-06P")
- `MQTT_HEARTBEAT_TOPIC`: Topic for heartbeat messages (default: "occupancy_monitor/heartbeat")
- `HEARTBEAT_INTERVAL`: Interval in seconds for sending heartbeat messages (default: 15)
- `KEEPALIVE_INTERVAL`: MQTT keepalive interval in seconds (default: 30)
- `MAX_INACTIVE_TIME`: Maximum time without activity before forcing reconnection (default: 60)

Make sure the `MQTT_TOPIC` matches the friendly name of your device in Zigbee2MQTT.

## Usage

Run the script:

```bash
python3 mqtt_occupancy_monitor.py
```

The script will connect to the MQTT broker and start monitoring the occupancy sensor. It will output a line with a timestamp each time the sensor state changes:

```
2023-05-15 14:23:45 PRESENCE DETECTED
2023-05-15 14:25:12 NO PRESENCE
```

To stop the script, press Ctrl+C.

## Troubleshooting

If you encounter issues:

1. Verify that your MQTT broker is running and accessible
2. Check that the MQTT topic matches your device's friendly name in Zigbee2MQTT
3. Ensure the sensor is properly connected and reporting to Zigbee2MQTT

## Resilience Features

This script includes several resilience measures to handle network interruptions:

1. **Automatic Reconnection**: The script will automatically attempt to reconnect if the connection to the MQTT broker is lost.

2. **Exponential Backoff**: Reconnection attempts use an exponential backoff strategy with jitter to prevent overwhelming the broker.

3. **Persistent Session**: The script uses a persistent session to maintain subscriptions and receive missed messages after reconnection.

4. **Connection Monitoring**: The script logs all connection state changes and reconnection attempts.

5. **Graceful Error Handling**: The script handles various error conditions gracefully and continues operation when possible.