#!/usr/bin/env python3
"""Replace the entire automation submenu in index.html with new UI."""

with open('/home/brifas/dashboard-html/index.html', 'r') as f:
    content = f.read()

# Find the automation block
start_marker = '<!-- AUTOMATION SUBMENU -->'
end_marker = '</script>\n</body>\n</html>'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx < 0:
    print("ERROR: start marker not found")
    exit(1)
if end_idx < 0:
    print("ERROR: end marker not found")
    exit(1)

before = content[:start_idx]
after = '</body>\n</html>'

new_auto = '''<!-- AUTOMATION SUBMENU -->
<style>
#auto-overlay{font-family:'Rajdhani',sans-serif;color:var(--text);}
.auto-header{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;flex-shrink:0;background:rgba(10,20,60,0.7);border-bottom:1px solid rgba(var(--accent-rgb),0.25);}
.auto-title{font-size:20px;font-weight:700;letter-spacing:2px;color:var(--text);}
.auto-btn{background:rgba(var(--accent-rgb),0.15);border:1px solid rgba(var(--accent-rgb),0.35);color:var(--text);border-radius:8px;padding:8px 18px;font-family:'Rajdhani',sans-serif;font-size:14px;font-weight:700;letter-spacing:1px;cursor:pointer;transition:background 0.2s;}
.auto-btn:hover{background:rgba(var(--accent-rgb),0.3);}
.auto-btn-close{background:rgba(220,40,40,0.12);border-color:rgba(220,40,40,0.35);color:#fca5a5;}
.auto-btn-close:hover{background:rgba(220,40,40,0.28);}
.auto-btn-danger{background:rgba(220,40,40,0.15);border-color:rgba(220,40,40,0.4);color:#fca5a5;}
.auto-btn-danger:hover{background:rgba(220,40,40,0.3);}
.auto-btn-success{background:rgba(34,197,94,0.15);border-color:rgba(34,197,94,0.4);color:#86efac;}
.auto-btn-success:hover{background:rgba(34,197,94,0.3);}
.auto-screen{display:none;flex-direction:column;height:100%;}
.auto-screen.active{display:flex;}
.auto-rule-item{display:flex;align-items:center;gap:14px;background:rgba(var(--accent-rgb),0.1);border:1px solid rgba(var(--accent-rgb),0.25);border-radius:10px;padding:14px 18px;transition:background 0.2s;}
.auto-rule-item:hover{background:rgba(var(--accent-rgb),0.18);}
.auto-rule-name{font-size:16px;font-weight:700;flex:1;}
.auto-rule-summary{font-size:12px;color:var(--text-sub);font-weight:600;}
.auto-rule-cat{font-size:11px;font-weight:700;letter-spacing:1px;color:var(--accent);background:rgba(var(--accent-rgb),0.15);border:1px solid rgba(var(--accent-rgb),0.3);border-radius:4px;padding:2px 8px;text-transform:uppercase;}
.auto-toggle{position:relative;width:48px;height:24px;cursor:pointer;flex-shrink:0;}
.auto-toggle input{opacity:0;width:0;height:0;}
.auto-toggle-slider{position:absolute;inset:0;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:24px;transition:0.3s;}
.auto-toggle-slider:before{content:'';position:absolute;height:18px;width:18px;left:2px;bottom:2px;background:var(--text-sub);border-radius:50%;transition:0.3s;}
.auto-toggle input:checked+.auto-toggle-slider{background:rgba(34,197,94,0.3);border-color:rgba(34,197,94,0.5);}
.auto-toggle input:checked+.auto-toggle-slider:before{transform:translateX(24px);background:#22c55e;box-shadow:0 0 8px rgba(34,197,94,0.7);}
.auto-form-section{background:rgba(var(--accent-rgb),0.08);border:1px solid rgba(var(--accent-rgb),0.2);border-radius:12px;padding:18px 22px;display:flex;flex-direction:column;gap:14px;}
.auto-form-label{font-size:11px;font-weight:700;letter-spacing:2px;color:var(--text-sub);text-transform:uppercase;}
.auto-form-row{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}
.auto-select{background:rgba(var(--accent-rgb),0.12);border:1px solid rgba(var(--accent-rgb),0.3);color:var(--text);border-radius:8px;padding:10px 14px;font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:600;cursor:pointer;flex:1;min-width:140px;}
.auto-select option{background:#0a1428;}
.auto-input{background:rgba(var(--accent-rgb),0.12);border:1px solid rgba(var(--accent-rgb),0.3);color:var(--text);border-radius:8px;padding:10px 14px;font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:600;flex:1;min-width:100px;}
.auto-input:focus,.auto-select:focus{outline:none;border-color:var(--accent);}
.auto-action-item{display:flex;align-items:center;gap:10px;background:rgba(var(--accent-rgb),0.06);border:1px solid rgba(var(--accent-rgb),0.15);border-radius:8px;padding:12px 14px;}
.auto-action-remove{background:none;border:1px solid rgba(220,40,40,0.3);border-radius:6px;color:#f87171;font-size:16px;width:32px;height:32px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.auto-action-remove:hover{background:rgba(220,40,40,0.2);}
.auto-day-btn{background:rgba(var(--accent-rgb),0.1);border:1px solid rgba(var(--accent-rgb),0.25);color:var(--text-sub);border-radius:6px;padding:6px 10px;font-family:'Rajdhani',sans-serif;font-size:13px;font-weight:700;cursor:pointer;min-width:38px;text-align:center;}
.auto-day-btn.active{background:rgba(var(--accent-rgb),0.4);border-color:var(--accent);color:var(--text);}
.auto-empty{padding:40px;text-align:center;color:var(--text-sub);font-size:16px;font-weight:600;letter-spacing:1px;}
.auto-cat-group{display:flex;flex-direction:column;gap:8px;margin-bottom:16px;}
.auto-cat-label{font-size:12px;font-weight:700;letter-spacing:2px;color:var(--text-sub);text-transform:uppercase;padding-left:4px;}
</style>

<div id="auto-overlay" style="display:none;position:fixed;inset:0;background:var(--overlay-bg);z-index:1000;flex-direction:column;">

<!-- MAIN SCREEN -->
<div id="auto-screen-main" class="auto-screen">
<div class="auto-header">
<span class="auto-title">&#9889; AUTOMATION</span>
<button class="auto-btn auto-btn-close" onclick="autoClose()">&#10005; CLOSE</button>
</div>
<div style="padding:16px 20px;display:flex;gap:10px;flex-shrink:0;">
<button class="auto-btn auto-btn-success" onclick="autoNewRule()" style="flex:1;">+ NEW AUTOMATION</button>
<button class="auto-btn" onclick="autoShowAll()" style="flex:1;">ALL RULES</button>
<button class="auto-btn" onclick="autoShowLog()">LOG</button>
</div>
<div style="padding:0 20px 4px;"><div class="auto-form-label">ACTIVE AUTOMATIONS</div></div>
<div id="auto-active-list" style="flex:1;overflow-y:auto;padding:0 20px 20px;display:flex;flex-direction:column;gap:8px;"></div>
</div>

<!-- ALL RULES SCREEN -->
<div id="auto-screen-all" class="auto-screen">
<div class="auto-header">
<span class="auto-title">&#9889; ALL RULES</span>
<div style="display:flex;gap:10px;">
<button class="auto-btn" onclick="autoBackToMain()">&#9664; BACK</button>
<button class="auto-btn auto-btn-close" onclick="autoClose()">&#10005; CLOSE</button>
</div>
</div>
<div style="padding:16px 20px;flex-shrink:0;">
<button class="auto-btn auto-btn-success" onclick="autoNewRule()">+ NEW AUTOMATION</button>
</div>
<div id="auto-all-list" style="flex:1;overflow-y:auto;padding:0 20px 20px;display:flex;flex-direction:column;gap:8px;"></div>
</div>

<!-- LOG SCREEN -->
<div id="auto-screen-log" class="auto-screen">
<div class="auto-header">
<span class="auto-title">&#128203; AUTOMATION LOG</span>
<div style="display:flex;gap:10px;">
<button class="auto-btn" onclick="autoBackToMain()">&#9664; BACK</button>
<button class="auto-btn auto-btn-close" onclick="autoClose()">&#10005; CLOSE</button>
</div>
</div>
<div id="auto-log-list" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:6px;"></div>
</div>

<!-- CREATE/EDIT SCREEN -->
<div id="auto-screen-edit" class="auto-screen">
<div class="auto-header">
<span id="auto-edit-title" class="auto-title">&#9889; NEW AUTOMATION</span>
<div style="display:flex;gap:10px;">
<button class="auto-btn" onclick="autoBackToMain()">&#9664; BACK</button>
<button class="auto-btn auto-btn-close" onclick="autoClose()">&#10005; CLOSE</button>
</div>
</div>
<div style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px;">

<!-- ACTIONS SECTION -->
<div class="auto-form-section">
<div class="auto-form-label">ACTIONS — WHAT TO DO</div>
<div id="auto-actions-list" style="display:flex;flex-direction:column;gap:8px;"></div>
<div class="auto-form-row">
<select id="auto-action-device" class="auto-select" onchange="autoActionDeviceChanged()">
<option value="">Select device...</option>
</select>
<select id="auto-action-control" class="auto-select">
<option value="">Select action...</option>
</select>
<input id="auto-action-value" class="auto-input" placeholder="Value" style="max-width:100px;">
<button class="auto-btn" onclick="autoAddAction()">+ ADD</button>
</div>
<div style="display:flex;align-items:center;gap:10px;margin-top:4px;">
<label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:14px;font-weight:600;">
<input type="checkbox" id="auto-alert-check" style="width:18px;height:18px;accent-color:var(--accent);">
Also send notification alert
</label>
</div>
<input id="auto-alert-msg" class="auto-input" placeholder="Alert message (optional)" style="display:none;">
</div>

<!-- TRIGGER SECTION -->
<div class="auto-form-section">
<div class="auto-form-label">TRIGGER — WHEN TO DO IT</div>
<div class="auto-form-row">
<select id="auto-trigger-type" class="auto-select" onchange="autoTriggerTypeChanged()">
<option value="">Select trigger type...</option>
<option value="schedule">Schedule (Time)</option>
<option value="astral">Astral (Sun Events)</option>
<option value="moon">Moon Phase</option>
<option value="sensor">Sensor Threshold</option>
<option value="camera">Camera Motion</option>
<option value="manual">Manual (Button)</option>
</select>
</div>
<div id="auto-trigger-config" style="display:flex;flex-direction:column;gap:10px;"></div>
</div>

<!-- NAME & CATEGORY -->
<div class="auto-form-section">
<div class="auto-form-label">NAME & CATEGORY</div>
<div class="auto-form-row">
<input id="auto-rule-name" class="auto-input" placeholder="Rule name" style="flex:2;">
<select id="auto-rule-cat" class="auto-select" style="flex:1;">
<option value="general">General</option>
<option value="lighting">Lighting</option>
<option value="pond">Pond</option>
<option value="alerts">Alerts</option>
<option value="security">Security</option>
</select>
</div>
</div>

<!-- SAVE -->
<div style="display:flex;gap:12px;">
<button class="auto-btn auto-btn-success" onclick="autoSaveRule()" style="flex:1;padding:14px;font-size:16px;">SAVE AUTOMATION</button>
<button class="auto-btn auto-btn-danger" id="auto-delete-btn" onclick="autoDeleteCurrent()" style="display:none;padding:14px;">DELETE</button>
</div>

</div>
</div>

</div>

<script>
const _auto = {
  rules: [],
  devices: [],
  sensors: [],
  cameras: [],
  actions: [],
  editingId: null
};

function _autoScreen(id) {
  document.querySelectorAll('.auto-screen').forEach(function(s) { s.classList.remove('active'); });
  var el = document.getElementById('auto-screen-' + id);
  if (el) el.classList.add('active');
}

async function _autoLoadData() {
  try {
    var r1 = await fetch('/api/lights');
    var d1 = await r1.json();
    var lights = (d1.devices || []).map(function(d) {
      return { id: d.id, name: d.name, type: d.type, category: 'light', controls: ['on', 'off', 'brightness', 'color'] };
    });
    var r2 = await fetch('/api/systems');
    var d2 = await r2.json();
    var systems = (d2.systems || []).map(function(d) {
      return { id: d.id, name: d.name, type: d.type, category: 'system', controls: ['on', 'off'] };
    });
    _auto.devices = lights.concat(systems);
  } catch(e) { _auto.devices = []; }
  try {
    var r3 = await fetch('/api/sensors');
    var d3 = await r3.json();
    _auto.sensors = d3.sensors || [];
  } catch(e) { _auto.sensors = []; }
  try {
    var r4 = await fetch('/api/camera/list');
    var d4 = await r4.json();
    _auto.cameras = d4.cameras || [];
  } catch(e) { _auto.cameras = []; }
}

async function _autoLoadRules() {
  try {
    var r = await fetch('/api/automation/rules');
    var d = await r.json();
    _auto.rules = d.rules || [];
  } catch(e) { _auto.rules = []; }
}

function _autoFmt(name) {
  return name.replace(/[-_]/g, ' ').replace(/\\b\\w/g, function(c) { return c.toUpperCase(); });
}

function _autoTriggerSummary(rule) {
  var t = rule.trigger_type;
  var tc = rule.trigger_config || {};
  if (t === 'schedule') {
    var time = tc.time || '??:??';
    var dayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    var days = (tc.days || []).map(function(d) { return dayNames[d] || '?'; }).join(', ');
    return 'At ' + time + (days ? ' on ' + days : ' daily');
  }
  if (t === 'astral') {
    var offset = tc.offset_minutes ? (' ' + (tc.offset_minutes > 0 ? '+' : '') + tc.offset_minutes + 'min') : '';
    return _autoFmt(tc.event || 'sunset') + offset;
  }
  if (t === 'moon') return 'Moon: ' + _autoFmt(tc.phase || 'full');
  if (t === 'sensor') {
    var op = tc.operator === 'gt' ? '>' : tc.operator === 'lt' ? '<' : '=';
    return (tc.sensor_name || tc.sensor_id || '?') + ' ' + op + ' ' + (tc.value || '?');
  }
  if (t === 'camera') return 'Motion on ' + _autoFmt(tc.camera || '?');
  if (t === 'manual') return 'Manual trigger';
  return t || 'Unknown';
}

function _autoActionSummary(rule) {
  var actions = rule.actions || [];
  return actions.map(function(a) {
    if (a.type === 'light_control') {
      var cmd = a.command || {};
      return _autoFmt(a.device_id || '?') + ' → ' + (cmd.value || cmd.action || '?');
    }
    if (a.type === 'system_control') {
      var cmd2 = a.command || {};
      return _autoFmt(a.system_id || a.device_id || '?') + ' → ' + (cmd2.value || cmd2.action || '?');
    }
    if (a.type === 'notification') return 'Alert: ' + (a.message || '');
    return a.type || '?';
  }).join(', ');
}

function _autoRenderItem(rule) {
  var trigger = _autoTriggerSummary(rule);
  var action = _autoActionSummary(rule);
  var checked = rule.enabled ? 'checked' : '';
  return '<div class="auto-rule-item">' +
    '<div style="flex:1;cursor:pointer;" onclick="autoEditRule(\\''+rule.id+'\\')"><div class="auto-rule-name">' + rule.name + '</div>' +
    '<div class="auto-rule-summary">' + trigger + ' → ' + action + '</div></div>' +
    '<span class="auto-rule-cat">' + (rule.category || 'general') + '</span>' +
    (rule.trigger_type === 'manual' ? '<button class="auto-btn" onclick="autoManualTrigger(\\''+rule.id+'\\')">RUN</button>' : '') +
    '<label class="auto-toggle"><input type="checkbox" '+checked+' onchange="autoToggleRule(\\''+rule.id+'\\')"><span class="auto-toggle-slider"></span></label>' +
    '</div>';
}

function _autoRenderActive() {
  var el = document.getElementById('auto-active-list');
  var active = _auto.rules.filter(function(r) { return r.enabled; });
  if (active.length === 0) {
    el.innerHTML = '<div class="auto-empty">No active automations</div>';
    return;
  }
  el.innerHTML = active.map(_autoRenderItem).join('');
}

function _autoRenderAll() {
  var el = document.getElementById('auto-all-list');
  if (_auto.rules.length === 0) {
    el.innerHTML = '<div class="auto-empty">No automation rules created yet</div>';
    return;
  }
  var cats = {};
  _auto.rules.forEach(function(r) {
    var cat = r.category || 'general';
    if (!cats[cat]) cats[cat] = [];
    cats[cat].push(r);
  });
  var html = '';
  Object.keys(cats).sort().forEach(function(cat) {
    html += '<div class="auto-cat-group"><div class="auto-cat-label">' + cat.toUpperCase() + '</div>';
    html += cats[cat].map(_autoRenderItem).join('');
    html += '</div>';
  });
  el.innerHTML = html;
}

async function autoOpen() {
  document.getElementById('auto-overlay').style.display = 'flex';
  document.getElementById('auto-overlay').style.flexDirection = 'column';
  await _autoLoadData();
  await _autoLoadRules();
  _autoRenderActive();
  _autoScreen('main');
}

function autoClose() {
  document.getElementById('auto-overlay').style.display = 'none';
}

function autoBackToMain() {
  _autoRenderActive();
  _autoScreen('main');
}

function autoShowAll() {
  _autoRenderAll();
  _autoScreen('all');
}

async function autoShowLog() {
  _autoScreen('log');
  var el = document.getElementById('auto-log-list');
  el.innerHTML = '<div class="auto-empty">Loading...</div>';
  try {
    var r = await fetch('/api/automation/log');
    var d = await r.json();
    var logs = d.log || [];
    if (logs.length === 0) {
      el.innerHTML = '<div class="auto-empty">No log entries</div>';
      return;
    }
    el.innerHTML = logs.map(function(l) {
      var dt = new Date(l.timestamp * 1000);
      var time = dt.toLocaleString();
      var color = l.result === 'success' ? '#22c55e' : '#f87171';
      return '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:rgba(var(--accent-rgb),0.06);border-radius:6px;">' +
        '<div><div style="font-weight:700;font-size:14px;">' + (l.rule_name || '?') + '</div>' +
        '<div style="font-size:12px;color:var(--text-sub);">' + (l.detail || '') + '</div></div>' +
        '<div style="text-align:right;"><div style="font-size:11px;color:' + color + ';font-weight:700;">' + (l.result || '').toUpperCase() + '</div>' +
        '<div style="font-size:11px;color:var(--text-sub);">' + time + '</div></div></div>';
    }).join('');
  } catch(e) {
    el.innerHTML = '<div class="auto-empty">Failed to load log</div>';
  }
}

async function autoToggleRule(id) {
  try {
    await fetch('/api/automation/rules/' + id + '/toggle', { method: 'POST' });
    await _autoLoadRules();
    _autoRenderActive();
    _autoRenderAll();
  } catch(e) {}
}

async function autoManualTrigger(id) {
  try {
    await fetch('/api/automation/rules/' + id + '/trigger', { method: 'POST' });
    alert('Rule triggered.');
  } catch(e) { alert('Failed.'); }
}

function _autoPopulateDevices() {
  var sel = document.getElementById('auto-action-device');
  sel.innerHTML = '<option value="">Select device...</option>';
  _auto.devices.forEach(function(d) {
    sel.innerHTML += '<option value="' + d.id + '" data-cat="' + d.category + '">' + _autoFmt(d.name) + ' (' + d.category + ')</option>';
  });
  // Add special entries
  sel.innerHTML += '<option value="__display__" data-cat="system">Display (Screen)</option>';
  sel.innerHTML += '<option value="__brightness__" data-cat="system">Brightness</option>';
}

function autoActionDeviceChanged() {
  var devId = document.getElementById('auto-action-device').value;
  var ctrl = document.getElementById('auto-action-control');
  var valInput = document.getElementById('auto-action-value');
  ctrl.innerHTML = '<option value="">Select action...</option>';
  valInput.style.display = 'none';
  valInput.value = '';

  if (devId === '__display__') {
    ctrl.innerHTML += '<option value="on">Turn On</option><option value="off">Turn Off</option>';
    return;
  }
  if (devId === '__brightness__') {
    ctrl.innerHTML += '<option value="set">Set Level</option>';
    valInput.style.display = '';
    valInput.placeholder = '0-100';
    return;
  }

  var dev = _auto.devices.find(function(d) { return d.id === devId; });
  if (!dev) return;

  if (dev.category === 'light') {
    ctrl.innerHTML += '<option value="on">Turn On</option><option value="off">Turn Off</option>';
    if (dev.type === 'dimmer' || dev.type === 'rgb') {
      ctrl.innerHTML += '<option value="brightness">Set Brightness</option>';
    }
    if (dev.type === 'rgb') {
      ctrl.innerHTML += '<option value="color">Set Color</option>';
    }
  } else {
    ctrl.innerHTML += '<option value="on">Turn On</option><option value="off">Turn Off</option>';
  }
}

function autoAddAction() {
  var devSel = document.getElementById('auto-action-device');
  var devId = devSel.value;
  var devName = devSel.options[devSel.selectedIndex] ? devSel.options[devSel.selectedIndex].text : '';
  var ctrlSel = document.getElementById('auto-action-control');
  var control = ctrlSel.value;
  var controlName = ctrlSel.options[ctrlSel.selectedIndex] ? ctrlSel.options[ctrlSel.selectedIndex].text : '';
  var value = document.getElementById('auto-action-value').value;

  if (!devId || !control) { alert('Select device and action.'); return; }

  var action = {};
  var devCat = devSel.options[devSel.selectedIndex].getAttribute('data-cat');

  if (devId === '__display__') {
    action = { type: 'system_control', device_id: 'display', command: { action: 'state', value: control }, _display: devName + ' → ' + controlName };
  } else if (devId === '__brightness__') {
    action = { type: 'system_control', device_id: 'brightness', command: { action: 'brightness', value: parseInt(value) || 50 }, _display: devName + ' → ' + value + '%' };
  } else if (devCat === 'light') {
    var cmd = { action: control === 'on' || control === 'off' ? 'state' : control, value: control === 'brightness' ? (parseInt(value) || 100) : control === 'color' ? (value || '#ffffff') : control };
    action = { type: 'light_control', device_id: devId, command: cmd, _display: devName + ' → ' + controlName + (value ? ' ' + value : '') };
  } else {
    action = { type: 'system_control', system_id: devId, device_id: devId, command: { action: 'state', value: control }, _display: devName + ' → ' + controlName };
  }

  _auto.actions.push(action);
  _autoRenderActions();
  devSel.value = '';
  ctrlSel.innerHTML = '<option value="">Select action...</option>';
  document.getElementById('auto-action-value').style.display = 'none';
  document.getElementById('auto-action-value').value = '';
}

function autoRemoveAction(idx) {
  _auto.actions.splice(idx, 1);
  _autoRenderActions();
}

function _autoRenderActions() {
  var el = document.getElementById('auto-actions-list');
  if (_auto.actions.length === 0) {
    el.innerHTML = '<div style="color:var(--text-sub);font-size:13px;padding:4px;">No actions added yet</div>';
    return;
  }
  el.innerHTML = _auto.actions.map(function(a, i) {
    return '<div class="auto-action-item"><span style="flex:1;font-size:14px;font-weight:600;">' + (a._display || a.type) + '</span>' +
      '<button class="auto-action-remove" onclick="autoRemoveAction(' + i + ')">&#10005;</button></div>';
  }).join('');
}

function autoTriggerTypeChanged() {
  var type = document.getElementById('auto-trigger-type').value;
  var el = document.getElementById('auto-trigger-config');
  el.innerHTML = '';

  if (type === 'schedule') {
    el.innerHTML = '<div class="auto-form-row"><label style="font-size:14px;font-weight:600;min-width:50px;">Time:</label><input type="time" id="auto-trig-time" class="auto-input" style="max-width:160px;"></div>' +
      '<div style="display:flex;gap:6px;flex-wrap:wrap;" id="auto-trig-days">' +
      ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(function(d, i) {
        return '<button class="auto-day-btn" data-day="' + i + '" onclick="this.classList.toggle(\\'active\\')">' + d + '</button>';
      }).join('') + '</div>';
  } else if (type === 'astral') {
    el.innerHTML = '<div class="auto-form-row"><select id="auto-trig-event" class="auto-select"><option value="sunrise">Sunrise</option><option value="sunset">Sunset</option><option value="dawn">Dawn</option><option value="dusk">Dusk</option><option value="noon">Solar Noon</option></select>' +
      '<label style="font-size:14px;font-weight:600;">Offset:</label><input type="number" id="auto-trig-offset" class="auto-input" value="0" style="max-width:80px;"><span style="font-size:13px;color:var(--text-sub);">minutes</span></div>';
  } else if (type === 'moon') {
    el.innerHTML = '<div class="auto-form-row"><select id="auto-trig-phase" class="auto-select">' +
      '<option value="new_moon">New Moon</option><option value="waxing_crescent">Waxing Crescent</option><option value="first_quarter">First Quarter</option><option value="waxing_gibbous">Waxing Gibbous</option>' +
      '<option value="full_moon">Full Moon</option><option value="waning_gibbous">Waning Gibbous</option><option value="last_quarter">Last Quarter</option><option value="waning_crescent">Waning Crescent</option>' +
      '</select></div>';
  } else if (type === 'sensor') {
    var opts = _auto.sensors.map(function(s) { return '<option value="' + s.id + '">' + _autoFmt(s.name || s.id) + ' (' + (s.unit || '') + ')</option>'; }).join('');
    el.innerHTML = '<div class="auto-form-row"><select id="auto-trig-sensor" class="auto-select">' + opts + '</select>' +
      '<select id="auto-trig-op" class="auto-select" style="max-width:100px;"><option value="gt">Above</option><option value="lt">Below</option><option value="eq">Equals</option></select>' +
      '<input type="number" id="auto-trig-value" class="auto-input" placeholder="Value" style="max-width:100px;"></div>';
  } else if (type === 'camera') {
    var camOpts = _auto.cameras.map(function(c) { return '<option value="' + c.id + '">' + c.name + '</option>'; }).join('');
    el.innerHTML = '<div class="auto-form-row"><select id="auto-trig-camera" class="auto-select">' + camOpts + '</select>' +
      '<span style="font-size:13px;color:var(--text-sub);">Triggers on motion detection</span></div>';
  } else if (type === 'manual') {
    el.innerHTML = '<div style="color:var(--text-sub);font-size:13px;padding:4px;">This rule will only run when you press the RUN button.</div>';
  }
}

function autoNewRule() {
  _auto.editingId = null;
  _auto.actions = [];
  document.getElementById('auto-edit-title').textContent = '\\u26a1 NEW AUTOMATION';
  document.getElementById('auto-delete-btn').style.display = 'none';
  document.getElementById('auto-rule-name').value = '';
  document.getElementById('auto-rule-cat').value = 'general';
  document.getElementById('auto-trigger-type').value = '';
  document.getElementById('auto-trigger-config').innerHTML = '';
  document.getElementById('auto-alert-check').checked = false;
  document.getElementById('auto-alert-msg').style.display = 'none';
  document.getElementById('auto-alert-msg').value = '';
  _autoPopulateDevices();
  _autoRenderActions();
  document.getElementById('auto-action-device').value = '';
  document.getElementById('auto-action-control').innerHTML = '<option value="">Select action...</option>';
  document.getElementById('auto-action-value').style.display = 'none';
  _autoScreen('edit');
}

function autoEditRule(id) {
  var rule = _auto.rules.find(function(r) { return r.id === id; });
  if (!rule) return;
  _auto.editingId = id;
  document.getElementById('auto-edit-title').textContent = '\\u26a1 EDIT: ' + rule.name;
  document.getElementById('auto-delete-btn').style.display = '';
  document.getElementById('auto-rule-name').value = rule.name;
  document.getElementById('auto-rule-cat').value = rule.category || 'general';

  // Restore actions
  _auto.actions = (rule.actions || []).map(function(a) {
    var display = '';
    if (a.type === 'light_control') display = _autoFmt(a.device_id || '') + ' → ' + ((a.command || {}).value || '');
    else if (a.type === 'system_control') display = _autoFmt(a.system_id || a.device_id || '') + ' → ' + ((a.command || {}).value || '');
    else if (a.type === 'notification') display = 'Alert: ' + (a.message || '');
    a._display = display;
    return a;
  });

  // Check for notification action
  var notifAction = _auto.actions.find(function(a) { return a.type === 'notification'; });
  document.getElementById('auto-alert-check').checked = !!notifAction;
  document.getElementById('auto-alert-msg').style.display = notifAction ? '' : 'none';
  document.getElementById('auto-alert-msg').value = notifAction ? (notifAction.message || '') : '';

  // Remove notification from actions list display (handled by checkbox)
  _auto.actions = _auto.actions.filter(function(a) { return a.type !== 'notification'; });

  _autoPopulateDevices();
  _autoRenderActions();

  // Set trigger
  document.getElementById('auto-trigger-type').value = rule.trigger_type || '';
  autoTriggerTypeChanged();

  // Fill trigger config after fields render
  setTimeout(function() {
    var tc = rule.trigger_config || {};
    if (rule.trigger_type === 'schedule') {
      var timeEl = document.getElementById('auto-trig-time');
      if (timeEl) timeEl.value = tc.time || '';
      (tc.days || []).forEach(function(d) {
        var btn = document.querySelector('#auto-trig-days .auto-day-btn[data-day="' + d + '"]');
        if (btn) btn.classList.add('active');
      });
    } else if (rule.trigger_type === 'astral') {
      var evEl = document.getElementById('auto-trig-event');
      if (evEl) evEl.value = tc.event || 'sunset';
      var offEl = document.getElementById('auto-trig-offset');
      if (offEl) offEl.value = tc.offset_minutes || 0;
    } else if (rule.trigger_type === 'moon') {
      var phEl = document.getElementById('auto-trig-phase');
      if (phEl) phEl.value = tc.phase || 'full_moon';
    } else if (rule.trigger_type === 'sensor') {
      var snEl = document.getElementById('auto-trig-sensor');
      if (snEl) snEl.value = tc.sensor_id || '';
      var opEl = document.getElementById('auto-trig-op');
      if (opEl) opEl.value = tc.operator || 'gt';
      var valEl = document.getElementById('auto-trig-value');
      if (valEl) valEl.value = tc.value || '';
    } else if (rule.trigger_type === 'camera') {
      var camEl = document.getElementById('auto-trig-camera');
      if (camEl) camEl.value = tc.camera || '';
    }
  }, 50);

  _autoScreen('edit');
}

function _autoGatherTrigger() {
  var type = document.getElementById('auto-trigger-type').value;
  var config = {};

  if (type === 'schedule') {
    config.time = (document.getElementById('auto-trig-time') || {}).value || '';
    config.days = [];
    document.querySelectorAll('#auto-trig-days .auto-day-btn.active').forEach(function(btn) {
      config.days.push(parseInt(btn.getAttribute('data-day')));
    });
  } else if (type === 'astral') {
    config.event = (document.getElementById('auto-trig-event') || {}).value || 'sunset';
    config.offset_minutes = parseInt((document.getElementById('auto-trig-offset') || {}).value) || 0;
  } else if (type === 'moon') {
    config.phase = (document.getElementById('auto-trig-phase') || {}).value || 'full_moon';
  } else if (type === 'sensor') {
    config.sensor_id = (document.getElementById('auto-trig-sensor') || {}).value || '';
    config.operator = (document.getElementById('auto-trig-op') || {}).value || 'gt';
    config.value = parseFloat((document.getElementById('auto-trig-value') || {}).value) || 0;
  } else if (type === 'camera') {
    config.camera = (document.getElementById('auto-trig-camera') || {}).value || '';
  }

  return { type: type, config: config };
}

async function autoSaveRule() {
  var name = document.getElementById('auto-rule-name').value.trim();
  if (!name) { alert('Enter a rule name.'); return; }

  var triggerType = document.getElementById('auto-trigger-type').value;
  if (!triggerType) { alert('Select a trigger type.'); return; }

  if (_auto.actions.length === 0) { alert('Add at least one action.'); return; }

  var trigger = _autoGatherTrigger();
  var cat = document.getElementById('auto-rule-cat').value;

  // Build clean actions (remove _display)
  var actions = _auto.actions.map(function(a) {
    var clean = {};
    Object.keys(a).forEach(function(k) {
      if (k !== '_display') clean[k] = a[k];
    });
    return clean;
  });

  // Add notification if checked
  if (document.getElementById('auto-alert-check').checked) {
    var msg = document.getElementById('auto-alert-msg').value || name + ' triggered';
    actions.push({ type: 'notification', message: msg });
  }

  var rule = {
    name: name,
    category: cat,
    enabled: 1,
    trigger_type: trigger.type,
    trigger_config: trigger.config,
    conditions: [],
    actions: actions
  };

  try {
    if (_auto.editingId) {
      await fetch('/api/automation/rules/' + _auto.editingId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rule)
      });
    } else {
      await fetch('/api/automation/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rule)
      });
    }
    await _autoLoadRules();
    autoBackToMain();
  } catch(e) { alert('Save failed.'); }
}

async function autoDeleteCurrent() {
  if (!_auto.editingId) return;
  if (!confirm('Delete this automation?')) return;
  try {
    await fetch('/api/automation/rules/' + _auto.editingId, { method: 'DELETE' });
    await _autoLoadRules();
    autoBackToMain();
  } catch(e) { alert('Delete failed.'); }
}

// Alert checkbox toggle
document.getElementById('auto-alert-check').addEventListener('change', function() {
  document.getElementById('auto-alert-msg').style.display = this.checked ? '' : 'none';
});
</script>
'''

content = before + new_auto + '\n' + after

with open('/home/brifas/dashboard-html/index.html', 'w') as f:
    f.write(content)

print("Automation UI rebuilt successfully")
print(f"File size: {len(content)} characters")
