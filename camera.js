async function _camLoadLive(){
  const cam=_cam.cameras[_cam.currentIdx];
  if(!cam)return;
  document.getElementById('cam-live-title').textContent=_camFmt(cam.name);
  const c=document.getElementById('cam-live-container');
  c.innerHTML='';
  var iframe=document.createElement('iframe');
  iframe.src=_GO2RTC+'/stream.html?src='+cam.name+'&mode=mse,mp4,mjpeg';
  iframe.style.cssText='width:100%;height:100%;border:1px solid rgba(var(--accent-rgb),0.3);border-radius:8px;background:#000;';
  iframe.allow='autoplay';
  iframe.setAttribute('frameborder','0');
  c.appendChild(iframe);
}
