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
          "io.camera.cameraTrigger.set( 1 )",
          function()
          {
            //winder.remoteAction( "io.camera.cameraTrigger.set( 0 )" )
          }
        )

      }
    )

  $( "#moveStart" )
    .click
    (
      function()
      {
        winder.remoteAction( "process.manualSeekXY( 110., 300., 400., 200., 200. )" )
      }
    )

  $( "#moveEnd" )
    .click
    (
      function()
      {
        winder.remoteAction( "process.manualSeekXY( 110., 600., 400., 200., 200. )" )
      }
    )

  $( "#reset" )
    .click
    (
      function()
      {
        //winder.remoteAction( "io.camera.cameraDeltaEnable.set( False )" )
        winder.remoteAction( "io.camera.reset()" )
      }
    )

  $( "#startUp" )
    .click
    (
      function()
      {
        // var command = "[" +
        //   "io.camera.cameraDeltaEnable.set( 0 )," +
        //   "io.camera.cameraTriggerEnable.set( 1 )," +
        //   "io.camera.cameraX_Delta.set( 0 )," +
        //   "io.camera.cameraY_Delta.set( 8 )," +
        //   "io.camera.cameraDeltaEnable.set( 1 )," +
        //   "process.manualSeekXY( 110., 600., 50., 200., 200. ) ]"
        var command = 'process.startCalibrationScanEdge( "LT", 50 )'

        winder.remoteAction( command )
      }
    )

  $( "#startDown" )
    .click
    (
      function()
      {
        var command = "[" +
          "io.camera.cameraDeltaEnable.set( 0 )," +
          "io.camera.cameraTriggerEnable.set( 1 )," +
          "io.camera.cameraX_Delta.set( 0 )," +
          "io.camera.cameraY_Delta.set( -8 )," +
          "io.camera.cameraDeltaEnable.set( 1 )," +
          "process.manualSeekXY( 110., 300., 50., 200., 200. ) ]"

        winder.remoteAction( command )
      }
    )

  winder.addPeriodicDisplay( "io.camera.cameraResultStatus.get()", "#cameraResult" )
  winder.addPeriodicDisplay( "io.camera.cameraResultScore.get()", "#cameraScore" )
  winder.addPeriodicDisplay( "io.camera.cameraResultX.get()", "#cameraX" )
  winder.addPeriodicDisplay( "io.camera.cameraResultY.get()", "#cameraY" )

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


  // Filter table object with columns for the log file.
  var filteredTable =
      new FilteredTable
      (
        [ "Motor X", "Motor Y", "Status", "Match Level", "Camera X", "Camera Y" ],
        [ false, false, false, false, false, false ],
        []
      )


  function round( value, decimals )
  {
    var multiplier = Math.pow( 10, decimals )
    return Math.round( value * multiplier ) / multiplier
  }


  winder.addPeriodicCallback
  (
    "io.camera.captureFIFO",
    function( data )
    {
      var table = $( "<table />" )
        .attr( "id", "calibrationTable" )

      var rowTag = $( "<tr />" ).appendTo( table )
      var heading = [ "Motor X", "Motor Y", "Status", "Match Level", "Camera X", "Camera Y" ]
      for ( var headingText of heading )
          $( "<th />" )
            .text( headingText )
            .appendTo( rowTag )


      for ( var row of data )
      {
        var rowData =
          [
            round( row.MotorX, 2 ),
            round( row.MotorY, 2 ),
            row.Status,
            row.MatchLevel,
            round( row.CameraX, 2 ),
            round( row.CameraY, 2 ),
          ]

        var rowTag = $( "<tr />" ).appendTo( table )
        for ( var columnIndex in rowData )
        {
          var column = rowData[ columnIndex ]
          $( "<td />" )
            .appendTo( rowTag )
            .text( column )
        }

        // $( "<td />" )
        //   .appendTo( rowTag )
        //   .text( "-" )
      }

      $( "#calibrationTable" ).replaceWith( table )


      // var dataSet = []
      // for ( var row of data )
      // {
      //
      //   dataSet.push( rowData )
      // }
      //
      // filteredTable.loadFromArray( dataSet )
      // filteredTable.display( "#calibrationTable" )
    }
  )

  cameraUpdateFunction()
}
