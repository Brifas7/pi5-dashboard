#!/usr/bin/env python3
"""Replace the Operations submenu with new UI including weather station detail."""

with open('/home/brifas/dashboard-html/index.html', 'r') as f:
    content = f.read()

# Find Operations block boundaries
ops_style_start = content.find('<!-- OPERATIONS SUBMENU -->')
if ops_style_start < 0:
    # Try finding by the style block
    ops_style_start = content.find('#ops-overlay { font-family:')
    if ops_style_start > 0:
        # Back up to the <style> tag
        ops_style_start = content.rfind('<style>', 0, ops_style_start)

settings_start = content.find('<!-- SETTINGS SUBMENU -->')

if ops_style_start < 0:
    print("ERROR: Operations block start not found")
    exit(1)
if settings_start < 0:
    print("ERROR: Settings block not found")
    exit(1)

print(f"Replacing from {ops_style_start} to {settings_start}")
print(f"That's {settings_start - ops_style_start} characters")

before = content[:ops_style_start]
after = content[settings_start:]

new_ops = '''<!-- OPERATIONS SUBMENU -->
<style>
#ops-overlay{font-family:'Rajdhani',sans-serif;color:var(--text);}
.ops-header{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;flex-shrink:0;background:rgba(10,20,60,0.7);border-bottom:1px solid rgba(var(--accent-rgb),0.25);}
.ops-title{font-size:20px;font-weight:700;letter-spacing:2px;color:var(--text);}
.ops-btn{background:rgba(var(--accent-rgb),0.15);border:1px solid rgba(var(--accent-rgb),0.35);color:var(--text);border-radius:8px;padding:8px 18px;font-family:'Rajdhani',sans-serif;font-size:14px;font-weight:700;letter-spacing:1px;cursor:pointer;transition:background 0.2s;}
.ops-btn:hover{background:rgba(var(--accent-rgb),0.3);}
.ops-btn-close{background:rgba(220,40,40,0.12);border-color:rgba(220,40,40,0.35);color:#fca5a5;}
.ops-btn-close:hover{background:rgba(220,40,40,0.28);}
.ops-screen{display:none;flex-direction:column;height:100%;}
.ops-screen.active{display:flex;}
.ops-system-item{display:flex;align-items:center;gap:16px;background:rgba(var(--accent-rgb),0.1);border:1px solid rgba(var(--accent-rgb),0.25);border-radius:10px;padding:16px 20px;cursor:pointer;transition:background 0.2s;}
.ops-system-item:hover{background:rgba(var(--accent-rgb),0.2);}
.ops-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.ops-dot-on{background:#22c55e;box-shadow:0 0 6px rgba(34,197,94,0.7);}
.ops-dot-off{background:#ef4444;}
.ops-section{background:rgba(var(--accent-rgb),0.08);border:1px solid rgba(var(--accent-rgb),0.2);border-radius:12px;padding:18px 22px;display:flex;flex-direction:column;gap:12px;}
.ops-section-label{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--text-sub);text-transform:uppercase;}
.ops-reading-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.ops-reading-card{display:flex;flex-direction:column;align-items:center;padding:12px 8px;background:rgba(var(--accent-rgb),0.12);border-radius:10px;border:1px solid rgba(var(--accent-rgb),0.25);}
.ops-reading-label{font-size:12px;color:var(--text-sub);text-transform:uppercase;letter-spacing:1px;font-weight:600;}
.ops-reading-val{font-family:'Orbitron',monospace;font-size:22px;color:var(--text);font-weight:700;}
.ops-reading-trend{font-size:11px;font-weight:700;margin-top:2px;}
.ops-reading-big{grid-column:1/-1;padding:16px 8px;}
.ops-reading-big .ops-reading-val{font-size:36px;}
.ops-stat-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(var(--accent-rgb),0.1);}
.ops-stat-row:last-child{border-bottom:none;}
.ops-stat-label{font-size:14px;color:var(--text-sub);font-weight:600;}
.ops-stat-val{font-family:'Orbitron',monospace;font-size:15px;font-weight:700;color:var(--text);}
.ops-graph-wrap{background:rgba(0,0,0,0.3);border:1px solid rgba(var(--accent-rgb),0.15);border-radius:8px;padding:12px;height:200px;position:relative;}
.ops-range-bar{display:flex;gap:6px;margin-bottom:8px;}
.ops-range-btn{background:rgba(var(--accent-rgb),0.1);border:1px solid rgba(var(--accent-rgb),0.25);color:var(--text-sub);border-radius:6px;padding:4px 10px;font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:700;cursor:pointer;}
.ops-range-btn.active{background:rgba(var(--accent-rgb),0.35);border-color:var(--accent);color:var(--text);}
.ops-empty{padding:40px;text-align:center;color:var(--text-sub);font-size:16px;font-weight:600;letter-spacing:1px;line-height:2;}
.ops-empty-icon{font-size:48px;display:block;margin-bottom:16px;opacity:0.4;}
</style>

<div id="ops-overlay" style="display:none;position:fixed;inset:0;background:var(--overlay-bg);z-index:1000;flex-direction:column;">

<!-- SYSTEM LIST -->
<div id="ops-screen-list" class="ops-screen">
<div class="ops-header">
<span class="ops-title">&#9881;&#65039; OPERATIONS</span>
<button class="ops-btn ops-btn-close" onclick="opsClose()">&#10005; CLOSE</button>
</div>
<div style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px;" id="ops-system-list"></div>
</div>

<!-- SYSTEM DETAIL -->
<div id="ops-screen-detail" class="ops-screen">
<div class="ops-header">
<span id="ops-detail-title" class="ops-title"></span>
<div style="display:flex;gap:10px;">
<button class="ops-btn" onclick="opsBackToList()">&#9664; BACK</button>
<button class="ops-btn ops-btn-close" onclick="opsClose()">&#10005; CLOSE</button>
</div>
</div>
<div id="ops-detail-body" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;"></div>
</div>

<!-- HISTORY / GRAPHS -->
<div id="ops-screen-history" class="ops-screen">
<div class="ops-header">
<span id="ops-history-title" class="ops-title">&#128200; HISTORY</span>
<div style="display:flex;gap:10px;">
<button class="ops-btn" onclick="opsBackToDetail()">&#9664; BACK</button>
<button class="ops-btn ops-btn-close" onclick="opsClose()">&#10005; CLOSE</button>
</div>
</div>
<div style="padding:12px 20px 0;display:flex;gap:8px;flex-shrink:0;">
<select class="ops-btn" id="ops-hist-sensor" onchange="opsLoadGraph()" style="flex:1;">
<option value="rak_temp">Temperature</option>
<option value="rak_humidity">Humidity</option>
<option value="rak_pressure">Barometric Pressure</option>
<option value="rak_airquality">Air Quality</option>
<option value="rak_dewpoint">Dew Point</option>
</select>
</div>
<div class="ops-range-bar" style="padding:8px 20px 0;" id="ops-hist-range">
<button class="ops-range-btn active" onclick="opsSetHistRange('24h',this)">24H</button>
<button class="ops-range-btn" onclick="opsSetHistRange('7d',this)">7D</button>
<button class="ops-range-btn" onclick="opsSetHistRange('30d',this)">30D</button>
<button class="ops-range-btn" onclick="opsSetHistRange('6m',this)">6M</button>
<button class="ops-range-btn" onclick="opsSetHistRange('1y',this)">1Y</button>
</div>
<div style="padding:12px 20px;flex:1;display:flex;flex-direction:column;min-height:0;">
<div class="ops-graph-wrap" style="flex:1;">
<canvas id="ops-hist-canvas"></canvas>
</div>
<div id="ops-hist-stats" style="margin-top:12px;"></div>
</div>
</div>

</div>

<script>
var _ops = { systems: [], currentSystem: null, currentRange: '24h', histChart: null };

function _opsScreen(id) {
  document.querySelectorAll('.ops-screen').forEach(function(s) { s.classList.remove('active'); });
  var el = document.getElementById('ops-screen-' + id);
  if (el) el.classList.add('active');
}

function _opsFmt(name) {
  return name.replace(/[-_]/g, ' ').replace(/\b\w/g, function(c) { return c.toUpperCase(); });
}

async function opsOpen() {
  var overlay = document.getElementById('ops-overlay');
  overlay.style.display = 'flex';
  overlay.style.flexDirection = 'column';
  _opsScreen('list');
  try {
    var r = await fetch('/api/systems');
    var d = await r.json();
    _ops.systems = d.systems || [];
  } catch(e) { _ops.systems = []; }
  _opsRenderList();
}

function opsClose() {
  if (typeof _isMobile === 'function' && _isMobile()) return _mobileClose();
  document.getElementById('ops-overlay').style.display = 'none';
}

function opsBackToList() { _opsScreen('list'); _opsRenderList(); }
function opsBackToDetail() { _opsScreen('detail'); }

function _opsRenderList() {
  var el = document.getElementById('ops-system-list');
  if (_ops.systems.length === 0) {
    el.innerHTML = '<div class="ops-empty"><span class="ops-empty-icon">&#9881;&#65039;</span>No systems registered.<br>Systems appear automatically when connected.</div>';
    return;
  }
  el.innerHTML = _ops.systems.map(function(sys, i) {
    var online = sys.online === true || sys.online === 1;
    return '<div class="ops-system-item" onclick="opsOpenDetail(' + i + ')">' +
      '<div class="ops-dot ' + (online ? 'ops-dot-on' : 'ops-dot-off') + '"></div>' +
      '<div style="flex:1;"><div style="font-size:18px;font-weight:700;">' + _opsFmt(sys.name) + '</div>' +
      '<div style="font-size:13px;color:var(--text-sub);">' + (sys.summary || sys.type || '') + '</div></div>' +
      '<span style="font-size:11px;font-weight:700;letter-spacing:1px;padding:3px 10px;border-radius:4px;' +
      (online ? 'color:#22c55e;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);' : 'color:#f87171;background:rgba(220,40,40,0.12);border:1px solid rgba(220,40,40,0.3);') +
      '">' + (online ? 'ONLINE' : 'OFFLINE') + '</span></div>';
  }).join('');
}

async function opsOpenDetail(idx) {
  _ops.currentSystem = _ops.systems[idx];
  var sys = _ops.currentSystem;
  document.getElementById('ops-detail-title').textContent = _opsFmt(sys.name);

  if (sys.type === 'weather_station' || sys.id === 'rak_weather_station') {
    await _opsRenderWeatherStation();
  } else {
    _opsRenderGenericSystem(sys);
  }
  _opsScreen('detail');
}

async function _opsRenderWeatherStation() {
  var body = document.getElementById('ops-detail-body');
  body.innerHTML = '<div class="ops-empty">Loading...</div>';

  // Fetch current readings
  var readings = {};
  try {
    var r = await fetch('/api/sensors');
    var d = await r.json();
    (d.sensors || []).forEach(function(s) { readings[s.id] = s; });
  } catch(e) {}

  // Fetch averages
  var avgs = {};
  try {
    var r2 = await fetch('/api/sensors/averages');
    avgs = await r2.json();
  } catch(e) {}

  var temp = readings.rak_temp;
  var humid = readings.rak_humidity;
  var pres = readings.rak_pressure;
  var aqi = readings.rak_airquality;
  var dew = readings.rak_dewpoint;

  var lastSeen = '';
  if (temp && temp.last_seen) {
    var diff = Math.floor(Date.now()/1000 - temp.last_seen);
    if (diff < 60) lastSeen = diff + 's ago';
    else if (diff < 3600) lastSeen = Math.floor(diff/60) + 'm ago';
    else lastSeen = Math.floor(diff/3600) + 'h ago';
  }

  var html = '';

  // Status
  html += '<div class="ops-section"><div class="ops-section-label">STATUS</div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Connection</span><span class="ops-stat-val" style="color:#22c55e;">Online</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Last Reading</span><span class="ops-stat-val">' + (lastSeen || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Device</span><span class="ops-stat-val" style="font-family:Rajdhani,sans-serif;">RAK4631 + RAK1906</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Interface</span><span class="ops-stat-val" style="font-family:Rajdhani,sans-serif;">USB /dev/ttyACM0</span></div>';
  html += '</div>';

  // Live readings
  html += '<div class="ops-section"><div class="ops-section-label">LIVE READINGS</div>';
  html += '<div class="ops-reading-grid">';
  html += '<div class="ops-reading-card ops-reading-big"><div class="ops-reading-label">Temperature</div><div class="ops-reading-val">' + (temp ? temp.last_value + '\\u00b0F' : '—') + '</div></div>';
  html += '<div class="ops-reading-card"><div class="ops-reading-label">Humidity</div><div class="ops-reading-val">' + (humid ? humid.last_value + '%' : '—') + '</div></div>';
  html += '<div class="ops-reading-card"><div class="ops-reading-label">Barometric</div><div class="ops-reading-val">' + (pres ? pres.last_value + '</div><div class="ops-reading-label" style="font-size:10px;">hPa</div>' : '—</div>') + '</div>';
  html += '<div class="ops-reading-card"><div class="ops-reading-label">Air Quality</div><div class="ops-reading-val">' + (aqi ? Math.round(aqi.last_value) + '</div><div class="ops-reading-label" style="font-size:10px;">IAQ</div>' : '—</div>') + '</div>';
  html += '<div class="ops-reading-card"><div class="ops-reading-label">Dew Point</div><div class="ops-reading-val">' + (dew ? dew.last_value + '\\u00b0F' : '—') + '</div></div>';
  html += '</div></div>';

  // Averages
  html += '<div class="ops-section"><div class="ops-section-label">AVERAGES</div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Temp (24h avg)</span><span class="ops-stat-val">' + (avgs.temp_24h || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Temp (7d avg)</span><span class="ops-stat-val">' + (avgs.temp_7d || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Temp (30d avg)</span><span class="ops-stat-val">' + (avgs.temp_30d || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Temp (24h high)</span><span class="ops-stat-val" style="color:#ef4444;">' + (avgs.temp_24h_high || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Temp (24h low)</span><span class="ops-stat-val" style="color:#3b82f6;">' + (avgs.temp_24h_low || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Humidity (24h avg)</span><span class="ops-stat-val">' + (avgs.humid_24h || '—') + '</span></div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Pressure (24h avg)</span><span class="ops-stat-val">' + (avgs.pres_24h || '—') + '</span></div>';
  html += '</div>';

  // History button
  html += '<button class="ops-btn" onclick="opsShowHistory()" style="width:100%;padding:14px;font-size:16px;">&#128200; VIEW FULL HISTORY</button>';

  body.innerHTML = html;
}

function _opsRenderGenericSystem(sys) {
  var body = document.getElementById('ops-detail-body');
  var online = sys.online === true || sys.online === 1;

  var html = '<div class="ops-section"><div class="ops-section-label">CONNECTION</div>';
  html += '<div class="ops-stat-row"><span class="ops-stat-label">Status</span><span class="ops-stat-val" style="color:' + (online ? '#22c55e' : '#f87171') + ';">' + (online ? 'ONLINE' : 'OFFLINE') + '</span></div>';
  if (sys.ip) html += '<div class="ops-stat-row"><span class="ops-stat-label">IP</span><span class="ops-stat-val" style="font-family:Rajdhani,sans-serif;">' + sys.ip + '</span></div>';
  if (sys.uptime) html += '<div class="ops-stat-row"><span class="ops-stat-label">Uptime</span><span class="ops-stat-val" style="font-family:Rajdhani,sans-serif;">' + sys.uptime + '</span></div>';
  if (sys.rssi) html += '<div class="ops-stat-row"><span class="ops-stat-label">Signal</span><span class="ops-stat-val">' + sys.rssi + ' dBm</span></div>';
  html += '</div>';

  if (sys.sensors && sys.sensors.length > 0) {
    html += '<div class="ops-section"><div class="ops-section-label">SENSORS</div>';
    sys.sensors.forEach(function(s) {
      html += '<div class="ops-stat-row"><span class="ops-stat-label">' + s.name + '</span><span class="ops-stat-val">' + s.value + ' ' + (s.unit || '') + '</span></div>';
    });
    html += '</div>';
  }

  if (sys.controls && sys.controls.length > 0) {
    html += '<div class="ops-section"><div class="ops-section-label">CONTROLS</div>';
    sys.controls.forEach(function(ctrl) {
      if (ctrl.type === 'toggle') {
        html += '<div class="ops-stat-row"><span class="ops-stat-label">' + ctrl.name + '</span>' +
          '<label class="auto-toggle"><input type="checkbox" ' + (ctrl.state === 'on' ? 'checked' : '') +
          ' onchange="opsControl(\\'' + sys.id + '\\',\\'' + ctrl.id + '\\',\\'toggle\\',this.checked)"><span class="auto-toggle-slider"></span></label></div>';
      } else if (ctrl.type === 'momentary') {
        html += '<div class="ops-stat-row"><span class="ops-stat-label">' + ctrl.name + '</span>' +
          '<button class="ops-btn" onclick="opsControl(\\'' + sys.id + '\\',\\'' + ctrl.id + '\\',\\'momentary\\',true)">' + (ctrl.label || 'PRESS') + '</button></div>';
      }
    });
    html += '</div>';
  }

  body.innerHTML = html;
}

async function opsControl(sysId, controlId, type, value) {
  try {
    await fetch('/api/systems/' + sysId + '/control', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ control_id: controlId, type: type, value: value })
    });
  } catch(e) {}
}

function opsShowHistory() {
  _ops.currentRange = '24h';
  document.querySelectorAll('#ops-hist-range .ops-range-btn').forEach(function(b) { b.classList.remove('active'); });
  document.querySelector('#ops-hist-range .ops-range-btn').classList.add('active');
  _opsScreen('history');
  opsLoadGraph();
}

function opsSetHistRange(range, btn) {
  _ops.currentRange = range;
  document.querySelectorAll('#ops-hist-range .ops-range-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
  opsLoadGraph();
}

async function opsLoadGraph() {
  var sensor = document.getElementById('ops-hist-sensor').value;
  var range = _ops.currentRange;

  try {
    var r = await fetch('/api/sensors/' + sensor + '/history?range=' + range);
    var d = await r.json();
    var points = d.points || [];

    if (points.length === 0) {
      document.getElementById('ops-hist-stats').innerHTML = '<div style="color:var(--text-sub);text-align:center;">No data for this range</div>';
      return;
    }

    // Calculate stats
    var values = points.map(function(p) { return p.v; });
    var high = Math.max.apply(null, values);
    var low = Math.min.apply(null, values);
    var sum = values.reduce(function(a, b) { return a + b; }, 0);
    var avg = sum / values.length;

    var sensorInfo = {rak_temp: '\\u00b0F', rak_humidity: '%', rak_pressure: ' hPa', rak_airquality: ' IAQ', rak_dewpoint: '\\u00b0F'};
    var unit = sensorInfo[sensor] || '';

    document.getElementById('ops-hist-stats').innerHTML =
      '<div class="ops-section"><div class="ops-section-label">STATISTICS (' + range.toUpperCase() + ')</div>' +
      '<div class="ops-stat-row"><span class="ops-stat-label">High</span><span class="ops-stat-val" style="color:#ef4444;">' + high.toFixed(1) + unit + '</span></div>' +
      '<div class="ops-stat-row"><span class="ops-stat-label">Low</span><span class="ops-stat-val" style="color:#3b82f6;">' + low.toFixed(1) + unit + '</span></div>' +
      '<div class="ops-stat-row"><span class="ops-stat-label">Average</span><span class="ops-stat-val">' + avg.toFixed(1) + unit + '</span></div>' +
      '<div class="ops-stat-row"><span class="ops-stat-label">Readings</span><span class="ops-stat-val" style="font-family:Rajdhani,sans-serif;">' + values.length + '</span></div>' +
      '</div>';

    // Draw chart
    var canvas = document.getElementById('ops-hist-canvas');
    var wrap = canvas.parentElement;
    canvas.width = wrap.clientWidth - 24;
    canvas.height = wrap.clientHeight - 24;
    var ctx = canvas.getContext('2d');

    if (_ops.histChart) {
      _ops.histChart.destroy();
      _ops.histChart = null;
    }

    var labels = points.map(function(p) {
      var dt = new Date(p.t * 1000);
      if (range === '24h') return dt.getHours() + ':' + String(dt.getMinutes()).padStart(2, '0');
      return (dt.getMonth()+1) + '/' + dt.getDate();
    });

    // Downsample if too many points
    var maxPoints = 200;
    var step = Math.max(1, Math.floor(points.length / maxPoints));
    var dsLabels = [];
    var dsValues = [];
    for (var i = 0; i < points.length; i += step) {
      dsLabels.push(labels[i]);
      dsValues.push(values[i]);
    }

    _ops.histChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dsLabels,
        datasets: [{
          data: dsValues,
          borderColor: 'rgba(30,90,255,0.8)',
          backgroundColor: 'rgba(30,90,255,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 10 }, maxTicksLimit: 8 },
            grid: { color: 'rgba(255,255,255,0.05)' }
          },
          y: {
            ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.08)' }
          }
        }
      }
    });

  } catch(e) {
    document.getElementById('ops-hist-stats').innerHTML = '<div style="color:#f87171;text-align:center;">Failed to load data</div>';
  }
}
</script>

'''

content = before + new_ops + after

with open('/home/brifas/dashboard-html/index.html', 'w') as f:
    f.write(content)

print("Operations UI rebuilt successfully")
print(f"File size: {len(content)} characters")
