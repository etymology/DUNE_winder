function Camera( modules )
{
  var self = this

  // Constant jog speed for incremental moves.
  // Something small but reasonable.
  var JOG_SPEED = 50

  // How often to update the image from the camera.
  var CAMERA_UPDATE_RATE = 500

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
  var cameraURL
  var cameraUpdateFunction = function()
  {
    var url = cameraURL + "?random=" + Math.floor( Math.random() * 0xFFFFFFFF )
    $( "#cameraImage" )
      .attr( "src", url )
  }

  // Function to load the URL of the camera's last captured image.
  var loadCameraURL = function()
  {
    winder.remoteAction
    (
      "process.getCameraImageURL()",
      function( url )
      {
        cameraURL = url
        if ( cameraTimer )
        {
          clearInterval( cameraTimer )
          cameraTimer = null
        }

        cameraTimer = setInterval( cameraUpdateFunction, CAMERA_UPDATE_RATE )
      }
    )
  }

  // Shutdown/restart function to stop/restart camera updates.
  modules
    .registerShutdownCallback
    (
      function()
      {
        clearInterval( cameraTimer )
        cameraTimer = null
      }
    )
    .registerRestoreCallback( loadCameraURL )


  // Incremental jog.
  page.loadSubPage
  (
    "/Desktop/Modules/IncrementalJog",
    "#smallMotionsDiv",
    function()
    {
      var incrementalJog = modules.get( "IncrementalJog" )
      incrementalJog.velocityCallback
      (
        function()
        {
          return JOG_SPEED
        }
      )
    }
  )

  // Incremental jog.
  page.loadSubPage
  (
    "/Desktop/Modules/JogJoystick",
    "#jogJoystickDiv",
    function()
    {
      var jogJoystick = modules.get( "JogJoystick" )
      jogJoystick.callbacks
      (
        function()
        {
          return JOG_SPEED
        },
        function()
        {
          return "None"
        },
        function()
        {
          return "None"
        },
      )
    }
  )

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


  // $$$ var rand = function() { return Math.round( Math.random() * 10 ); }
  // $$$ var tempData = []
  // $$$ for ( var count = 0; count < 800; count += 1 )
  // $$$   tempData.push
  // $$$   (
  // $$$     { MotorX: rand(), MotorY: rand(), Status: rand(), MatchLevel: rand(), CameraX: rand(), CameraY: rand() },
  // $$$   )

  var oldData = null

  function isCaptureFIFO_Different( a, b )
  {
    var isDifferent = false

    isDifferent |= ! ( a instanceof Array )
    isDifferent |= ! ( b instanceof Array )

    if ( ! isDifferent )
      isDifferent |= ( a.length != b.length )

    if ( ! isDifferent )
    {
      for ( var index = 0; index < a.length; index += 1 )
      {
        var rowA = a[ index ]
        var rowB = b[ index ]

        for ( var key in rowA )
          isDifferent |= rowA[ key ] != rowB[ key ]
      }
    }

    return isDifferent
  }

  var count = 0
  winder.addPeriodicCallback
  (
    "io.camera.captureFIFO",
    function( data )
    {
      // $$$ count += 1
      // $$$ $( "#debugText" ).text( count )
      // $$$
      // $$$ data = tempData

      if ( isCaptureFIFO_Different( data, oldData ) )
      {
        oldData = data

        var table =
          $( "<table />" )
            .attr( "id", "calibrationTable" )

        var theadTag = $( "<thead />" ).appendTo( table )

        var rowTag = $( "<tr />" ).appendTo( theadTag )
        var heading = [ "Motor X", "Motor Y", "Status", "Match Level", "Camera X", "Camera Y" ]
        for ( var headingText of heading )
          $( "<th />" )
            .text( headingText )
            .appendTo( rowTag )

        var tbodyTag = $( "<tbody />" ).appendTo( table )

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

          var rowTag = $( "<tr />" ).appendTo( tbodyTag )
          for ( var columnIndex in rowData )
          {
            var column = rowData[ columnIndex ]
            $( "<td />" )
              .appendTo( rowTag )
              .text( column )
          }

        }

        $( "#calibrationTable" ).replaceWith( table )
      }
    }
  )

  loadCameraURL()
}
