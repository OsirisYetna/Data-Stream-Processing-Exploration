"""
Simplified version of ingest-data.py
Fetches JCDecaux bike station data and sends it to Kafka
"""

import time
import requests
import json
from datetime import datetime
from kafka import KafkaProducer

# --- Configuration ---
API_KEY = "316618c901fc96f9b164cf19fde014d015ec28eb"
API_URL = "https://api.jcdecaux.com/vls/v1/stations"
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "velib-stations"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')

)

i = 0
while True:

    # Get station data from JCDecaux API
    response = requests.get(API_URL, params={"apiKey": API_KEY}, timeout=10)
    stations = response.json()
    # Send the datas
    producer.send(TOPIC_NAME, stations)
    print(f"[{i}] Sent {len(stations)} stations to topic '{TOPIC_NAME}'")
    i += 1
    time.sleep(10)

# make sure id (number ne fonctionne pas) position geo lat long par ex
# 