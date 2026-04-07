const _settings={
  themes:[
    {id:'water',name:'Deep Water',color:'#1e5aff'},
    {id:'titanium',name:'Titanium',color:'#8ea4d4'},
    {id:'emerald',name:'Dark Emerald',color:'#10b981'},
    {id:'purple',name:'Electric Purple',color:'#a855f7'},
  ],
  activeTheme:'water',
  navStack:[]
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
  if(id==='about')_settingsLoadSysInfo();if(id==='holiday_themes')_settingsRenderHolidays();
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
    return '<div class="settings-theme-btn '+(th.id===_settings.activeTheme?'active':'')+'" onclick="settingsSetTheme(\''+th.id+'\')"><div class="settings-theme-swatch" style="background:'+th.color+';box-shadow:0 0 8px '+th.color+'66;"></div>'+th.name+'</div>';
  }).join('');
}
function settingsSetTheme(id){applyTheme(id);}
async function settingsBrightness(val){
  document.getElementById('settings-brightness-val').textContent=val+'%';
  try{await fetch('/api/brightness',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({value:parseInt(val)})});}catch(e){}
}
async function _settingsLoadSysInfo(){
  try{var r=await fetch('/api/sysinfo');var d=await r.json();
  document.getElementById('settings-hostname').textContent=d.hostname||'—';
  document.getElementById('settings-ip').textContent=d.ip||'—';
  document.getElementById('settings-tailscale').textContent=d.tailscale||'—';
  document.getElementById('settings-uptime').textContent=d.uptime||'—';
  }catch(e){}
}
async function settingsDisplayOn(){
  try{await fetch('/api/display',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:'on'})});}catch(e){}
}
async function settingsDisplayOff(){
  try{await fetch('/api/display',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:'off'})});}catch(e){}
}
const _themeColors={
  water:{rgb:'30,90,255',accent:'#1e5aff',bg:'linear-gradient(to bottom, #0a2a6e 0%, #051c35 40%, #03112a 100%)',text:'#e0e8ff',sub:'#8ea4d4',notif:'rgba(0,47,178,0.45)',overlay:'rgba(4,10,35,0.97)',gauge:'#1e5aff',clock:'#1e5aff'},
  titanium:{rgb:'143,170,184',accent:'#8faab8',bg:'linear-gradient(165deg, #3a4550 0%, #2d363f 30%, #4a555f 60%, #2a333c 100%)',text:'#d8e4ec',sub:'#8faab8',notif:'rgba(45,54,63,0.7)',overlay:'rgba(20,25,30,0.97)',gauge:'#8faab8',clock:'#8faab8'},
  emerald:{rgb:'16,185,129',accent:'#10b981',bg:'linear-gradient(to bottom, #0a2e1f 0%, #051c14 40%, #031210 100%)',text:'#e0f5ee',sub:'#6ee7b7',notif:'rgba(4,80,60,0.45)',overlay:'rgba(2,15,12,0.97)',gauge:'#10b981',clock:'#10b981'},
  purple:{rgb:'168,85,247',accent:'#a855f7',bg:'linear-gradient(to bottom, #2a0a4a 0%, #1a0535 40%, #0f0320 100%)',text:'#f0e0ff',sub:'#c4a5e0',notif:'rgba(80,20,140,0.45)',overlay:'rgba(12,4,30,0.97)',gauge:'#a855f7',clock:'#a855f7'},
  christmas:{rgb:'34,197,94',accent:'#22c55e',bg:'linear-gradient(to bottom, #1a0a0a 0%, #0f0505 40%, #0a1a0a 100%)',text:'#e0ffe8',sub:'#86efac',notif:'rgba(20,80,20,0.45)',overlay:'rgba(5,12,5,0.97)',gauge:'#22c55e',clock:'#22c55e'},
  stpatricks:{rgb:'22,163,74',accent:'#16a34a',bg:'linear-gradient(to bottom, #0a1f0f 0%, #051a0a 40%, #031208 100%)',text:'#e0ffe8',sub:'#6ee7a0',notif:'rgba(10,70,30,0.45)',overlay:'rgba(3,12,6,0.97)',gauge:'#16a34a',clock:'#16a34a'}
};
function applyTheme(id){console.log("THEME:",id);document.title="Theme:"+id;
  var c=_themeColors[id];if(!c)return;
  var r=document.documentElement.style;
  r.setProperty('--accent-rgb',c.rgb);
  r.setProperty('--accent',c.accent);
  r.setProperty('--bg',c.bg);
  r.setProperty('--text',c.text);
  r.setProperty('--text-sub',c.sub);
  r.setProperty('--notif-bg',c.notif);
  r.setProperty('--overlay-bg',c.overlay);
  _settings.activeTheme=id;
  localStorage.setItem('dashTheme',id);
  _settingsRenderThemes();
}

(function(){
  var saved=localStorage.getItem('dashTheme');
  if(saved && _themeColors[saved]) applyTheme(saved);
})();

var _holidayThemes=[
  {id:'christmas',name:'Christmas',color:'#22c55e',icon:'\u{1F384}'},
  {id:'stpatricks',name:"St. Patrick's",color:'#16a34a',icon:'\u{2618}\u{FE0F}'}
];
function _settingsRenderHolidays(){
  var g=document.getElementById('settings-holiday-grid');
  if(!g)return;
  g.innerHTML=_holidayThemes.map(function(th){
    return '<div class="settings-theme-btn '+(th.id===_settings.activeTheme?'active':'')+'" onclick="settingsSetTheme(\''+th.id+'\')">'
    +'<div class="settings-theme-swatch" style="background:'+th.color+';box-shadow:0 0 8px '+th.color+'66;"></div>'
    +th.icon+' '+th.name+'</div>';
  }).join('');
}
