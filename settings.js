const _settings = {
  themes: [
    {id:'nebula',name:'Nebula',color:'#7e22ff'},
    {id:'void',name:'Void',color:'#00f0ff'},
    {id:'matrix',name:'Matrix',color:'#00ff41'},
    {id:'aquatic',name:'Aquatic',color:'#00b8a9'}
  ],
  activeTheme:'aquatic',
  navStack:[]
};

const _themeColors={
  nebula:{rgb:'126,34,255',accent:'#7e22ff',bg:'linear-gradient(to bottom, #1a0033 0%, #0f0022 40%, #001122 100%)',text:'#f0e0ff',sub:'#c4a5ff',notif:'rgba(80,20,180,0.45)',overlay:'rgba(12,4,40,0.97)',gauge:'#7e22ff',clock:'#7e22ff'},
  void:{rgb:'0,240,255',accent:'#00f0ff',bg:'linear-gradient(to bottom, #001122 0%, #000a1a 40%, #000511 100%)',text:'#e0f8ff',sub:'#88ddff',notif:'rgba(0,80,120,0.45)',overlay:'rgba(0,10,20,0.97)',gauge:'#00f0ff',clock:'#00f0ff'},
  matrix:{rgb:'0,255,65',accent:'#00ff41',bg:'linear-gradient(to bottom, #001100 0%, #000a00 40%, #001100 100%)',text:'#e0ffe8',sub:'#88ffaa',notif:'rgba(0,100,40,0.45)',overlay:'rgba(0,15,5,0.97)',gauge:'#00ff41',clock:'#00ff41'},
  aquatic:{rgb:'0,184,169',accent:'#00b8a9',bg:'linear-gradient(to bottom, #001a22 0%, #002833 40%, #00141a 100%)',text:'#e0f8f5',sub:'#6ee7d8',notif:'rgba(0,120,110,0.45)',overlay:'rgba(0,20,25,0.97)',gauge:'#00b8a9',clock:'#00b8a9'},
  christmas:{rgb:'34,197,94',accent:'#22c55e',bg:'linear-gradient(to bottom, #0a1a0a 0%, #051505 40%, #0a0f0a 100%)',text:'#e0ffe8',sub:'#86efac',notif:'rgba(20,80,20,0.45)',overlay:'rgba(5,12,5,0.97)',gauge:'#dc2626',clock:'#f59e0b',navBg:'#dc2626',widgetBg:'#22c55e',bezelGlow:'#f59e0b'},
  stpatricks:{rgb:'0,255,65',accent:'#00ff41',bg:'linear-gradient(to bottom, #001100 0%, #000a00 40%, #001100 100%)',text:'#a8f0c0',sub:'#6ee7a0',notif:'rgba(0,100,40,0.45)',overlay:'rgba(0,15,5,0.97)',gauge:'#00ff41',clock:'#d4a017'},
  mothersday:{rgb:'219,112,147',accent:'#db7093',bg:'linear-gradient(to bottom, #1a0a10 0%, #0d0508 40%, #0a0d0d 100%)',text:'#ffe4e8',sub:'#c4848e',notif:'rgba(180,60,90,0.45)',overlay:'rgba(15,5,8,0.97)',gauge:'#db7093',clock:'#db7093'},
  july4:{rgb:'220,38,38',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f8fafc',navBg:'#dc2626',widgetBg:'#1e3a8a',bezelGlow:'#f8fafc'},
  flagday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #1a0505 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,5,15,0.97)',gauge:'#cc2200',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#7f1d1d',bezelGlow:'#f8fafc'},
  laborday:{rgb:'107,114,128',accent:'#6b7280',bg:'linear-gradient(to bottom, #111827 0%, #0a0f18 40%, #111827 100%)',text:'#f8fafc',sub:'#d1d5db',notif:'rgba(107,114,128,0.45)',overlay:'rgba(10,15,25,0.97)',gauge:'#d1d5db',clock:'#f8fafc',navBg:'#374151',widgetBg:'#374151',bezelGlow:'#f8fafc'},
  veteransday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #1a0f05 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f59e0b',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f59e0b'},
  memorialday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f8fafc'},
  womensday:{rgb:'192,38,211',accent:'#c026d3',bg:'linear-gradient(to bottom, #1a0520 0%, #0f0215 40%, #1a0520 100%)',text:'#fff1f2',sub:'#f9a8d4',notif:'rgba(192,38,211,0.45)',overlay:'rgba(15,2,18,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#c026d3',widgetBg:'#c026d3',bezelGlow:'#f472b6'},
  soviet:{rgb:'204,0,0',accent:'#cc0000',bg:'linear-gradient(to bottom, #1a0000 0%, #0f0000 40%, #1a0000 100%)',text:'#fff8e7',sub:'#fde68a',notif:'rgba(204,0,0,0.45)',overlay:'rgba(15,0,0,0.97)',gauge:'#f59e0b',clock:'#f59e0b',navBg:'#cc0000',widgetBg:'#cc0000',bezelGlow:'#f59e0b'},
  easter:{rgb:'147,51,234',accent:'#9333ea',bg:'linear-gradient(to bottom, #1a0a2e 0%, #0f0518 40%, #1a0a2e 100%)',text:'#f8fafc',sub:'#e9d5ff',notif:'rgba(147,51,234,0.45)',overlay:'rgba(10,5,20,0.97)',gauge:'#4ade80',clock:'#f59e0b',navBg:'#9333ea',widgetBg:'#9333ea',bezelGlow:'#4ade80'},
  valentine:{rgb:'190,18,60',accent:'#be123c',bg:'linear-gradient(to bottom, #1a0510 0%, #0f0208 40%, #1a0510 100%)',text:'#fff1f2',sub:'#fda4af',notif:'rgba(190,18,60,0.45)',overlay:'rgba(15,2,8,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#be123c',widgetBg:'#be123c',bezelGlow:'#f472b6'},
  flagday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #1a0505 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,5,15,0.97)',gauge:'#cc2200',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#7f1d1d',bezelGlow:'#f8fafc'},
  laborday:{rgb:'107,114,128',accent:'#6b7280',bg:'linear-gradient(to bottom, #111827 0%, #0a0f18 40%, #111827 100%)',text:'#f8fafc',sub:'#d1d5db',notif:'rgba(107,114,128,0.45)',overlay:'rgba(10,15,25,0.97)',gauge:'#d1d5db',clock:'#f8fafc',navBg:'#374151',widgetBg:'#374151',bezelGlow:'#f8fafc'},
  veteransday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #1a0f05 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f59e0b',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f59e0b'},
  memorialday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f8fafc'},
  womensday:{rgb:'192,38,211',accent:'#c026d3',bg:'linear-gradient(to bottom, #1a0520 0%, #0f0215 40%, #1a0520 100%)',text:'#fff1f2',sub:'#f9a8d4',notif:'rgba(192,38,211,0.45)',overlay:'rgba(15,2,18,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#c026d3',widgetBg:'#c026d3',bezelGlow:'#f472b6'},
  soviet:{rgb:'204,0,0',accent:'#cc0000',bg:'linear-gradient(to bottom, #1a0000 0%, #0f0000 40%, #1a0000 100%)',text:'#fff8e7',sub:'#fde68a',notif:'rgba(204,0,0,0.45)',overlay:'rgba(15,0,0,0.97)',gauge:'#f59e0b',clock:'#f59e0b',navBg:'#cc0000',widgetBg:'#cc0000',bezelGlow:'#f59e0b'},
  easter:{rgb:'147,51,234',accent:'#9333ea',bg:'linear-gradient(to bottom, #1a0a2e 0%, #0f0518 40%, #1a0a2e 100%)',text:'#f8fafc',sub:'#e9d5ff',notif:'rgba(147,51,234,0.45)',overlay:'rgba(10,5,20,0.97)',gauge:'#4ade80',clock:'#f59e0b',navBg:'#9333ea',widgetBg:'#9333ea',bezelGlow:'#4ade80'},
  valentine:{rgb:'190,18,60',accent:'#be123c',bg:'linear-gradient(to bottom, #1a0510 0%, #0f0208 40%, #1a0510 100%)',text:'#fff1f2',sub:'#fda4af',notif:'rgba(190,18,60,0.45)',overlay:'rgba(15,2,8,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#be123c',widgetBg:'#be123c',bezelGlow:'#f472b6'},
  newyears:{rgb:'245,158,11',accent:'#f59e0b',bg:'linear-gradient(to bottom, #0a0a0f 0%, #05050a 40%, #0a0a0f 100%)',text:'#f8fafc',sub:'#cbd5e1',notif:'rgba(245,158,11,0.45)',overlay:'rgba(5,5,10,0.97)',gauge:'#e2e8f0',clock:'#f59e0b',navBg:'#f59e0b',widgetBg:'#0f172a',bezelGlow:'#f59e0b'},
  thanksgiving:{rgb:'146,64,14',accent:'#92400e',bg:'linear-gradient(to bottom, #1a0f05 0%, #0f0802 40%, #1a0f05 100%)',text:'#fef3c7',sub:'#fed7aa',notif:'rgba(146,64,14,0.45)',overlay:'rgba(15,8,2,0.97)',gauge:'#f97316',clock:'#f59e0b',navBg:'#92400e',widgetBg:'#92400e',bezelGlow:'#f59e0b'},
  halloween:{rgb:'168,85,247',accent:'#a855f7',bg:'linear-gradient(to bottom, #0a0010 0%, #050008 40%, #0a0010 100%)',text:'#f0e0ff',sub:'#c4a5e0',notif:'rgba(80,20,140,0.45)',overlay:'rgba(8,0,15,0.97)',gauge:'#ff4500',clock:'#ff4500',navBg:'#a855f7',widgetBg:'#0a0a0a',bezelGlow:'#ff9933'}
};

function _settingsHideAll(){
  document.querySelectorAll('#settings-overlay .settings-screen').forEach(function(s){s.classList.remove('active');});
}
function settingsNav(id){
  var cur=document.querySelector('#settings-overlay .settings-screen.active');
  if(cur)_settings.navStack.push(cur.id.replace('settings-screen-',''));
  _settingsHideAll();
  document.getElementById('settings-screen-'+id).classList.add('active');
  if(id==='themes_list')_settingsRenderThemes();
  if(id==='about')_settingsLoadSysInfo();
  if(id==='holiday_themes')_settingsRenderHolidays();
  if(id==='theme_schedule')scheduleRenderList();
  if(id==='theme_carousel')carouselInit();
}
function settingsBack(target){
  _settingsHideAll();
  var dest=target||_settings.navStack.pop()||'main';
  document.getElementById('settings-screen-'+dest).classList.add('active');
}
async function settingsOpen(){
  _settings.navStack=[];
  var o=document.getElementById('settings-overlay');
  o.style.display='flex';
  o.style.flexDirection='column';
  _settingsHideAll();
  document.getElementById('settings-screen-main').classList.add('active');
}
function settingsClose(){
  document.getElementById('settings-overlay').style.display='none';
  _settings.navStack=[];
}
function _settingsRenderThemes(){
  var g=document.getElementById('settings-theme-grid');
  if(!g)return;
  g.innerHTML=_settings.themes.map(function(th){
    var active=th.id===_settings.activeTheme?'active':'';
    return '<div class="settings-theme-btn '+active+'" onclick="settingsSetTheme(\''+th.id+'\')">'
      +'<div class="settings-theme-swatch" style="background:'+th.color+';box-shadow:0 0 8px '+th.color+'66;"></div>'
      +th.name+'</div>';
  }).join('');
}
function settingsSetTheme(id){applyTheme(id);}
function applyTheme(id){
  var c=_themeColors[id];if(!c)return;
  var r=document.documentElement.style;
  r.setProperty('--accent-rgb',c.rgb);
  r.setProperty('--accent',c.accent);
  r.setProperty('--text',c.text);
  r.setProperty('--text-sub',c.sub);
  r.setProperty('--notif-bg',c.notif);
  r.setProperty('--overlay-bg',c.overlay);
  r.setProperty('--gauge',c.gauge||c.accent);
  r.setProperty('--nav-bg',c.navBg||c.accent);
  r.setProperty('--widget-bg',c.widgetBg||c.accent);
  r.setProperty('--bezel-glow',c.bezelGlow||c.accent);
  document.body.style.background='url(static/themes/'+id+'.jpg) center/cover no-repeat #051c35';
  _settings.activeTheme=id;
  localStorage.setItem('dashTheme',id);
  _settingsRenderThemes();
  if(typeof fetchStats==='function')fetchStats();
}
(function(){
  var saved=localStorage.getItem('dashTheme');
  if(saved&&_themeColors[saved]){applyTheme(saved);}else{localStorage.removeItem('dashTheme');applyTheme('aquatic');}
})();
async function settingsBrightness(val){
  document.getElementById('settings-brightness-val').textContent=val+'%';
  try{await fetch('/api/brightness',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({value:parseInt(val)})});}catch(e){}
}
async function settingsDisplayOn(){
  try{await fetch('/api/display',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:'on'})});}catch(e){}
}
async function settingsDisplayOff(){
  try{await fetch('/api/display',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:'off'})});}catch(e){}
}
async function _settingsLoadSysInfo(){
  try{var r=await fetch('/api/sysinfo');var d=await r.json();
  var s=function(id,v){var el=document.getElementById(id);if(el)el.textContent=v||'—';};
  s('si-version',d.version);s('si-uptime',d.uptime);s('si-astral',d.astral);s('si-db',d.db_size);
  s('si-hostname',d.hostname);s('si-kernel',d.kernel);s('si-python',d.python);
  s('si-hailo',d.hailo);s('si-ram',d.ram_total);s('si-storage',d.storage_total);
  s('si-ip',d.ip);s('si-eth0',d.eth0);s('si-tailscale',d.tailscale);
  }catch(e){}
}
var _holidayThemes=[
  {id:'christmas',name:'Christmas',color:'#22c55e',icon:'\u{1F384}'},
  {id:'stpatricks',name:"St. Patrick's",color:'#16a34a',icon:'\u{2618}\u{FE0F}'},
  {id:'flagday',name:'Flag Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'laborday',name:'Labor Day',color:'#6b7280',icon:'\u{1F528}'},
  {id:'veteransday',name:'Veterans Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'memorialday',name:'Memorial Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'womensday',name:"Women's Day",color:'#c026d3',icon:'\u{1F338}'},
  {id:'soviet',name:'Victory Day',color:'#cc0000',icon:'\u{2B50}'},
  {id:'easter',name:'Easter',color:'#9333ea',icon:'\u{1F430}'},
  {id:'valentine',name:"Valentine's Day",color:'#be123c',icon:'\u{1F496}'},
  {id:'flagday',name:'Flag Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'laborday',name:'Labor Day',color:'#6b7280',icon:'\u{1F528}'},
  {id:'veteransday',name:'Veterans Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'memorialday',name:'Memorial Day',color:'#1e3a8a',icon:'\u{1F1FA}\u{1F1F8}'},
  {id:'womensday',name:"Women's Day",color:'#c026d3',icon:'\u{1F338}'},
  {id:'soviet',name:'Victory Day',color:'#cc0000',icon:'\u{2B50}'},
  {id:'easter',name:'Easter',color:'#9333ea',icon:'\u{1F430}'},
  {id:'valentine',name:"Valentine's Day",color:'#be123c',icon:'\u{1F496}'},
  {id:'newyears',name:"New Year's",color:'#f59e0b',icon:'\u{1F386}'},
  {id:'halloween',name:'Halloween',color:'#a855f7',icon:'\u{1F383}'},
  {id:'thanksgiving',name:'Thanksgiving',color:'#f97316',icon:'\u{1F983}'},
  {id:'july4',name:'4th of July',color:'#dc2626',icon:'\u{1F386}'},
  {id:'mothersday',name:"Mother's Day",color:'#db7093',icon:'\u{1F338}'}
];
function _settingsRenderHolidays(){
  var g=document.getElementById('settings-holiday-grid');
  if(!g)return;
  g.innerHTML=_holidayThemes.map(function(th){
    var active=th.id===_settings.activeTheme?'active':'';
    return '<div class="settings-theme-btn '+active+'" onclick="settingsSetTheme(\''+th.id+'\')">'
      +'<div class="settings-theme-swatch" style="background:'+th.color+';box-shadow:0 0 8px '+th.color+'66;"></div>'
      +th.icon+' '+th.name+'</div>';
  }).join('');
}

// === THEME SCHEDULER ===
var _holidayActive = false;

function scheduleCheck() {
  var schedules = JSON.parse(localStorage.getItem('themeSchedules') || '[]');
  var now = new Date();
  var month = now.getMonth() + 1;
  var day = now.getDate();
  for (var i = 0; i < schedules.length; i++) {
    var s = schedules[i];
    var sm = parseInt(s.start.split('/')[0]), sd = parseInt(s.start.split('/')[1]);
    var em = parseInt(s.end.split('/')[0]), ed = parseInt(s.end.split('/')[1]);
    var inRange = false;
    if (sm <= em) {
      inRange = (month > sm || (month === sm && day >= sd)) && (month < em || (month === em && day <= ed));
    } else {
      inRange = (month > sm || (month === sm && day >= sd)) || (month < em || (month === em && day <= ed));
    }
    if (inRange) {
      _holidayActive = true;
      applyTheme(s.themeId);
      return;
    }
  }
  _holidayActive = false;
}

function scheduleShowCreate() {
  var sel = document.getElementById('sch-theme');
  sel.innerHTML = _settings.themes.map(function(t) {
    return '<option value="' + t.id + '">' + t.name + '</option>';
  }).join('');
  document.getElementById('sch-name').value = '';
  document.getElementById('sch-start').value = '';
  document.getElementById('sch-end').value = '';
  document.getElementById('schedule-create').style.display = 'flex';
}

function scheduleHideCreate() {
  document.getElementById('schedule-create').style.display = 'none';
}

function scheduleSave() {
  var name = document.getElementById('sch-name').value.trim();
  var start = document.getElementById('sch-start').value.trim();
  var end = document.getElementById('sch-end').value.trim();
  var themeId = document.getElementById('sch-theme').value;
  if (!name || !start || !end) { alert('Fill in all fields.'); return; }
  var schedules = JSON.parse(localStorage.getItem('themeSchedules') || '[]');
  schedules.push({ id: Date.now(), name: name, themeId: themeId, start: start, end: end });
  localStorage.setItem('themeSchedules', JSON.stringify(schedules));
  scheduleHideCreate();
  scheduleRenderList();
  scheduleCheck();
}

function scheduleRenderList() {
  var el = document.getElementById('schedule-list');
  if (!el) return;
  var schedules = JSON.parse(localStorage.getItem('themeSchedules') || '[]');
  if (schedules.length === 0) {
    el.innerHTML = '<div style="color:var(--text-sub);text-align:center;padding:40px;font-size:15px;">No schedules yet. Tap + NEW to create one.</div>';
    return;
  }
  el.innerHTML = schedules.map(function(s) {
    var c = _themeColors[s.themeId];
    var color = c ? c.accent : '#1e5aff';
    return '<div style="display:flex;align-items:center;gap:14px;background:rgba(var(--accent-rgb),0.08);border:1px solid rgba(var(--accent-rgb),0.2);border-radius:10px;padding:14px 18px;margin-bottom:10px;">'
      + '<div style="width:14px;height:14px;border-radius:50%;background:' + color + ';flex-shrink:0;"></div>'
      + '<div style="flex:1;"><div style="font-size:16px;font-weight:700;">' + s.name + '</div>'
      + '<div style="font-size:13px;color:var(--text-sub);">' + s.start + ' → ' + s.end + ' · ' + s.themeId + '</div></div>'
      + '<button class="settings-btn" style="background:rgba(220,40,40,0.15);border-color:rgba(220,40,40,0.4);color:#fca5a5;" onclick="scheduleDelete(' + s.id + ')">🗑</button>'
      + '</div>';
  }).join('');
}

function scheduleDelete(id) {
  var schedules = JSON.parse(localStorage.getItem('themeSchedules') || '[]');
  schedules = schedules.filter(function(s) { return s.id !== id; });
  localStorage.setItem('themeSchedules', JSON.stringify(schedules));
  scheduleRenderList();
  scheduleCheck();
}

// === CAROUSEL ===
var _carouselTimer = null;

function carouselToggle(enabled) {
  var val = parseInt(document.getElementById('carousel-val').value) || 1;
  var unit = parseInt(document.getElementById('carousel-unit').value);
  localStorage.setItem('carouselEnabled', enabled ? '1' : '0');
  carouselSave();
  if (enabled) carouselStart(); else carouselStop();
}

function carouselSave() {
  var val = parseInt(document.getElementById('carousel-val').value) || 1;
  var unit = parseInt(document.getElementById('carousel-unit').value);
  localStorage.setItem('carouselInterval', val * unit);
}

function carouselStart() {
  if (_holidayActive) return;
  carouselStop();
  var interval = parseInt(localStorage.getItem('carouselInterval') || '3600000');
  _carouselTimer = setInterval(function() {
    if (_holidayActive) { carouselStop(); return; }
    var themes = _settings.themes;
    var idx = themes.findIndex(function(t) { return t.id === _settings.activeTheme; });
    var next = themes[(idx + 1) % themes.length];
    applyTheme(next.id);
  }, interval);
}

function carouselStop() {
  if (_carouselTimer) { clearInterval(_carouselTimer); _carouselTimer = null; }
}

function carouselInit() {
  var enabled = localStorage.getItem('carouselEnabled') === '1';
  var interval = parseInt(localStorage.getItem('carouselInterval') || '3600000');
  var toggle = document.getElementById('carousel-toggle');
  if (toggle) toggle.checked = enabled;
  var units = [60000, 3600000, 86400000, 604800000];
  var unitEl = document.getElementById('carousel-unit');
  var valEl = document.getElementById('carousel-val');
  for (var u of units) {
    if (interval % u === 0) {
      if (unitEl) unitEl.value = u;
      if (valEl) valEl.value = interval / u;
      break;
    }
  }
  if (enabled) carouselStart();
}

// Run on load
scheduleCheck();
setTimeout(carouselInit, 500);

// Re-render list when screen opens

