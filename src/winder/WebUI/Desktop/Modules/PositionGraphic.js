function PositionGraphic( modules )
{
  var self = this

  // Number of path lines to leave on screen.
  var LINES = 25

  // Default scale factor for all images.
  var DEFAULT_SCALE = 1.0

  // Limits of image (in pixels).
  // Simi-constants come from images used.  Simi-constant because they are
  // scaled at class creation.
  var BASE_GRAPHIC_X = 1286
  var BASE_GRAPHIC_Y = 463
  var Z_GRAPHIC_X    = 1500
  var Z_GRAPHIC_Y    = 332
  var MIN_X          = 95
  var MAX_X          = 1065
  var MIN_Y          = 393
  var MAX_Y          = 17
  var HEAD_X_OFFSET  = 100
  var MIN_ARM_Z      = 0
  var MAX_ARM_Z      = 281
  var MIN_HEAD_Z     = 783
  var MAX_HEAD_Z     = 1064
  var LINE_OFFSET_X  = 129
  var LINE_OFFSET_Y  = 30
  var Z_HEAD_ARM_X   = 843
  var Z_HEAD_ARM_Y   = 105
  var Z_HEAD_ARM_MIN_WIDTH = 20
  var Z_HEAD_ARM_MAX_WIDTH = 90
  var Z_HEAD_ARM_HEIGHT    = 20
  var HEAD_ANGLE_X      = 60
  var HEAD_ANGLE_Y      = 60
  var HEAD_ANGLE_RADIUS = 50

  var winder
  var motorStatus
  var runStatus

  // Storage location for additional variables read for setup.
  var readData = {}

  // Images to hide if server stops communicating.
  var IMAGES_TO_HIDE =
  [
    "#pathCanvas",
    "#seekCanvas",
    "#zStatusCanvas"
  ]

  // Images to blur if server stops communicating.
  var IMAGES_TO_BLUR =
  [
    "#loopImage",
    "#headImage",
    "#zHeadImage",
    "#zArmImage",
  ]

  // Scale factor for all images.
  var scale

  // Position debouce to keep deal with the asynchronous nature of desired X/Y
  // positions.
  var debounceLastX = null
  var debounceLastY = null
  var debounceX = null
  var debounceY = null

  var motorX = null
  var motorY = null
  var wasMoving = false

  var lastX = null
  var lastY = null
  var startingX = null
  var startingY = null
  var lines = []

  var machineCaliration
  var inputs

  //---------------------------------------------------------------------------
  // Uses:
  //   Set the state of a status light on the Z image.
  // Input:
  //   x - Location in x.
  //   y - Location in y.
  //   status - State of light.
  //   offIsError - False if being off (false) is ok, or true if this is an error.
  //---------------------------------------------------------------------------
  var statusLight = function( zStatusCanvas, x, y, status, offIsError )
  {
    // Scale locations.
    x *= scale
    y *= scale

    // Select the color of the light indicator.
    if ( status )
    {
      zStatusCanvas.fillStyle = "lime"
      zStatusCanvas.strokeStyle = "green"
    }
    else
    if ( ! offIsError )
    {
      zStatusCanvas.fillStyle = "blue"
      zStatusCanvas.strokeStyle = "darkBlue"
    }
    else
    {
      zStatusCanvas.fillStyle = "red"
      zStatusCanvas.strokeStyle = "darkRed"
    }

    // Draw a circle at the specified location.
    zStatusCanvas.beginPath()
    zStatusCanvas.arc( x, y, 8 * scale, 0, 2 * Math.PI )

    // Draw fill (do before border).
    zStatusCanvas.fill()

    // Draw border.
    zStatusCanvas.lineWidth = 2 * scale
    zStatusCanvas.stroke()
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Callback run after machine calibration has been acquired.  Sets up
  //   periodic function to update graphics.
  //---------------------------------------------------------------------------
  var setupCallback = function()
  {
    var baseGraphicWidth  = BASE_GRAPHIC_X * scale
    var baseGraphicHeight = BASE_GRAPHIC_Y * scale

    // Scale limits of image.
    Z_GRAPHIC_X   *= scale
    Z_GRAPHIC_Y   *= scale
    MIN_X         *= scale
    MAX_X         *= scale
    MIN_Y         *= scale
    MAX_Y         *= scale
    HEAD_X_OFFSET *= scale
    MIN_ARM_Z     *= scale
    MAX_ARM_Z     *= scale
    MIN_HEAD_Z    *= scale
    MAX_HEAD_Z    *= scale
    LINE_OFFSET_X *= scale
    LINE_OFFSET_Y *= scale
    Z_HEAD_ARM_X  *= scale
    Z_HEAD_ARM_Y  *= scale
    Z_HEAD_ARM_MIN_WIDTH *= scale
    Z_HEAD_ARM_MAX_WIDTH *= scale
    Z_HEAD_ARM_HEIGHT    *= scale
    HEAD_ANGLE_X         *= scale
    HEAD_ANGLE_Y         *= scale
    HEAD_ANGLE_RADIUS    *= scale

    // Limits of travel (in mm).
    var MIN_X_POSITION = machineCaliration[ "limitLeft" ]
    var MAX_X_POSITION = machineCaliration[ "limitRight" ]
    var MIN_Y_POSITION = machineCaliration[ "limitBottom" ]
    var MAX_Y_POSITION = machineCaliration[ "limitTop" ]
    var MIN_Z_POSITION = machineCaliration[ "zFront" ]
    var MAX_Z_POSITION = machineCaliration[ "zBack" ]

    $( "#pathCanvas" )
      .attr( "width",  baseGraphicWidth  + "px" )
      .attr( "height", baseGraphicHeight + "px"  )

    $( "#seekCanvas" )
      .attr( "width",  baseGraphicWidth  + "px" )
      .attr( "height", baseGraphicHeight + "px"  )

    $( "#zStatusCanvas" )
      .attr( "width",  Z_GRAPHIC_X  + "px" )
      .attr( "height", Z_GRAPHIC_Y + "px"  )

    // Image position
    winder.addPeriodicEndCallback
    (
      function()
      {
        if ( ! motorStatus.motor[ "yFunctional" ] )
          $( "#loopImage" ).addClass( "axisFault" )
        else
          $( "#loopImage" ).removeClass( "axisFault" )

        // Motor position history.
        debounceLastX = debounceX
        debounceLastY = debounceY
        debounceX = Math.round( motorStatus.motor[ "xDesiredPosition" ] )
        debounceY = Math.round( motorStatus.motor[ "yDesiredPosition" ] )

        // Debounce motor positions.
        // This is done because the X and Y destinations change asynchronously.
        // To ensure they stay in step, they both must match their previous
        // value twice in a row.
        if ( ( debounceLastX == debounceX )
          && ( debounceLastY == debounceY ) )
        {
          motorX = debounceX
          motorY = debounceY
        }

        // Rescale value based on sizes.
        var rescale =
          function( value, outMin, outMax, inMin, inMax, offset )
          {
            var result = outMax - outMin
            result *= value - inMin
            result /= ( inMax - inMin )
            result += outMin + offset

            return result
          }

        // Axis positions.  Round to keep graphic from jittering.
        var xPosition = Math.round( motorStatus.motor[ "xPosition" ] )
        var yPosition = Math.round( motorStatus.motor[ "yPosition" ] )
        var zPosition = Math.round( motorStatus.motor[ "zPosition" ] )

        //
        // Position loop (X/Y image).
        //

        var x = rescale( xPosition, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, 0 )

        $( "#loopImage" )
          .css( "left", x + "px" )

        var y = rescale( yPosition, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, 0 )

        //
        // Position head (X/Y image).
        //
        x += HEAD_X_OFFSET

        $( "#headImage" )
          .css( "left", x + "px" )
          .css( "top", y + "px" )

        //
        // Position head (Z image).
        //
        var zHead = rescale( zPosition, MIN_HEAD_Z, MAX_HEAD_Z, MIN_Z_POSITION, MAX_Z_POSITION, 0 )

        if ( 0 != motorStatus.motor[ "headSide" ] )
          zHead = MAX_HEAD_Z

        $( "#zHeadImage" )
          .css( "left", zHead + "px" )

        //
        // Position arm (Z image).
        //
        var zArm = rescale( zPosition, MIN_ARM_Z, MAX_ARM_Z, MIN_Z_POSITION, MAX_Z_POSITION, 0 )

        $( "#zArmImage" )
          .css( "left", zArm + "px" )

        var zStatusCanvas = document.getElementById( "zStatusCanvas" ).getContext( "2d" )
        zStatusCanvas.clearRect( 0, 0, Z_GRAPHIC_X, Z_GRAPHIC_Y )

        //
        // Draw angle of arm on head.
        //
        var z = zPosition
        if ( 0 != motorStatus.motor[ "headSide" ] )
          z = MAX_Z_POSITION

        var zHeadArm =
          rescale
          (
            z,
            MIN_ARM_Z,
            MAX_ARM_Z,
            MIN_Z_POSITION,
            MAX_Z_POSITION,
            Z_HEAD_ARM_X
          )

        var zHeadArmWidth = ( Z_HEAD_ARM_MAX_WIDTH - Z_HEAD_ARM_MIN_WIDTH )
        zHeadArmWidth *= -Math.sin( readData[ 'headAngle' ] )

        if ( zHeadArmWidth < 0 )
        {
          zHeadArm += zHeadArmWidth
          zHeadArmWidth = Z_HEAD_ARM_MIN_WIDTH - zHeadArmWidth
        }
        else
          zHeadArmWidth += Z_HEAD_ARM_MIN_WIDTH

        zStatusCanvas.fillStyle = "grey"
        zStatusCanvas.fillRect
        (
          zHeadArm,
          Z_HEAD_ARM_Y,
          zHeadArmWidth,
          Z_HEAD_ARM_HEIGHT
        )
        zStatusCanvas.strokeStyle = "black"
        zStatusCanvas.lineWidth = 1 * scale
        zStatusCanvas.strokeRect
        (
          zHeadArm,
          Z_HEAD_ARM_Y,
          zHeadArmWidth,
          Z_HEAD_ARM_HEIGHT
        )

        var radius = HEAD_ANGLE_RADIUS
        zStatusCanvas.beginPath()
        zStatusCanvas.arc( HEAD_ANGLE_X, HEAD_ANGLE_Y, radius, 0, 2 * Math.PI )
        zStatusCanvas.lineWidth = 2 * scale
        zStatusCanvas.stroke()

        zStatusCanvas.beginPath()
        var x = -Math.sin( readData[ 'headAngle' ] ) * radius
        var y =  Math.cos( readData[ 'headAngle' ] ) * radius
        zStatusCanvas.moveTo( HEAD_ANGLE_X, HEAD_ANGLE_Y )
        zStatusCanvas.lineTo( x + HEAD_ANGLE_X, y + HEAD_ANGLE_Y )
        zStatusCanvas.lineWidth = 2 * scale
        zStatusCanvas.stroke()

        //
        // Update status lights on Z image.
        // NOTE: Constants come for positions on image.
        //

        statusLight( zStatusCanvas, 485, 150, ! inputs[ "Z_End_of_Travel" ], true )
        statusLight( zStatusCanvas, 505, 150, inputs[ "Z_Retracted_1A" ] )

        statusLight( zStatusCanvas, 545, 150, ! inputs[ "Z_End_of_Travel" ], true )
        statusLight( zStatusCanvas, 565, 150, inputs[ "Z_Extended" ] )

        statusLight( zStatusCanvas, 1200, 275, inputs[ "Z_Fixed_Latched" ] )
        statusLight( zStatusCanvas, 1220, 203, inputs[ "Z_Fixed_Present" ] )

        var armBase = zArm / scale
        statusLight( zStatusCanvas, armBase + 765, 135, inputs[ "Latch_Actuator_Top" ] )
        statusLight( zStatusCanvas, armBase + 765, 155, inputs[ "Latch_Actuator_Mid" ] )
        statusLight( zStatusCanvas, armBase + 770, 235, inputs[ "Z_Stage_Present" ] )
        statusLight( zStatusCanvas, armBase + 780, 273, inputs[ "Z_Stage_Latched" ] )
        statusLight( zStatusCanvas, armBase + 767, 305, ( runStatus.states[ "plcState" ] == "Latching" ) )

        //
        // Draw movement history.
        //

        // If there is a new line segment, the current seek position will be
        // different from the last seek position.
        if ( ( lastX != motorX )
          || ( lastY != motorY ) )
        {
          var x =
            rescale( motorX, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, LINE_OFFSET_X )

          var y =
            rescale( motorY, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, LINE_OFFSET_Y )

          // Save this location.
          lines.push( [ x, y ] )

          // Get rid of the oldest line segments.
          while ( lines.length > ( LINES + 1 ) )
            lines.shift()

          var pathCanvas = document.getElementById( "pathCanvas" ).getContext( "2d" )

          // Clear canvas.
          pathCanvas.clearRect( 0, 0, baseGraphicWidth, baseGraphicHeight )

          // Draw the previous path.
          var previousX = null
          var previousY = null
          for ( var lineIndex in lines )
          {
            // Get finishing location for this line.
            var x = lines[ lineIndex ][ 0 ]
            var y = lines[ lineIndex ][ 1 ]

            // If this isn't the first point (we need two points to draw a line
            // segment)...
            if ( 0 != lineIndex )
            {
              // Start line segment.
              pathCanvas.beginPath()

              // Make the line.
              pathCanvas.moveTo( previousX, previousY )
              pathCanvas.lineTo( x, y )

              // Calculate the gradient alpha transparency for this line segment.
              var numberOfLines = lines.length - 1
              var alphaStart  = ( ( lineIndex - 1 ) / numberOfLines )
              var alphaFinish = ( lineIndex / numberOfLines )

              // Make a gradient color for this line segment.
              // Line color is black with the alpha transparency fading from
              // oldest segment (mostly transparent) to newest (no
              // transparency).
              var gradient = pathCanvas.createLinearGradient( previousX, previousY, x, y )
              gradient.addColorStop( 0, 'rgba( 139, 69, 19, ' + alphaStart + ' )' )
              gradient.addColorStop( 1, 'rgba( 139, 69, 19, ' + alphaFinish + ' )' )
              pathCanvas.lineWidth = 2
              pathCanvas.strokeStyle = gradient

              // Draw line segment.
              pathCanvas.stroke()
            }

            // Next starting location is the finishing location of the segment
            // just drawn.
            previousX = x
            previousY = y
          }

          // Update histories.
          startingX = lastX
          startingY = lastY
          lastX = motorX
          lastY = motorY
        }

        var seekCanvas = document.getElementById( "seekCanvas" ).getContext( "2d" )

        // If there is a starting point and X/Y is in motion.
        if ( ( null !== startingX )
          && ( null !== startingY )
          && ( ( motorStatus.motor[ "xMoving" ] )
            || ( motorStatus.motor[ "yMoving" ] ) ) )
        {
          // Clear canvas.
          seekCanvas.clearRect( 0, 0, baseGraphicWidth, baseGraphicHeight )

          seekCanvas.beginPath()

          var startX =
            rescale( startingX, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, LINE_OFFSET_X )

          var startY =
            rescale( startingY, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, LINE_OFFSET_Y )

          var endX =
            rescale( xPosition, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, LINE_OFFSET_X )

          var endY =
            rescale( yPosition, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, LINE_OFFSET_Y )

          seekCanvas.moveTo( startX, startY )
          seekCanvas.lineTo( endX, endY )

          seekCanvas.strokeStyle = "yellow"
          seekCanvas.lineWidth = 1
          seekCanvas.stroke()

          wasMoving = true
        }
        else
        if ( wasMoving )
        {
          seekCanvas.clearRect( 0, 0, baseGraphicWidth, baseGraphicHeight )
          wasMoving = false
        }

      } // function

    ) // winder.addPeriodicEndCallback

  } // setupCallback

  var isSetup = false
  var startSetup = function()
  {
    // Scaling can take place after machine calibration has been read.
    // So read the calibration and start the setup when we have this data.
    winder.remoteAction
    (
      "machineCalibration.__dict__",
      function( data )
      {
        if ( data )
        {
          machineCaliration = data
          setupCallback()
        }
      }
    )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Setup periodic callback that will reposition images.  Don't call until
  //   page is fully loaded.
  //-----------------------------------------------------------------------------
  this.initialize = function( scaleParameter )
  {
    if ( scaleParameter )
      scale = scaleParameter
    else
      scale = DEFAULT_SCALE

    if ( winder )
      startSetup()
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Setup images to use scale factor.
  //-----------------------------------------------------------------------------
  var rescale = function()
  {
    var width = $( this ).width() * scale
    $( this ).width( width )

    var ITEMS = [ "margin-left", "margin-top", "top" ]
    for ( index in ITEMS )
    {
      var item = ITEMS[ index ]

      var newSize = $( this ).css( item )
      var raw = newSize
      if ( newSize )
      {
        newSize  = newSize.replace( "px", "" )
        if ( $.isNumeric( newSize ) )
        {
          newSize  = parseFloat( newSize )
          newSize *= scale

          $( this ).css( item, newSize )
        }
      }
    }
    $( this ).css( "display", "inline" )
  }

  modules.load
  (
    [ "/Scripts/Winder", "/Desktop/Modules/MotorStatus", "/Desktop/Modules/RunStatus" ],
    function()
    {
      winder = modules.get( "Winder" )
      motorStatus = modules.get( "MotorStatus" )
      runStatus = modules.get( "RunStatus" )

      //
      // Load images for X/Y.
      //

      $( "<img />" )
        .attr( "src", "Images/Base.png" )
        .attr( "id", "baseImage" )
        .attr( "alt", "Front view" )
        .load( rescale )
        .appendTo( "#sideGraphic" )

      $( "<canvas />" )
        .attr( "id", "pathCanvas" )
        .addClass( "pathCanvas" )
        .appendTo( "#sideGraphic" )

      $( "<canvas />" )
        .attr( "id", "seekCanvas" )
        .addClass( "seekCanvas" )
        .appendTo( "#sideGraphic" )

      $( "<img />" )
        .attr( "src", "Images/Loop.png" )
        .attr( "id", "loopImage" )
        .attr( "alt", "Loop view" )
        .load( rescale )
        .appendTo( "#sideGraphic" )

      $( "<img />" )
        .attr( "src", "Images/Head.png" )
        .attr( "id", "headImage" )
        .attr( "alt", "Head view" )
        .load( rescale )
        .appendTo( "#sideGraphic" )

      //
      // Load images for Z.
      //

      $( "<img />" )
        .attr( "src", "Images/Z_Base.png" )
        .attr( "id", "zBaseImage" )
        .attr( "alt", "Z-Base view" )
        .load( rescale )
        .appendTo( "#zGraphic" )

      $( "<img />" )
        .attr( "src", "Images/Z_Head.png" )
        .attr( "id", "zHeadImage" )
        .attr( "alt", "Z-Head view" )
        .load( rescale )
        .appendTo( "#zGraphic" )

      $( "<img />" )
        .attr( "src", "Images/Z_Arm.png" )
        .attr( "id", "zArmImage" )
        .attr( "alt", "Z-Arm view" )
        .load( rescale )
        .appendTo( "#zGraphic" )

      $( "<canvas />" )
        .attr( "id", "zStatusCanvas" )
        .addClass( "zStatusCanvas" )
        .appendTo( "#zGraphic" )

      var zStatusCanvas = document.getElementById( "zStatusCanvas" ).getContext( "2d" )

      // Scaling can take place after machine calibration has been read.
      // So read the calibration and start the setup when we have this data.
      winder.addPeriodicCallback
      (
        "LowLevelIO.getInputs()",
        function( data )
        {
          if ( data )
          {
            inputs = {}
            for ( var input of data )
              inputs[ input[ 0 ] ] = input[ 1 ]
          }
        }
      )

      winder.addPeriodicRead
      (
        "process.getHeadAngle()",
        readData,
        "headAngle"
      )

      winder.addErrorCallback
      (
        function()
        {
          for ( var index in IMAGES_TO_HIDE )
          {
            var image = IMAGES_TO_HIDE[ index ]
            $( image ).css( "display", "none" )
          }

          for ( var index in IMAGES_TO_BLUR )
          {
            var image = IMAGES_TO_BLUR[ index ]
            $( image )
              .css( "opacity", "0.75" )
              .css( "filter", "blur( 10px )" )
          }
        }
      )

      winder.addErrorClearCallback
      (
        function()
        {
          for ( var index in IMAGES_TO_HIDE )
          {
            var image = IMAGES_TO_HIDE[ index ]
            $( image )
              .css( "display", "inline" )
          }

          for ( var index in IMAGES_TO_BLUR )
          {
            var image = IMAGES_TO_BLUR[ index ]
            $( image )
              .css( "opacity", "1.0" )
              .css( "filter", "" )
          }
        }
      )

      if ( scale )
        startSetup()

    }
  )
} // PositionGraphic
