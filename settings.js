var _themeApplyTransient=false;
const _settings = {
  themes: [
    {id:'void',name:'Void',color:'#00f0ff'},
    {id:'aquatic',name:'Aquatic',color:'#00b8a9'},
    {id:'abyss',name:'Abyss',color:'#06b6d4'},
    {id:'aurora',name:'Aurora',color:'#22d3ee'},
    {id:'autumn',name:'Autumn',color:'#f97316'},
    {id:'canyon',name:'Canyon',color:'#d97706'},
    {id:'cave',name:'Cave',color:'#22d3ee'},
    {id:'cosmos',name:'Cosmos',color:'#8b5cf6'},
    {id:'desert',name:'Desert',color:'#f59e0b'},
    {id:'emerald',name:'Emerald',color:'#10b981'},
    {id:'frost',name:'Frost',color:'#7dd3fc'},
    {id:'glow',name:'Glow',color:'#84cc16'},
    {id:'lava',name:'Lava',color:'#f97316'},
    {id:'reef',name:'Reef',color:'#22d3ee'},
    {id:'storm',name:'Storm',color:'#60a5fa'},
    {id:'sakura',name:'Sakura',color:'#fb7185'}
  ],
  activeTheme:'aquatic',
  navStack:[]
};

const _themeColors={
  void:{rgb:'0,240,255',accent:'#00f0ff',bg:'linear-gradient(to bottom, #001122 0%, #000a1a 40%, #000511 100%)',text:'#e0f8ff',sub:'#88ddff',notif:'rgba(0,80,120,0.45)',overlay:'rgba(0,10,20,0.97)',gauge:'#00f0ff',clock:'#00f0ff',clockFace:null,clockTicks:'#00f0ff',clockHands:'#00f0ff',clockSecond:'#ef4444'},
  aquatic:{rgb:'0,184,169',accent:'#00b8a9',bg:'linear-gradient(to bottom, #001a22 0%, #002833 40%, #00141a 100%)',text:'#e0f8f5',sub:'#6ee7d8',notif:'rgba(0,120,110,0.45)',overlay:'rgba(0,20,25,0.97)',gauge:'#00b8a9',clock:'#00b8a9',clockFace:null,clockTicks:'#00b8a9',clockHands:'#00b8a9',clockSecond:'#ef4444'},
  christmas:{rgb:'34,197,94',accent:'#22c55e',bg:'linear-gradient(to bottom, #0a1a0a 0%, #051505 40%, #0a0f0a 100%)',text:'#e0ffe8',sub:'#86efac',notif:'rgba(20,80,20,0.45)',overlay:'rgba(5,12,5,0.97)',gauge:'#dc2626',clock:'#f59e0b',navBg:'#dc2626',widgetBg:'#22c55e',bezelGlow:'#f59e0b',clockFace:null,clockTicks:'#22c55e',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  stpatricks:{rgb:'0,255,65',accent:'#00ff41',bg:'linear-gradient(to bottom, #001100 0%, #000a00 40%, #001100 100%)',text:'#a8f0c0',sub:'#6ee7a0',notif:'rgba(0,100,40,0.45)',overlay:'rgba(0,15,5,0.97)',gauge:'#00ff41',clock:'#d4a017',clockFace:null,clockTicks:'#00ff41',clockHands:'#d4a017',clockSecond:'#ef4444'},
  mothersday:{rgb:'219,112,147',accent:'#db7093',bg:'linear-gradient(to bottom, #1a0a10 0%, #0d0508 40%, #0a0d0d 100%)',text:'#ffe4e8',sub:'#c4848e',notif:'rgba(180,60,90,0.45)',overlay:'rgba(15,5,8,0.97)',gauge:'#db7093',clock:'#db7093',clockFace:null,clockTicks:'#db7093',clockHands:'#db7093',clockSecond:'#ef4444'},
  july4:{rgb:'220,38,38',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f8fafc',navBg:'#dc2626',widgetBg:'#1e3a8a',bezelGlow:'#f8fafc',clockFace:null,clockTicks:'#1e3a8a',clockHands:'#f8fafc',clockSecond:'#ef4444'},
  flagday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #1a0505 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,5,15,0.97)',gauge:'#cc2200',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#7f1d1d',bezelGlow:'#f8fafc',clockFace:null,clockTicks:'#1e3a8a',clockHands:'#f8fafc',clockSecond:'#ef4444'},
  laborday:{rgb:'107,114,128',accent:'#6b7280',bg:'linear-gradient(to bottom, #111827 0%, #0a0f18 40%, #111827 100%)',text:'#f8fafc',sub:'#d1d5db',notif:'rgba(107,114,128,0.45)',overlay:'rgba(10,15,25,0.97)',gauge:'#d1d5db',clock:'#f8fafc',navBg:'#374151',widgetBg:'#374151',bezelGlow:'#f8fafc',clockFace:null,clockTicks:'#6b7280',clockHands:'#f8fafc',clockSecond:'#ef4444'},
  veteransday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #1a0f05 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f59e0b',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f59e0b',clockFace:null,clockTicks:'#1e3a8a',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  memorialday:{rgb:'30,58,138',accent:'#1e3a8a',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#f8fafc',sub:'#93c5fd',notif:'rgba(30,58,138,0.45)',overlay:'rgba(5,8,20,0.97)',gauge:'#dc2626',clock:'#f8fafc',navBg:'#1e3a8a',widgetBg:'#1e3a8a',bezelGlow:'#f8fafc',clockFace:null,clockTicks:'#1e3a8a',clockHands:'#f8fafc',clockSecond:'#ef4444'},
  womensday:{rgb:'192,38,211',accent:'#c026d3',bg:'linear-gradient(to bottom, #1a0520 0%, #0f0215 40%, #1a0520 100%)',text:'#fff1f2',sub:'#f9a8d4',notif:'rgba(192,38,211,0.45)',overlay:'rgba(15,2,18,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#c026d3',widgetBg:'#c026d3',bezelGlow:'#f472b6',clockFace:null,clockTicks:'#c026d3',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  soviet:{rgb:'204,0,0',accent:'#cc0000',bg:'linear-gradient(to bottom, #1a0000 0%, #0f0000 40%, #1a0000 100%)',text:'#fff8e7',sub:'#fde68a',notif:'rgba(204,0,0,0.45)',overlay:'rgba(15,0,0,0.97)',gauge:'#f59e0b',clock:'#f59e0b',navBg:'#cc0000',widgetBg:'#cc0000',bezelGlow:'#f59e0b',clockFace:null,clockTicks:'#cc0000',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  easter:{rgb:'147,51,234',accent:'#9333ea',bg:'linear-gradient(to bottom, #1a0a2e 0%, #0f0518 40%, #1a0a2e 100%)',text:'#f8fafc',sub:'#e9d5ff',notif:'rgba(147,51,234,0.45)',overlay:'rgba(10,5,20,0.97)',gauge:'#4ade80',clock:'#f59e0b',navBg:'#9333ea',widgetBg:'#9333ea',bezelGlow:'#4ade80',clockFace:null,clockTicks:'#9333ea',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  valentine:{rgb:'190,18,60',accent:'#be123c',bg:'linear-gradient(to bottom, #1a0510 0%, #0f0208 40%, #1a0510 100%)',text:'#fff1f2',sub:'#fda4af',notif:'rgba(190,18,60,0.45)',overlay:'rgba(15,2,8,0.97)',gauge:'#f472b6',clock:'#f59e0b',navBg:'#be123c',widgetBg:'#be123c',bezelGlow:'#f472b6',clockFace:null,clockTicks:'#be123c',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  newyears:{rgb:'245,158,11',accent:'#f59e0b',bg:'linear-gradient(to bottom, #0a0a0f 0%, #05050a 40%, #0a0a0f 100%)',text:'#f8fafc',sub:'#cbd5e1',notif:'rgba(245,158,11,0.45)',overlay:'rgba(5,5,10,0.97)',gauge:'#e2e8f0',clock:'#f59e0b',navBg:'#f59e0b',widgetBg:'#0f172a',bezelGlow:'#f59e0b',clockFace:null,clockTicks:'#f59e0b',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  thanksgiving:{rgb:'146,64,14',accent:'#92400e',bg:'linear-gradient(to bottom, #1a0f05 0%, #0f0802 40%, #1a0f05 100%)',text:'#fef3c7',sub:'#fed7aa',notif:'rgba(146,64,14,0.45)',overlay:'rgba(15,8,2,0.97)',gauge:'#f97316',clock:'#f59e0b',navBg:'#92400e',widgetBg:'#92400e',bezelGlow:'#f59e0b',clockFace:null,clockTicks:'#92400e',clockHands:'#f59e0b',clockSecond:'#ef4444'},
  halloween:{rgb:'168,85,247',accent:'#a855f7',bg:'linear-gradient(to bottom, #0a0010 0%, #050008 40%, #0a0010 100%)',text:'#f0e0ff',sub:'#c4a5e0',notif:'rgba(80,20,140,0.45)',overlay:'rgba(8,0,15,0.97)',gauge:'#ff4500',clock:'#ff4500',navBg:'#a855f7',widgetBg:'#0a0a0a',bezelGlow:'#ff9933',clockFace:null,clockTicks:'#a855f7',clockHands:'#ff4500',clockSecond:'#ef4444'},
  abyss:{rgb:'6,182,212',accent:'#06b6d4',bg:'linear-gradient(to bottom, #021a24 0%, #011018 40%, #021a24 100%)',text:'#22d3ee',sub:'#0891b2',notif:'rgba(8,50,70,0.5)',overlay:'rgba(2,15,25,0.97)',gauge:'#06b6d4',clock:'#22d3ee',navBg:'#0e4d5e',widgetBg:'#083344',bezelGlow:'#22d3ee',clockFace:null,clockTicks:'#06b6d4',clockHands:'#22d3ee',clockSecond:'#ef4444'},
  aurora:{rgb:'34,211,238',accent:'#22d3ee',bg:'linear-gradient(to bottom, #0a0a1a 0%, #050510 40%, #0a0a1a 100%)',text:'#a5f3fc',sub:'#67e8f9',notif:'rgba(15,30,60,0.5)',overlay:'rgba(5,10,25,0.97)',gauge:'#22d3ee',clock:'#67e8f9',navBg:'#0e7490',widgetBg:'#164e63',bezelGlow:'#67e8f9',clockFace:null,clockTicks:'#22d3ee',clockHands:'#67e8f9',clockSecond:'#ef4444'},
  autumn:{rgb:'249,115,22',accent:'#f97316',bg:'linear-gradient(to bottom, #1a1008 0%, #0d0805 40%, #1a1008 100%)',text:'#fdba74',sub:'#fb923c',notif:'rgba(80,40,10,0.5)',overlay:'rgba(15,10,5,0.97)',gauge:'#f97316',clock:'#fb923c',navBg:'#7c2d12',widgetBg:'#431407',bezelGlow:'#fb923c',clockFace:null,clockTicks:'#f97316',clockHands:'#fb923c',clockSecond:'#ef4444'},
  canyon:{rgb:'217,119,6',accent:'#d97706',bg:'linear-gradient(to bottom, #1a1208 0%, #0d0a05 40%, #1a1208 100%)',text:'#fde68a',sub:'#fbbf24',notif:'rgba(60,30,10,0.5)',overlay:'rgba(15,10,5,0.97)',gauge:'#d97706',clock:'#fde68a',navBg:'#92400e',widgetBg:'#451a03',bezelGlow:'#fbbf24',clockFace:null,clockTicks:'#d97706',clockHands:'#fde68a',clockSecond:'#ef4444'},
  cave:{rgb:'34,211,238',accent:'#22d3ee',bg:'linear-gradient(to bottom, #0a1520 0%, #050c14 40%, #0a1520 100%)',text:'#ecfeff',sub:'#a5f3fc',notif:'rgba(10,40,60,0.5)',overlay:'rgba(5,15,25,0.97)',gauge:'#22d3ee',clock:'#67e8f9',navBg:'#155e75',widgetBg:'#0e3a4a',bezelGlow:'#67e8f9',clockFace:null,clockTicks:'#22d3ee',clockHands:'#67e8f9',clockSecond:'#ef4444'},
  cosmos:{rgb:'139,92,246',accent:'#8b5cf6',bg:'linear-gradient(to bottom, #0a0612 0%, #050308 40%, #0a0612 100%)',text:'#e9d5ff',sub:'#a5b4fc',notif:'rgba(76,29,149,0.5)',overlay:'rgba(10,6,20,0.97)',gauge:'#a78bfa',clock:'#a78bfa',navBg:'#4c1d95',widgetBg:'#1e1b4b',bezelGlow:'#22d3ee',clockFace:null,clockTicks:'#8b5cf6',clockHands:'#a78bfa',clockSecond:'#ef4444'},
  desert:{rgb:'245,158,11',accent:'#f59e0b',bg:'linear-gradient(to bottom, #1a1208 0%, #0d0a05 40%, #1a1208 100%)',text:'#fde68a',sub:'#fbbf24',notif:'rgba(60,40,10,0.5)',overlay:'rgba(15,10,5,0.97)',gauge:'#f59e0b',clock:'#fde68a',navBg:'#78350f',widgetBg:'#451a03',bezelGlow:'#fbbf24',clockFace:null,clockTicks:'#f59e0b',clockHands:'#fde68a',clockSecond:'#ef4444'},
  emerald:{rgb:'16,185,129',accent:'#10b981',bg:'linear-gradient(to bottom, #022c22 0%, #011a14 40%, #022c22 100%)',text:'#ecfdf5',sub:'#6ee7b7',notif:'rgba(6,95,70,0.5)',overlay:'rgba(2,20,16,0.97)',gauge:'#10b981',clock:'#6ee7b7',navBg:'#065f46',widgetBg:'#064e3b',bezelGlow:'#34d399',clockFace:null,clockTicks:'#10b981',clockHands:'#6ee7b7',clockSecond:'#ef4444'},
  frost:{rgb:'125,211,252',accent:'#7dd3fc',bg:'linear-gradient(to bottom, #0a1520 0%, #050a12 40%, #0a1520 100%)',text:'#bae6fd',sub:'#7dd3fc',notif:'rgba(15,40,60,0.5)',overlay:'rgba(5,15,25,0.97)',gauge:'#7dd3fc',clock:'#bae6fd',navBg:'#0c4a6e',widgetBg:'#082f49',bezelGlow:'#38bdf8',clockFace:null,clockTicks:'#7dd3fc',clockHands:'#bae6fd',clockSecond:'#ef4444'},
  glow:{rgb:'132,204,22',accent:'#84cc16',bg:'linear-gradient(to bottom, #0a1a0a 0%, #050d05 40%, #0a1a0a 100%)',text:'#bbf7d0',sub:'#86efac',notif:'rgba(20,60,20,0.5)',overlay:'rgba(5,15,5,0.97)',gauge:'#84cc16',clock:'#a3e635',navBg:'#3f6212',widgetBg:'#1a2e05',bezelGlow:'#a3e635',clockFace:null,clockTicks:'#84cc16',clockHands:'#a3e635',clockSecond:'#ef4444'},
  lava:{rgb:'249,115,22',accent:'#f97316',bg:'linear-gradient(to bottom, #1a0a05 0%, #0d0502 40%, #1a0a05 100%)',text:'#fdba74',sub:'#fb923c',notif:'rgba(80,30,10,0.5)',overlay:'rgba(15,5,2,0.97)',gauge:'#f97316',clock:'#fb923c',navBg:'#7c2d12',widgetBg:'#431407',bezelGlow:'#fb923c',clockFace:null,clockTicks:'#f97316',clockHands:'#fb923c',clockSecond:'#ef4444'},
  reef:{rgb:'34,211,238',accent:'#22d3ee',bg:'linear-gradient(to bottom, #021a24 0%, #011018 40%, #021a24 100%)',text:'#a5f3fc',sub:'#22d3ee',notif:'rgba(8,50,70,0.5)',overlay:'rgba(2,15,25,0.97)',gauge:'#22d3ee',clock:'#67e8f9',navBg:'#0e4d5e',widgetBg:'#083344',bezelGlow:'#67e8f9',clockFace:null,clockTicks:'#22d3ee',clockHands:'#67e8f9',clockSecond:'#ef4444'},
  storm:{rgb:'96,165,250',accent:'#60a5fa',bg:'linear-gradient(to bottom, #0a0f1a 0%, #050810 40%, #0a0f1a 100%)',text:'#eff6ff',sub:'#bfdbfe',notif:'rgba(20,40,80,0.5)',overlay:'rgba(5,10,20,0.97)',gauge:'#60a5fa',clock:'#93c5fd',navBg:'#1e3a8a',widgetBg:'#172554',bezelGlow:'#93c5fd',clockFace:null,clockTicks:'#60a5fa',clockHands:'#93c5fd',clockSecond:'#ef4444'},
  sakura:{rgb:'251,113,133',accent:'#fb7185',bg:'linear-gradient(to bottom, #1a0a12 0%, #0d0508 40%, #1a0a12 100%)',text:'#fecdd3',sub:'#fb7185',notif:'rgba(120,40,60,0.5)',overlay:'rgba(15,5,10,0.97)',gauge:'#fb7185',clock:'#fda4af',navBg:'#9f1239',widgetBg:'#4c0519',bezelGlow:'#fda4af',clockFace:null,clockTicks:'#fb7185',clockHands:'#fda4af',clockSecond:'#ef4444'}
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
  if(!_themeApplyTransient)localStorage.setItem('dashBaseTheme',id);
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
      if(_settings.activeTheme!==s.themeId){_themeApplyTransient=true;applyTheme(s.themeId);_themeApplyTransient=false;}
      return;
    }
  }
  if(_holidayActive){
    var base=localStorage.getItem('dashBaseTheme');
    if(base&&_themeColors[base]&&base!==_settings.activeTheme)applyTheme(base);
  }
  _holidayActive = false;
}
function _scheduleMidnightTimer(){
  var n=new Date(),m=new Date(n.getFullYear(),n.getMonth(),n.getDate()+1,0,0,30);
  setTimeout(function(){scheduleCheck();_scheduleMidnightTimer();},m-n);
}

function scheduleShowCreate() {
  var sel = document.getElementById('sch-theme');
  sel.innerHTML = _settings.themes.concat(_holidayThemes).map(function(t) {
    return '<option value="' + t.id + '">' + t.name + '</option>';
  }).join('');
  document.getElementById('sch-start-m').value = '1';
  document.getElementById('sch-start-d').value = '1';
  document.getElementById('sch-end-m').value = '1';
  document.getElementById('sch-end-d').value = '1';
  document.getElementById('schedule-create').style.display = 'flex';
}

function scheduleHideCreate() {
  document.getElementById('schedule-create').style.display = 'none';
}

function scheduleSave() {
  var themeId = document.getElementById('sch-theme').value;
  var sm = document.getElementById('sch-start-m').value;
  var sd = document.getElementById('sch-start-d').value;
  var em = document.getElementById('sch-end-m').value;
  var ed = document.getElementById('sch-end-d').value;
  if (!sm || !sd || !em || !ed) { alert('Pick start and end month and day.'); return; }
  var start = sm + '/' + sd;
  var end = em + '/' + ed;
  var all = _settings.themes.concat(_holidayThemes);
  var t = all.find(function(x){ return x.id === themeId; });
  var name = (t ? t.name : themeId) + ' ' + start + '\u2013' + end;
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
if(!localStorage.getItem('dashBaseTheme'))localStorage.setItem('dashBaseTheme',localStorage.getItem('dashTheme')||'aquatic');
scheduleCheck();
_scheduleMidnightTimer();
setTimeout(carouselInit, 500);

// Re-render list when screen opens

