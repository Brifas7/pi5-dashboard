#!/bin/bash
pkill chromium 2>/dev/null
for i in $(seq 1 10); do
  pgrep chromium >/dev/null || break
  sleep 1
done
pkill -9 chromium 2>/dev/null
sleep 1
nohup chromium-browser --ozone-platform=wayland --kiosk --no-sandbox --disable-session-crashed-bubble --disable-infobars --noerrdialogs http://localhost:8000/ >/dev/null 2>&1 &
disown
