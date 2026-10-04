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
ls -1 /etc/nginx/sites-enabled/ > system/nginx/ENABLED.txt
m /etc/mosquitto/conf.d/dashboard.conf system/mosquitto-dashboard.conf
m $H/engine-v2/sim_light.py engine-v2/sim_light.py
m $H/engine-v2/simctl engine-v2/simctl
m $H/engine-v2/engine.py engine-v2/engine.py
m $H/engine-v2/engctl engine-v2/engctl
m $H/engine-v2/ruleslib.py engine-v2/ruleslib.py
m $H/engine-v2/mkrule.py engine-v2/mkrule.py
m $H/engine-v2/rules_api.py engine-v2/rules_api.py
m $H/engine-v2/t02.sh engine-v2/t02.sh
m /etc/systemd/system/engine-v2.service system/systemd/engine-v2.service
m /etc/logrotate.d/engine-v2 system/logrotate-engine-v2
git status --short
