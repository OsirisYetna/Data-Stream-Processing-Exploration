"""
stations-activity.py
Listens to 'velib-stations', detects station status changes,
and sends updates to 'stations-status'.
"""

import time
import json
from kafka import KafkaConsumer, KafkaProducer

# Config 
BROKER = "localhost:9092"
INPUT_TOPIC = "velib-stations"
OUTPUT_TOPIC = "stations-status"
GROUP_ID = "stations-activity-app"

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BROKER,
    group_id=GROUP_ID,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# In-memory station states 
station_states = {}

print("Listening to topic:", INPUT_TOPIC)
print("Will send updates to topic:", OUTPUT_TOPIC)


for message in consumer:
    station_data = message.value["station_data"]
    station_number = station_data["number"]

    # Current station status
    current_status = {
        "available_bikes": station_data.get("available_bikes", 0),
        "available_bike_stands": station_data.get("available_bike_stands", 0)
    }

    # Check if status has changed
    prev_status = station_states.get(station_number)
    if prev_status != current_status:
        # Send update to 'stations-status'
        update_msg = {
            "station_number": station_number,
            "name": station_data.get("name"),
            "contract_name": station_data.get("contract_name"),
            "timestamp": message.value.get("timestamp"),
            "available_bikes": current_status["available_bikes"],
            "available_bike_stands": current_status["available_bike_stands"]
        }

        producer.send(OUTPUT_TOPIC, update_msg)
        producer.flush()
        print("Sending update for station {} to topic {}".format(station_number, OUTPUT_TOPIC))

        # Update in-memory state
        station_states[station_number] = current_status

    # Small delay to mimic your style (optional)
    time.sleep(1)

