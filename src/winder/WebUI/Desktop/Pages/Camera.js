function Camera( modules )
{
  var self = this

  var page = modules.get( "Page" )
  var winder = modules.get( "Winder" )

  var cameraTimer

  // Motor status.
  page.loadSubPage
  (
    "/Desktop/Modules/MotorStatus",
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

    cameraTimer = setTimeout( cameraUpdateFunction, 100 )
  }

  // Shutdown/restart function to stop/restart camera updates.
  modules
    .registerShutdownCallback
    (
      function()
      {
        clearTimeout( cameraTimer )
      }
    )
    .registerRestoreCallback( cameraUpdateFunction )

  cameraUpdateFunction()
}

// //-----------------------------------------------------------------------------
// // Uses:
// //   Called when page loads.
// //-----------------------------------------------------------------------------
// $( document ).ready
// (
//   function()
//   {
//     //winder.inhibitUpdates()
//     camera = new Camera()
//   }
// )
//