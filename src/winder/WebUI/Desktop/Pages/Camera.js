function Camera( modules )
{
  var self = this

  // Constant jog speed for incremental moves.
  // Something small but reasonable.
  var JOG_SPEED = 50

  // How often to update the image from the camera.
  var CAMERA_UPDATE_RATE = 500

  // Dimensions of image from camera.
  var IMAGE_WIDTH  = 640
  var IMAGE_HEIGHT = 480

  var page = modules.get( "Page" )
  var winder = modules.get( "Winder" )

  var cameraTimer

  var lastCapture = {}

  var motorStatus
  modules.load
  (
    "/Desktop/Modules/MotorStatus",
    function()
    {
      motorStatus = modules.get( "MotorStatus" )
    }
  )

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

  $( "#triggerStartButton" )
    .click
    (
      function()
      {

        winder.remoteAction
        (
          "[ io.camera.cameraTriggerEnable.set( 1 ), io.camera.cameraTrigger.set( 1 ) ]",
          function()
          {
            //winder.remoteAction( "io.camera.cameraTrigger.set( 0 )" )
          }
        )

      }
    )

  $( "#triggerStopButton" )
    .click
    (
      function()
      {
        //winder.remoteAction( "process.manualSeekXY( 110., 300., 400., 200., 200. )" )
        winder.remoteAction( "io.camera.cameraTrigger.set( 0 )" )
      }
    )

  $( "#centerButton" )
    .click
    (
      function()
      {
        var pixelsPer_mm = 17.7734782609
        //parseFloat( $( "pixelsPer_mm" ).val() )

        // (Yes, x and y are reversed)
        var y = ( IMAGE_WIDTH  / 2 ) - parseFloat( lastCapture[ "x" ] )
        var x = ( IMAGE_HEIGHT / 2 ) - parseFloat( lastCapture[ "y" ] )

        x /= pixelsPer_mm
        y /= pixelsPer_mm

        x = parseFloat( motorStatus.motor[ "xPosition" ] ) + x
        y = parseFloat( motorStatus.motor[ "yPosition" ] ) - y

        winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + ", 50 )"  )
        //alert( x + " " + y )
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

  $( "#randomButton" )
    .click
    (
      function()
      {
        var command = 'io.camera.fillFIFO_WithRandom()'
        winder.remoteAction( command )
      }
    )

  $( "#scanButton" )
    .click
    (
      function()
      {
        var startPin = parseInt( $( "#startPin" ).val() )
        var endPin   = parseInt( $( "#endPin"   ).val() )
        var spacingX = parseFloat( $( "#spacingX" ).val() )
        var spacingY = parseFloat( $( "#spacingY" ).val() )
        var velocity = parseFloat( $( "#velocity" ).val() )

        var pinDelta = endPin - startPin

        var startX = motorStatus.motor[ "xPosition" ]
        var startY = motorStatus.motor[ "yPosition" ]
        var endX = startX + spacingX * pinDelta
        var endY = startY + spacingY * pinDelta

        var command =
          "process.startManualCalibrate( "
          + spacingX + ", "
          + spacingY + ", "
          + pinDelta + ", "
          + velocity + " )"

        winder.remoteAction( command )
      }
    )

  winder.addPeriodicDisplay( "io.camera.cameraResultStatus.get()", "#cameraResult", lastCapture, "status" )
  winder.addPeriodicDisplay( "io.camera.cameraResultScore.get()", "#cameraScore", lastCapture, "score" )
  winder.addPeriodicDisplay( "io.camera.cameraResultX.get()", "#cameraX", lastCapture, "x" )
  winder.addPeriodicDisplay( "io.camera.cameraResultY.get()", "#cameraY", lastCapture, "y" )

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  function line( canvas, x1, y1, x2, y2 )
  {
    canvas.beginPath()
    canvas.moveTo( x1, y1 )
    canvas.lineTo( x2, y2 )
    canvas.stroke()
  }

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  function crosshairs( canvas, x, y, length )
  {
    line( canvas, x - length, y, x + length, y )
    line( canvas, x, y - length, x, y + length )
  }

  //---------------------------------------------------------------------------
  // $$$DEBUG - Doesn't work.  Fix.
  //---------------------------------------------------------------------------
  function bigCrosshairs( canvas, x, y, length )
  {
    line( canvas, x - length, y - 1, x + length, y - 1 )
    line( canvas, x - length, y + 1, x + length, y + 1 )

    line( canvas, x - 1, y - length, x - 1, y + length )
    line( canvas, x + 1, y - length, x + 1, y + length )
  }

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  var count = 0
  var cameraURL
  var cameraUpdateFunction = function()
  {
    var url = cameraURL + "?random=" + Math.floor( Math.random() * 0xFFFFFFFF )
    $( "#cameraImage" )
      .attr( "src", url )
      .bind
      (
        "load",
        function()
        {
          var canvas = getCanvas( "cameraCanvas" )
          canvas.clearRect( 0, 0, IMAGE_WIDTH, IMAGE_HEIGHT )

          //canvas.lineWidth = 3
          //canvas.strokeStyle = "white"
          //crosshairs( canvas, IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2, 10 )

          canvas.lineWidth = 1
          canvas.strokeStyle = "black"
          crosshairs( canvas, IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2, 10 )
          //bigCrosshairs( canvas, IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2, 10 )

          canvas.strokeStyle = "Magenta"
          crosshairs( canvas, lastCapture[ "x" ], lastCapture[ "y" ], 10 )


        }
      )
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
        }
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

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  function round( value, decimals )
  {
    var multiplier = Math.pow( 10, decimals )
    return Math.round( value * multiplier ) / multiplier
  }

  var oldData = null

  //---------------------------------------------------------------------------
  // Uses:
  //   Get a canvas context by name.
  //---------------------------------------------------------------------------
  function getCanvas( canvasName )
  {
    var canvas = document.getElementById( canvasName )
    var context

    if ( canvas )
      context = canvas.getContext( "2d" )

    return context
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   $$$DEBUG
  //---------------------------------------------------------------------------
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

  var columnNames = [ "Pin",  "Motor X", "Motor Y", "Status", "Match", "Camera X", "Camera Y" ]
  var filters     = [ false,  false,     false,     true,     false,   false,      false      ]
  var widths      = [ "10%",  "15%",     "15%",     "15%",    "15%",   "15%",      "15%"      ]
  var filteredTable = new FilteredTable( columnNames, filters, widths )

  // Callback when a row on the calibration table is clicked.
  // The information from the row is put in the Select Pin table.
  filteredTable.setRowCallback
  (
    function( row )
    {
      var rowData = oldData[ row ]
      $( "#selectPin"  ).val( rowData[ "Pin" ] )
      $( "#selectPinX" ).val( rowData[ "MotorX" ] )
      $( "#selectPinY" ).val( rowData[ "MotorY" ] )
    }
  )

  var count = 0
  winder.addPeriodicCallback
  (
    "process.getCalibrationData()",
    function( data )
    {
      if ( isCaptureFIFO_Different( data, oldData ) )
      {
        oldData = data

        var cleanData = []
        for ( var rowIndex in data )
        {
          var row = data[ rowIndex ]
          cleanData.push
          (
            [
              row.Pin,
              round( row.MotorX, 2 ),
              round( row.MotorY, 2 ),
              row.Status,
              round( row.MatchLevel, 0 ),
              round( row.CameraX, 2 ),
              round( row.CameraY, 2 ),
            ]
          )
        }

        filteredTable.loadFromArray( cleanData )
        filteredTable.display( "#calibrationTable" )
      }

    }
  )

  loadCameraURL()

  var ENABLE_STATES =
  [
    {
      tl : true,
      t  : false,
      tr : true,
      l  : false,
      go : false,
      r  : false,
      bl : true,
      b  : false,
      br : true
    },

    {
      tl : false,
      t  : true,
      tr : false,
      l  : true,
      go : false,
      r  : true,
      bl : false,
      b  : true,
      br : false
    },

    {
      tl : false,
      t  : false,
      tr : false,
      l  : false,
      go : true,
      r  : false,
      bl : false,
      b  : false,
      br : false
    }
  ]

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  function setState( state )
  {
    for ( var tag in ENABLE_STATES[ state ] )
      $( "#" + tag ).prop( "disabled", ! ENABLE_STATES[ state ][ tag ] )
  }

  //---------------------------------------------------------------------------
  // $$$DEBUG
  //---------------------------------------------------------------------------
  var selectedCorner = null

  var OUTER =
  [
    "#tl",
    "#tr",
    "#bl",
    "#br",
    "#t",
    "#l",
    "#r",
    "#b"
  ]

  var CORNERS =
  [
    [ "#tl", "tl" ],
    [ "#tr", "tr" ],
    [ "#bl", "bl" ],
    [ "#br", "br" ]
  ]

  for ( var index in CORNERS )
  {
    let corner = CORNERS[ index ]
    $( corner[ 0 ] )
      .click
      (
        function()
        {
          $( corner[ 0 ] ).attr( "class", "selected" )
          selectedCorner = corner[ 1 ]
          setState( 1 )
        }
      )
  }

  var EDGES =
  [
    [ "#t", "t" ],
    [ "#l", "l" ],
    [ "#r", "r" ],
    [ "#b", "b" ]
  ]

  //

  var scanDirection
  for ( var index in EDGES )
  {
    let edge = EDGES[ index ]
    $( edge[ 0 ] )
      .click
      (
        function()
        {
          var selectedEdge = edge[ 1 ]
          var otherSelection = selectedCorner.replace( selectedEdge, "" )

          var DIRECTIONS =
          {
            l: "r",
            r: "l",
            t: "b",
            b: "t"
          }

          var direction = DIRECTIONS[ otherSelection ]

          scanDirection = otherSelection + direction

          var ARROWS =
          {
            lr: "&#8594;",
            rl: "&#8592;",
            tb: "&#8595;",
            bt: "&#8593;"
          }

          for ( var item in OUTER )
            if ( ( OUTER[ item ] != ( "#" + selectedEdge ) )
              && ( OUTER[ item ] != ( "#" + selectedCorner ) ) )
            {
                $( OUTER[ item ] ).attr( "class", "notSelected" )
            }

          $( edge[ 0 ] ).html( ARROWS[ scanDirection ] )

          setState( 2 )
        }
      )
  }

  setState( 0 )

  $( "#go" )
    .click
    (
      function()
      {
        $( "#tl" ).attr( "class", "" )
        $( "#tr" ).attr( "class", "" )
        $( "#bl" ).attr( "class", "" )
        $( "#br" ).attr( "class", "" )

        $( "#t" ).html( "&#8660;" ).attr( "class", "" )
        $( "#l" ).html( "&#8661;" ).attr( "class", "" )
        $( "#r" ).html( "&#8661;" ).attr( "class", "" )
        $( "#b" ).html( "&#8660;" ).attr( "class", "" )

        setState( 0 )
      }
    )

  $( "#selectPinSeek" )
    .click
    (
      function()
      {
        var x = parseFloat( $( "#selectPinX" ).val() )
        var y = parseFloat( $( "#selectPinY" ).val() )

        winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + ", 150 )"  )
      }
    )

  $( "#selectPinUseCurrent" )
    .click
    (
      function()
      {
        $( "#selectPinX" ).val( parseFloat( motorStatus.motor[ "xPosition" ] ) )
        $( "#selectPinY" ).val( parseFloat( motorStatus.motor[ "yPosition" ] ) )
      }
    )

  $( "#selectPinSave" )
    .click
    (
      function()
      {
        var pin = $( "#selectPin" ).val()
        var x = $( "#selectPinX" ).val()
        var y = $( "#selectPinY" ).val()
        winder.remoteAction( "process.setCalibrationData( " + pin + ", " + x + ", " + y + " )"  )
      }
    )

  // Register shutdown function that will stop the camera updates.
  modules.registerShutdownCallback
  (
    function()
    {
      if ( cameraTimer )
      {
        clearInterval( cameraTimer )
        cameraTimer = null
      }
    }

  )
}
