#!/bin/bash
cd /home/brifas/dashboard-html || exit 1
H=/home/brifas
m(){ [ -f "$1" ] || { echo "MISSING $1"; return; }
  cmp -s "$1" "$2" && echo "same    $2" || { cp "$1" "$2"; echo "UPDATED $2"; }; }
m $H/backend/main.py main.py.txt
m $H/frigate/config/config.yml frigate-config.yml.txt
m $H/frigate/config/config.yml frigate-config.yml
m $H/rak_reader.py rak_reader.py
m $H/automation_engine.py automation_engine.py
m $H/backup.sh system/backup.sh
m $H/relaunch-dashboard.sh system/relaunch-dashboard.sh
m $H/.config/autostart/dashboard.desktop system/dashboard.desktop
m $H/frigate/docker-compose.yml system/docker-compose.yml
for u in dashboard-api rak-reader automation-engine; do
  m /etc/systemd/system/$u.service system/systemd/$u.service
done
for f in /etc/nginx/sites-available/*; do
  m "$f" "system/nginx/$(basename "$f")"
done
crontab -l > system/crontab.txt
grep -v '^#' /etc/dnsmasq.conf | grep . > system/dnsmasq.conf
cat /etc/ssh/sshd_config.d/*.conf > system/sshd-dropins.conf 2>/dev/null
mask(){ sed -E 's/(^| |\[)2[0-9a-f]{3}:[0-9a-f:]+(\/[0-9]+)?/\1<public-ipv6>/g'; }
ip -br addr | mask > system/ip-addr.txt
sudo ss -tulnp | mask > system/listening.txt
git status --short
