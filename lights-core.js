// lights-core.js: shared by the wall Lighting screen (index.html) and the phone (m/lights.html).
// Reads the engine's status (/api/v2/status) and sends commands (/api/v2/lights, /api/v2/groups).
// A switch shows what the light itself last confirmed. A tap shows "Turning on…" until the light confirms it.
const LightsCore = (() => {
  const STALE_S = 30, PENDING_MS = 12000, FAILED_MS = 30000, DEAD_MS = 10000, DEAD_W = 5;
  let st = null, err = 'Loading…';
  const pending = {}, failed = {}, deadSince = {};

  async function refresh() {
    try {
      const r = await fetch('/api/v2/status', { cache: 'no-store' });
      const j = await r.json();
      if (!r.ok) { st = null; err = j.detail || 'Automation engine not available'; return; }
      if (Date.now() / 1000 - (j.ts || 0) > STALE_S) { st = null; err = "The automation engine isn't running, so lights can't be shown or switched."; return; }
      st = j; err = null;
    } catch (e) { st = null; err = "Can't reach the dashboard."; }
  }

  function devices() {
    if (!st) return {};
    const o = {};
    for (const [id, d] of Object.entries(st.devices || {})) if (d.in_inventory) o[id] = d;
    return o;
  }

  // Groups sorted by name. Lights with no group go in "Other lights" (no All On/Off there).
  function groups() {
    const devs = devices(), out = [], grouped = new Set();
    for (const [gid, g] of Object.entries((st && st.groups) || {})) {
      const m = g.members.filter(i => devs[i]);
      m.forEach(i => grouped.add(i));
      if (m.length) out.push({ gid, name: g.name || gid, members: m, all: true });
    }
    out.sort((a, b) => a.name.localeCompare(b.name));
    const rest = Object.keys(devs).filter(i => !grouped.has(i)).sort();
    if (rest.length) out.push({ gid: '_other', name: 'Other lights', members: rest, all: false });
    for (const g of out) {
      g.on = g.members.filter(i => devs[i].online && devs[i].state === 'on').length;
      g.offline = g.members.filter(i => !devs[i].online).length;
      g.line = g.on + ' of ' + g.members.length + ' on' + (g.offline ? ' · ' + g.offline + ' offline' : '');
    }
    return out;
  }

  function group(gid) { return groups().find(g => g.gid === gid) || null; }

  function when(iso) {                       // "2026-10-07T05:00" -> "5:00 AM", "tomorrow 5:00 AM", "Thu 5:00 AM"
    if (!iso) return '';
    const t = new Date(iso), now = new Date();
    const hm = t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    const days = Math.round((new Date(t.toDateString()) - new Date(now.toDateString())) / 86400000);
    if (days === 0) return hm;
    if (days === 1) return 'tomorrow ' + hm;
    return t.toLocaleDateString([], { weekday: 'short' }) + ' ' + hm;
  }

  // Everything a screen needs for one light. kind: ok | pending | warn | offline
  function light(id) {
    const d = devices()[id];
    if (!d) return null;
    const v = { id, name: d.name || id, online: d.online, on: d.state === 'on', kind: 'ok', line: '' };
    const now = Date.now(), p = pending[id];
    if (p && d.online && d.state === p.state) delete pending[id];
    if (d.online && d.state === 'on' && typeof d.watts === 'number' && d.watts < DEAD_W) deadSince[id] = deadSince[id] || now;
    else delete deadSince[id];

    if (!d.online) {
      v.kind = 'offline';
      v.line = d.state ? 'Offline · last known ' + (d.state === 'on' ? 'On' : 'Off') : 'Offline';
      delete pending[id];
    } else if (pending[id] && now - pending[id].t < PENDING_MS) {
      v.kind = 'pending'; v.line = pending[id].state === 'on' ? 'Turning on…' : 'Turning off…';
    } else if (pending[id]) {
      delete pending[id]; failed[id] = now;
      v.kind = 'warn'; v.line = 'Not responding';
    } else if (failed[id] && now - failed[id] < FAILED_MS) {
      v.kind = 'warn'; v.line = 'Not responding';
    } else if (d.manual && d.resume && d.state !== d.want) {     // the light really differs from the automation
      v.line = 'Changed by hand · automation resumes ' + when(d.resume);
    } else if (d.want && !d.confirmed && !d.manual && d.want !== d.state) {
      if (d.tries >= 2) { v.kind = 'warn'; v.line = 'Not responding · automation keeps trying to turn it ' + d.want; }
      else { v.kind = 'pending'; v.line = 'Automation turning it ' + d.want + '…'; }
    } else if (v.on && deadSince[id] && now - deadSince[id] > DEAD_MS) {
      v.kind = 'warn'; v.line = 'On, but drawing ' + Math.round(d.watts) + ' W · check the fixture';
    } else if (v.on) {
      v.line = 'On' + (typeof d.watts === 'number' ? ' · ' + Math.round(d.watts) + ' W' : '')
        + (d.until && d.want === 'on' && d.confirmed ? ' · automation until ' + when(d.until) : '');
    } else v.line = 'Off';
    if (failed[id] && now - failed[id] >= FAILED_MS) delete failed[id];
    return v;
  }

  function anyPending() { return Object.keys(pending).length > 0; }

  async function post(url, state) {
    try {
      const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ state }) });
      const j = await r.json();
      if (!r.ok) return { ok: false, msg: j.detail || 'Failed' };
      const now = Date.now();
      for (const i of j.sent) { pending[i] = { state, t: now }; delete failed[i]; }
      const devs = devices();
      const skipped = (j.skipped_offline || []).map(i => (devs[i] && devs[i].name) || i);
      return { ok: true, msg: skipped.length ? 'Offline, skipped: ' + skipped.join(', ') : '' };
    } catch (e) { return { ok: false, msg: "Can't reach the dashboard." }; }
  }

  // Tap on a light: ask for the opposite of what it last confirmed. Offline or waiting lights ignore taps.
  function tap(id) {
    const v = light(id);
    if (!v || !v.online || v.kind === 'pending') return Promise.resolve({ ok: false, msg: v && !v.online ? v.name + ' is offline' : '' });
    return post('/api/v2/lights/' + encodeURIComponent(id), v.on ? 'off' : 'on');
  }
  function all(gid, state) { return post('/api/v2/groups/' + encodeURIComponent(gid), state); }

  return { refresh, error: () => err, groups, group, light, tap, all, anyPending };
})();
