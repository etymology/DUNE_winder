
//=============================================================================
// Master class for screen.
//=============================================================================
function Camera()
{
  var self = this

  // Motor status.
  winder.loadSubPage
  (
    "/Desktop/Modules/motorStatus",
    "#motorStatusDiv",
    function()
    {
      // Setup copy fields for motor positions.  Allows current motor positions
      // to be copied to input fields.
      var x = new CopyField( "#xPosition", "#xPositionCell" )
      var y = new CopyField( "#yPosition", "#yPositionCell" )
      var z = new CopyField( "#zPosition", "#zPositionCell" )
    }
  )

  $( "#cameraTriggerButton" )
    .click
    (
      function()
      {

        winder.remoteAction
        (
          "io.plcLogic.cameraTrigger.set( 1 )",
          function()
          {
            //winder.remoteAction( "io.plcLogic.cameraTrigger.set( 0 )" )
          }
        )

      }
    )

  winder.addPeriodicDisplay( "io.plcLogic.cameraResultStatus.get()", "#cameraResult" )
  winder.addPeriodicDisplay( "io.plcLogic.cameraResultScore.get()", "#cameraScore" )
  winder.addPeriodicDisplay( "io.plcLogic.cameraResultX.get()", "#cameraX" )
  winder.addPeriodicDisplay( "io.plcLogic.cameraResultY.get()", "#cameraY" )

  var count = 0
  var cameraUpdateFunction = function()
  {
    var url = "ftp://admin@192.168.16.55/image.bmp?random=" + Math.floor( Math.random() * 0xFFFFFFFF )
    $( "#cameraImage" )
      .attr( "src", url )

    count += 1
    $( "#debugText" ).text( count )

    setTimeout( cameraUpdateFunction, 100 )
  }

  cameraUpdateFunction()

  $( "#customCommandButton" )
    .click
    (
      function()
      {
        var command = $( "#customCommand" ).val()
        winder.remoteAction
        (
          command,
          function( data )
          {
            $( "#customCommandResult" ).val( data )
          }
        )
      }
    )

}

//-----------------------------------------------------------------------------
// Uses:
//   Call when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    //winder.inhibitUpdates()
    camera = new Camera()
  }
)
