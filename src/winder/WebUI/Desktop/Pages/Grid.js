function Grid()
{
  // Callback function to initialize position graphic.
  // Called twice--once when the position graphic page is loaded, and again
  // when the motor status page is loaded.  Both must be loaded before
  // initialization can take place, and either could load first.
  var positionGraphicCount = 2
  positionGraphicInitialize = function()
  {
    positionGraphicCount -= 1
    if ( 0 == positionGraphicCount )
      positionGraphic.initialize()
  }

  winder.loadSubPage
  (
    "/Desktop/Modules/positionGraphic",
    "#positionGraphicDiv",
    positionGraphicInitialize
  )

  winder.loadSubPage
  (
    "/Desktop/Modules/motorStatus",
    "#motorStatusDiv",
    positionGraphicInitialize
  )

  winder.loadSubPage
  (
    "/Desktop/Modules/gCode",
    "#gCodeDiv",
    function()
    {
      gCode.create( 3 )
    }
  )

  winder.loadSubPage
  (
    "/Desktop/Modules/recentLog",
    "#recentLogDiv",
    function()
    {
      recentLog.create( 10 )
    }
  )

}

//-----------------------------------------------------------------------------
// Uses:
//   Called when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    grid = new Grid()
  }
)
