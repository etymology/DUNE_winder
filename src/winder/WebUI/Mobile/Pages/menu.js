function Main()
{
  var self = this
}

//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
function toggleFullscreen()
{
  var isFullScreen =
    (
      document.fullscreenElement
      || document.mozFullScreenElement
      || document.webkitFullscreenElement
    )

  if ( ! isFullScreen )
  {
    var element = document.documentElement
    if ( element.requestFullscreen )
      element.requestFullscreen()
    else
    if ( element.mozRequestFullScreen )
      element.mozRequestFullScreen()
    else
    if ( element.webkitRequestFullscreen )
      element.webkitRequestFullscreen()
    else
    if ( element.msRequestFullscreen )
      element.msRequestFullscreen()
  }
  else
  {
    if ( document.exitFullscreen )
      document.exitFullscreen()
    else
    if ( document.mozCancelFullScreen )
      document.mozCancelFullScreen()
    else
    if ( document.webkitExitFullscreen )
      document.webkitExitFullscreen()
  }

}

//-----------------------------------------------------------------------------
// Uses:
//   Called when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    main = new Main()
  }
);
