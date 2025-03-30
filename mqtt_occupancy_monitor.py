#!/usr/bin/env python3

import json
import time
import datetime
import random
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties

# MQTT Configuration
MQTT_BROKER = "pi400.fritz.box"
MQTT_PORT = 1883
# Adjust this topic to match your zigbee2mqtt configuration
# This is typically zigbee2mqtt/DEVICE_FRIENDLY_NAME
# Updated to match the SONOFF_SNZB-06P sensor
MQTT_TOPIC = "zigbee2mqtt/SONOFF_SNZB-06P"
# Topic for heartbeat messages
MQTT_HEARTBEAT_TOPIC = "occupancy_monitor/heartbeat"
# Heartbeat interval in seconds (shorter than keepalive)
HEARTBEAT_INTERVAL = 15
# Keepalive interval in seconds (shorter than default 60s)
KEEPALIVE_INTERVAL = 30
# Maximum time without receiving messages before forcing reconnection
MAX_INACTIVE_TIME = 60  # seconds

# Reconnection parameters
RECONNECT_DELAY_MIN = 1  # Minimum delay in seconds
RECONNECT_DELAY_MAX = 60  # Maximum delay in seconds
RECONNECT_ATTEMPTS = 0  # Counter for reconnection attempts
MAX_RECONNECT_ATTEMPTS = -1  # -1 means infinite attempts

# Track the last known state to only report changes
last_occupancy_state = None

# Flag to track if we're in a reconnection loop
reconnecting = False

# Track the last time we received any message from the broker
last_activity_time = None

# Callback when connecting to the MQTT broker
def on_connect(client, userdata, flags, rc, properties=None):
    global reconnecting, RECONNECT_ATTEMPTS
    
    if rc == 0:
        print(f"{get_timestamp()} Connected to MQTT Broker at {MQTT_BROKER}")
        # Subscribe to the sensor topic
        client.subscribe(MQTT_TOPIC)
        print(f"{get_timestamp()} Subscribed to {MQTT_TOPIC}")
        print(f"{get_timestamp()} Monitoring occupancy sensor state changes...")
        
        # Reset reconnection parameters on successful connection
        if reconnecting:
            print(f"{get_timestamp()} Reconnection successful after {RECONNECT_ATTEMPTS} attempts")
            reconnecting = False
            RECONNECT_ATTEMPTS = 0
    else:
        print(f"{get_timestamp()} Failed to connect to MQTT Broker, return code: {rc}")

# Callback when disconnecting from the MQTT broker
def on_disconnect(client, userdata, rc, properties=None, reason_code=None):
    global reconnecting
    
    if rc != 0:
        print(f"{get_timestamp()} Unexpected disconnection from MQTT Broker, return code: {rc}")
        reconnecting = True
    else:
        print(f"{get_timestamp()} Disconnected from MQTT Broker")

# Calculate exponential backoff delay with jitter for reconnection
def get_reconnect_delay():
    global RECONNECT_ATTEMPTS
    RECONNECT_ATTEMPTS += 1
    
    # Calculate delay with exponential backoff and jitter
    delay = min(RECONNECT_DELAY_MAX, RECONNECT_DELAY_MIN * (2 ** (RECONNECT_ATTEMPTS - 1)))
    # Add jitter (random value between 0 and 1 second)
    jitter = random.uniform(0, 1)
    
    return delay + jitter

# Callback when a message is received from the broker
def on_message(client, userdata, msg, properties=None):
    global last_occupancy_state
    
    try:
        # Parse the JSON payload
        payload = json.loads(msg.payload.decode())
        
        # Check if the message contains occupancy information
        if 'occupancy' in payload:
            current_state = payload['occupancy']
            
            # Only output when the state changes
            if current_state != last_occupancy_state:
                state_text = "PRESENCE DETECTED" if current_state else "NO PRESENCE"
                print(f"{get_timestamp()} {state_text}")
                last_occupancy_state = current_state
    except json.JSONDecodeError:
        print(f"{get_timestamp()} Error: Received non-JSON message")
    except Exception as e:
        print(f"{get_timestamp()} Error processing message: {e}")

# Get current timestamp in a readable format
def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Main function
def main():
    # Create MQTT client instance
    # For MQTT v5, we don't use clean_session parameter as it's not supported
    client = mqtt.Client(
        client_id="occupancy_monitor", 
        protocol=mqtt.MQTTv5, 
        callback_api_version=CallbackAPIVersion.VERSION2
    )
    
    # For MQTT v5, clean session behavior is controlled during connection
    # We'll set clean_start=False when connecting
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Set automatic reconnect parameters
    client.reconnect_delay_set(min_delay=RECONNECT_DELAY_MIN, max_delay=RECONNECT_DELAY_MAX)
    
    # Enable automatic reconnection
    # For MQTT v5, we set clean_start=False during connection
    # In paho-mqtt 1.6.1, Properties requires a packetType parameter
    # CONNECT packet type is 1 for MQTT v5
    connect_properties = Properties(packetType=1)  # 1 is for CONNECT packet
    client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=KEEPALIVE_INTERVAL, clean_start=False, properties=connect_properties)
    
    # Start the network loop
    try:
        # This will block and process network traffic
        client.loop_start()
        
        # Main loop to handle reconnection logic
        while True:
            try:
                # Check if we need to reconnect manually
                if reconnecting and not client.is_connected():
                    # If we've reached the maximum number of reconnection attempts and it's not infinite
                    if MAX_RECONNECT_ATTEMPTS > 0 and RECONNECT_ATTEMPTS >= MAX_RECONNECT_ATTEMPTS:
                        print(f"{get_timestamp()} Maximum reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached. Exiting.")
                        break
                    
                    delay = get_reconnect_delay()
                    print(f"{get_timestamp()} Attempting to reconnect in {delay:.2f} seconds (attempt {RECONNECT_ATTEMPTS})...")
                    time.sleep(delay)
                    
                    try:
                        client.reconnect()
                    except Exception as e:
                        print(f"{get_timestamp()} Reconnection attempt failed: {e}")
                
                # Small sleep to prevent CPU hogging
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n{get_timestamp()} Script terminated by user")
                break
            except Exception as e:
                print(f"{get_timestamp()} Error in main loop: {e}")
                # Continue the loop to allow reconnection
    
    except Exception as e:
        print(f"{get_timestamp()} Critical error: {e}")
    finally:
        # Stop the network loop and disconnect
        client.loop_stop()
        if client.is_connected():
            client.disconnect()
            print(f"{get_timestamp()} Disconnected from MQTT broker")

if __name__ == "__main__":
    main()