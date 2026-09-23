function secs(t){return t>1e12?t/1000:t}
function ageMin(t){return t?(Date.now()/1000-secs(t))/60:1e9}
function ago(t){
 if(!t)return 'never';
 const m=ageMin(t);
 if(m<60)return Math.round(m)+' min ago';
 if(m<2880)return Math.round(m/60)+' h ago';
 return new Date(secs(t)*1000).toLocaleDateString(undefined,{month:'short',day:'numeric'});
}
async function sensors(){
 try{
  const d=await (await fetch('/api/sensors')).json(), o={};
  (d.sensors||[]).forEach(x=>o[x.id]=x);
  return o;
 }catch(e){return {}}
}
