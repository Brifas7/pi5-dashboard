#!/bin/bash
# Close any running Chromium gently, then force
pkill chromium 2>/dev/null
for i in $(seq 1 10); do
  pgrep chromium >/dev/null || break
  sleep 1
done
pkill -9 chromium 2>/dev/null
sleep 1

# Wait for the dashboard API (up to 90s) so Chromium never loads a dead server
for i in $(seq 1 45); do
  curl -sf -o /dev/null http://localhost:8000/api/health && break
  sleep 2
done

nohup chromium-browser --ozone-platform=wayland --kiosk --no-sandbox --disable-session-crashed-bubble --disable-infobars --noerrdialogs http://localhost:8000/ >/dev/null 2>&1 &
disown
