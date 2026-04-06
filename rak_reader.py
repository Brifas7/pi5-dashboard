#!/usr/bin/env python3
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

API_URL = "http://localhost:8000/api/sensors/ingest"

def c_to_f(c):
    return round((c * 9/5) + 32, 1)

def on_telemetry(packet, interface):
    try:
        telemetry = packet.get('decoded', {}).get('telemetry', {})
        env = telemetry.get('environmentMetrics', {})
        if not env:
            return
        readings = []
        if 'temperature' in env:
            readings.append({"id":"rak_temp","name":"Temperature","value":c_to_f(env['temperature']),"unit":"°F"})
        if 'relativeHumidity' in env:
            readings.append({"id":"rak_humidity","name":"Humidity","value":round(env['relativeHumidity'],1),"unit":"%"})
        if 'barometricPressure' in env:
            readings.append({"id":"rak_pressure","name":"Pressure","value":round(env['barometricPressure'],1),"unit":"hPa"})
        if 'iaq' in env:
            readings.append({"id":"rak_airquality","name":"Air Quality","value":round(env['iaq'],1),"unit":"IAQ"})
        if readings:
            r = requests.post(API_URL, json={"readings": readings}, timeout=5)
            log.info(f"Ingested {len(readings)} readings: {readings}")
    except Exception as e:
        log.error(f"Error processing telemetry: {e}")

def main():
    while True:
        try:
            log.info("Connecting to RAK via USB...")
            iface = meshtastic.serial_interface.SerialInterface()
            pub.subscribe(on_telemetry, "meshtastic.receive.telemetry")
            log.info("Connected. Listening for telemetry...")
            while True:
                time.sleep(1)
        except Exception as e:
            log.error(f"Connection error: {e}. Retrying in 10s...")
            time.sleep(10)

if __name__ == "__main__":
    main()
