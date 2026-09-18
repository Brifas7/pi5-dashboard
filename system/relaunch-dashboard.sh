#!/bin/bash
pkill -9 chromium 2>/dev/null
pkill -9 chromium-browser 2>/dev/null
sleep 3
while pgrep -x chromium > /dev/null || pgrep -x chromium-browser > /dev/null; do
  sleep 1
done
chromium-browser --ozone-platform=wayland --kiosk --no-sandbox --disable-session-crashed-bubble --disable-infobars --noerrdialogs http://localhost:8000/ &
disown
