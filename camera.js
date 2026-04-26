function _camOpenFrigate(cameraId) {
  var iframe = document.getElementById('cam-frigate-iframe');
  if (!iframe) return;
  var host = window.location.hostname;
  var path = cameraId ? ('/cameras/' + cameraId) : '/';
  iframe.src = 'http://' + host + ':8082' + path;
}
function _camStopStreams() {
  var iframe = document.getElementById('cam-frigate-iframe');
  if (iframe) iframe.src = 'about:blank';
  var vid = document.getElementById('cam-playback-video');
  if (vid) { vid.pause(); vid.src = ''; }
}
