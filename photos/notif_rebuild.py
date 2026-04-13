#!/usr/bin/env python3
"""Replace the Notifications settings screen with full UI."""

with open('/home/brifas/dashboard-html/index.html', 'r') as f:
    content = f.read()

old = '<div id="settings-screen-notifications" class="settings-screen"><div class="settings-header"><button class="settings-btn" onclick="settingsBack(\'main\')">◀ BACK</button><span class="settings-title">🔔 NOTIFICATIONS</span><button class="settings-btn settings-btn-close" onclick="settingsClose()">✕ CLOSE</button></div><div class="settings-body"><div class="settings-section"><div style="text-align:center;padding:40px 20px;color:var(--text-sub);font-size:15px;">Notification preferences — coming soon</div></div></div></div>'

if old not in content:
    print("ERROR: Notification screen placeholder not found")
    exit(1)

new_screen = '''<div id="settings-screen-notifications" class="settings-screen"><div class="settings-header"><button class="settings-btn" onclick="settingsBack('main')">&#9664; BACK</button><span class="settings-title">&#128276; NOTIFICATIONS</span><button class="settings-btn settings-btn-close" onclick="settingsClose()">&#10005; CLOSE</button></div><div class="settings-body">
<div class="settings-section">
<div class="settings-section-label">NOTIFICATION TYPES</div>
<div class="settings-row"><div><div class="settings-row-label">Camera Motion</div><div class="settings-row-sub">Alerts when camera detects motion</div></div>
<label class="settings-toggle"><input type="checkbox" id="notif-camera-motion" onchange="notifSave()"><span class="settings-toggle-slider"></span></label></div>
<div class="settings-row"><div><div class="settings-row-label">System Alerts</div><div class="settings-row-sub">CPU temp, storage warnings</div></div>
<label class="settings-toggle"><input type="checkbox" id="notif-system-alerts" onchange="notifSave()"><span class="settings-toggle-slider"></span></label></div>
<div class="settings-row"><div><div class="settings-row-label">Sensor Alerts</div><div class="settings-row-sub">Threshold alerts from sensors</div></div>
<label class="settings-toggle"><input type="checkbox" id="notif-sensor-alerts" onchange="notifSave()"><span class="settings-toggle-slider"></span></label></div>
<div class="settings-row"><div><div class="settings-row-label">Automation Alerts</div><div class="settings-row-sub">Notifications from automation rules</div></div>
<label class="settings-toggle"><input type="checkbox" id="notif-auto-alerts" onchange="notifSave()"><span class="settings-toggle-slider"></span></label></div>
</div>

<div class="settings-section">
<div class="settings-section-label">SENSOR ALERT THRESHOLDS</div>
<div id="notif-thresholds-list" style="display:flex;flex-direction:column;gap:8px;"></div>
<div style="display:flex;gap:8px;margin-top:8px;">
<select id="notif-thresh-sensor" class="settings-select" style="flex:2;">
<option value="rak_temp">Temperature</option>
<option value="rak_humidity">Humidity</option>
<option value="rak_pressure">Barometric Pressure</option>
<option value="rak_airquality">Air Quality</option>
<option value="rak_dewpoint">Dew Point</option>
</select>
<select id="notif-thresh-op" class="settings-select" style="flex:1;">
<option value="below">Below</option>
<option value="above">Above</option>
</select>
<input type="number" id="notif-thresh-value" class="settings-select" placeholder="Value" style="flex:1;max-width:80px;">
<button class="settings-btn" onclick="notifAddThreshold()">ADD</button>
</div>
</div>

<div class="settings-section">
<div class="settings-section-label">QUIET HOURS</div>
<div class="settings-row"><div><div class="settings-row-label">Start</div><div class="settings-row-sub">Suppress notifications after this time</div></div>
<input type="time" id="notif-quiet-start" class="settings-select" style="width:130px;" onchange="notifSave()"></div>
<div class="settings-row"><div><div class="settings-row-label">End</div><div class="settings-row-sub">Resume notifications at this time</div></div>
<input type="time" id="notif-quiet-end" class="settings-select" style="width:130px;" onchange="notifSave()"></div>
</div>

<div class="settings-section">
<div class="settings-section-label">SOUND</div>
<div class="settings-row"><div><div class="settings-row-label">Audible Alert</div><div class="settings-row-sub">Play sound on kiosk for notifications</div></div>
<label class="settings-toggle"><input type="checkbox" id="notif-sound" onchange="notifSave()"><span class="settings-toggle-slider"></span></label></div>
</div>

<div class="settings-section">
<div class="settings-section-label">NOTIFICATION HISTORY</div>
<div id="notif-history-list" style="display:flex;flex-direction:column;gap:4px;max-height:300px;overflow-y:auto;"></div>
<button class="settings-btn" onclick="notifLoadHistory()" style="width:100%;margin-top:8px;">REFRESH HISTORY</button>
</div>

</div></div>'''

content = content.replace(old, new_screen)

# Add the JS functions
funcs = '''
<script>
var _notifSettings = {};
var _notifThresholds = [];

async function notifLoad() {
  try {
    var r = await fetch('/api/notifications/settings');
    _notifSettings = await r.json();
    document.getElementById('notif-camera-motion').checked = _notifSettings.camera_motion !== false;
    document.getElementById('notif-system-alerts').checked = _notifSettings.system_alerts !== false;
    document.getElementById('notif-sensor-alerts').checked = _notifSettings.sensor_alerts !== false;
    document.getElementById('notif-auto-alerts').checked = _notifSettings.automation_alerts !== false;
    document.getElementById('notif-sound').checked = _notifSettings.sound === true;
    document.getElementById('notif-quiet-start').value = _notifSettings.quiet_start || '';
    document.getElementById('notif-quiet-end').value = _notifSettings.quiet_end || '';
    _notifThresholds = _notifSettings.sensor_thresholds || [];
    notifRenderThresholds();
    notifLoadHistory();
  } catch(e) {}
}

async function notifSave() {
  var settings = {
    camera_motion: document.getElementById('notif-camera-motion').checked,
    system_alerts: document.getElementById('notif-system-alerts').checked,
    sensor_alerts: document.getElementById('notif-sensor-alerts').checked,
    automation_alerts: document.getElementById('notif-auto-alerts').checked,
    sound: document.getElementById('notif-sound').checked,
    quiet_start: document.getElementById('notif-quiet-start').value,
    quiet_end: document.getElementById('notif-quiet-end').value,
    sensor_thresholds: _notifThresholds
  };
  try {
    await fetch('/api/notifications/settings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(settings)
    });
  } catch(e) {}
}

function notifRenderThresholds() {
  var el = document.getElementById('notif-thresholds-list');
  var names = {rak_temp: 'Temperature', rak_humidity: 'Humidity', rak_pressure: 'Pressure', rak_airquality: 'Air Quality', rak_dewpoint: 'Dew Point'};
  var units = {rak_temp: '\\u00b0F', rak_humidity: '%', rak_pressure: ' hPa', rak_airquality: ' IAQ', rak_dewpoint: '\\u00b0F'};
  if (_notifThresholds.length === 0) {
    el.innerHTML = '<div style="color:var(--text-sub);font-size:13px;padding:4px;">No thresholds set</div>';
    return;
  }
  el.innerHTML = _notifThresholds.map(function(t, i) {
    return '<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(var(--accent-rgb),0.06);border-radius:6px;">' +
      '<span style="flex:1;font-size:14px;font-weight:600;">' + (names[t.sensor] || t.sensor) + ' ' + t.op + ' ' + t.value + (units[t.sensor] || '') + '</span>' +
      '<button class="settings-btn" style="padding:2px 10px;font-size:11px;background:rgba(220,40,40,0.12);border-color:rgba(220,40,40,0.35);color:#fca5a5;" onclick="notifRemoveThreshold(' + i + ')">\\u2715</button></div>';
  }).join('');
}

function notifAddThreshold() {
  var sensor = document.getElementById('notif-thresh-sensor').value;
  var op = document.getElementById('notif-thresh-op').value;
  var value = document.getElementById('notif-thresh-value').value;
  if (!value) { alert('Enter a value.'); return; }
  _notifThresholds.push({sensor: sensor, op: op, value: parseFloat(value)});
  notifRenderThresholds();
  notifSave();
  document.getElementById('notif-thresh-value').value = '';
}

function notifRemoveThreshold(idx) {
  _notifThresholds.splice(idx, 1);
  notifRenderThresholds();
  notifSave();
}

async function notifLoadHistory() {
  var el = document.getElementById('notif-history-list');
  try {
    var r = await fetch('/api/notifications/history?limit=50');
    var d = await r.json();
    var notifs = d.notifications || [];
    if (notifs.length === 0) {
      el.innerHTML = '<div style="color:var(--text-sub);font-size:13px;padding:8px 0;">No notification history</div>';
      return;
    }
    el.innerHTML = notifs.map(function(n) {
      var dt = new Date(n.timestamp * 1000);
      var time = dt.toLocaleString();
      var colors = {camera: '#3b82f6', system: '#ef4444', sensor: '#22c55e', automation: '#a855f7'};
      var color = colors[n.type] || 'var(--text-sub)';
      return '<div style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(var(--accent-rgb),0.04);border-radius:4px;">' +
        '<span style="font-size:16px;">' + (n.icon || '\\u2022') + '</span>' +
        '<div style="flex:1;"><div style="font-size:13px;font-weight:600;">' + (n.source || '') + ' \\u2014 ' + (n.message || '') + '</div>' +
        '<div style="font-size:11px;color:var(--text-sub);">' + time + '</div></div>' +
        '<div style="font-size:10px;font-weight:700;color:' + color + ';letter-spacing:1px;text-transform:uppercase;">' + (n.type || '') + '</div></div>';
    }).join('');
  } catch(e) {
    el.innerHTML = '<div style="color:var(--text-sub);font-size:13px;">Failed to load history</div>';
  }
}

(function() {
  var _prevNav = window.settingsNav;
  if (_prevNav) {
    window.settingsNav = function(screen) {
      _prevNav(screen);
      if (screen === 'notifications') notifLoad();
    };
  }
})();
</script>
'''

body_idx = content.rfind('</body>')
if body_idx > 0:
    content = content[:body_idx] + funcs + content[body_idx:]
    print("Functions added")

with open('/home/brifas/dashboard-html/index.html', 'w') as f:
    f.write(content)

print("Notifications screen rebuilt successfully")
print(f"File size: {len(content)} characters")
