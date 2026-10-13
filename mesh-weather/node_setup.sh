#!/bin/bash
# node_setup.sh   One-time Meshtastic setup for the XIAO weather node.
# Uses ~/mesh-weather/channel-url.txt if present. Stop the readers first.
for s in mesh-weather rak-reader; do
  systemctl is-active --quiet $s && { echo "Stop it first: sudo systemctl stop $s"; exit 1; }
done
P=$(ls /dev/serial/by-id/*Espressif* 2>/dev/null | head -1); P=${P:-/dev/ttyACM0}
URL=$(grep -o 'https://meshtastic.org/e/[^ ]*' ~/mesh-weather/channel-url.txt 2>/dev/null | head -1)
echo "Node on $P"
meshtastic --port "$P" --set lora.region US;                                   sleep 20
if [ -n "$URL" ]; then meshtastic --port "$P" --seturl "$URL";                 sleep 20
else echo "No channel URL saved: set the channels from the phone app (Bluetooth stays on), then carry on"; fi
meshtastic --port "$P" --set-owner "Weather Station" --set-owner-short "WX";   sleep 10
meshtastic --port "$P" --set telemetry.environment_measurement_enabled true \
  --set telemetry.environment_update_interval 300 \
  --set telemetry.device_update_interval 900;                                  sleep 20
meshtastic --port "$P" --get lora.region --get bluetooth.enabled \
  --get telemetry.environment_measurement_enabled --get telemetry.environment_update_interval
