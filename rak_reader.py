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
        if 'temperature' in env and 'relativeHumidity' in env:
            import math
            tc=env['temperature']
            rh=env['relativeHumidity']
            a,b=17.27,237.7
            alpha=a*tc/(b+tc)+math.log(rh/100.0)
            dp_c=b*alpha/(a-alpha)
            readings.append({'id':'rak_dewpoint','name':'Dew Point','value':c_to_f(dp_c),'unit':'°F'})
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
            iface = None
            iface = meshtastic.serial_interface.SerialInterface("/dev/ttyACM0")
            pub.subscribe(on_telemetry, "meshtastic.receive.telemetry")
            log.info("Connected. Listening for telemetry...")
            # Register weather station as a system in device registry
            try:
                requests.post("http://localhost:8000/api/devices/register", json={
                    "id": "rak_weather_station",
                    "name": "RAK WisBlock Weather Station",
                    "category": "system",
                    "type": "weather_station",
                    "summary": "RAK4631 + RAK1906 Environmental Sensor",
                    "ip": "/dev/ttyACM0"
                }, timeout=5)
                log.info("Weather station registered")
            except Exception as e:
                log.warning(f"Registration failed: {e}")
            while True:
                time.sleep(1)
        except Exception as e:
            log.error(f"Connection error: {e}. Retrying in 10s...")
        finally:
            if iface:
                try:
                    iface.close()
                    log.info("Serial interface closed.")
                except Exception:
                    pass
        time.sleep(10)

if __name__ == "__main__":
    main()
