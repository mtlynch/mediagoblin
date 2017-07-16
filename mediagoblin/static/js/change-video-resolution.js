var glplayer;

$(document).ready(function()
{
  // fire up the plugin
  glplayer = videojs('video_1', {
    controls: true,
    muted: true,
    height: 400,
    width: 700,
    plugins: {
      videoJsResolutionSwitcher: {
        ui: true,
        default: 'low', // Default resolution [{Number}, 'low', 'high'],
        dynamicLabel: true // Display dynamic labels or gear symbol
      }
    }
  }, function(){
    var player = this;
    window.player = player
    player.on('resolutionchange', function(){
      console.info('Source changed to %s', player.src());
      console.log(player.currentTime());
    })
  })

  videojs.options.flash.swf = "https://ajax.cdnjs.com/ajax/libs/videojs-swf/5.4.0/video-js.swf"

});

/*

function myFunctionA() {
    glplayer.currentResolution('720p');
    console.log("clicked on A");
}

function myFunctionB() {
    glplayer.currentResolution('480p');
    console.log("clicked on A");
}

*/