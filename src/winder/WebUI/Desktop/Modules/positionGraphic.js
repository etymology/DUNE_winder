function PositionGraphic()
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
  var MIN_X          = 95
  var MAX_X          = 1065
  var MIN_Y          = 387
  var MAX_Y          = 32
  var HEAD_X_OFFSET  = 100
  var MIN_ARM_Z      = 0
  var MAX_ARM_Z      = 281
  var MIN_HEAD_Z     = 783
  var MAX_HEAD_Z     = 1064
  var LINE_OFFSET_X  = 129
  var LINE_OFFSET_Y  = 30

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

  var lastX = null
  var lastY = null
  var startingX = null
  var startingY = null
  var lines = []

  var machineCaliration

  var setupCallback = function()
  {
    var baseGraphicWidth  = BASE_GRAPHIC_X * scale
    var baseGraphicHeight = BASE_GRAPHIC_Y * scale

    // Scale limits of image.
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

    $( "#baseCanvas" )
      .attr( "width",  baseGraphicWidth  + "px" )
      .attr( "height", baseGraphicHeight + "px"  )

    // Image position
    winder.addPeriodicEndCallback
    (
      function()
      {
        // Motor position history.
        debounceLastX = debounceX
        debounceLastY = debounceY
        debounceX = motorStatus.motor[ "xDesiredPosition" ]
        debounceY = motorStatus.motor[ "yDesiredPosition" ]

        // Debounce motor positions.
        // This is done because the X and Y destinations change asynchronously.
        // To ensure they stay in step, they both must match their previous
        // value twice in a row.
        if ( ( debounceLastX == debounceX )
          || ( debounceLastY == debounceY ) )
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

        // Limits of travel (in mm).
        var MIN_X_POSITION = machineCaliration[ "limitLeft" ]
        var MAX_X_POSITION = machineCaliration[ "limitRight" ]
        var MIN_Y_POSITION = machineCaliration[ "limitBottom" ]
        var MAX_Y_POSITION = machineCaliration[ "limitTop" ]
        var MIN_Z_POSITION = machineCaliration[ "zFront" ]
        var MAX_Z_POSITION = machineCaliration[ "zBack" ]

        var xPosition = motorStatus.motor[ "xPosition" ]
        var yPosition = motorStatus.motor[ "yPosition" ]
        var zPosition = motorStatus.motor[ "zPosition" ]

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
        var z = rescale( zPosition, MIN_HEAD_Z, MAX_HEAD_Z, MIN_Z_POSITION, MAX_Z_POSITION, 0 )

        if ( 0 != motorStatus.motor[ "headSide" ] )
          z = MAX_HEAD_Z

        $( "#zHeadImage" )
          .css( "left", z + "px" )

        //
        // Position arm (Z image).
        //
        var z = rescale( zPosition, MIN_ARM_Z, MAX_ARM_Z, MIN_Z_POSITION, MAX_Z_POSITION, 0 )

        $( "#zArmImage" )
          .css( "left", z + "px" )

        //
        // Draw movement history.
        //

        // Get the canvas and clear it.
        var canvas = document.getElementById( "baseCanvas" ).getContext( "2d" )
        canvas.clearRect( 0, 0, baseGraphicWidth, baseGraphicHeight )

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

          // Update histories.
          startingX = lastX
          startingY = lastY
          lastX = motorX
          lastY = motorY
        }

        // If there is a history to draw...
        if ( ( null !== lastX )
          && ( null !== lastY ) )
        {
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
              canvas.beginPath()

              // Make the line.
              canvas.moveTo( previousX, previousY )
              canvas.lineTo( x, y )

              // Calculate the gradient alpha transparency for this line segment.
              var numberOfLines = lines.length - 1
              var alphaStart  = ( ( lineIndex - 1 ) / numberOfLines )
              var alphaFinish = ( lineIndex / numberOfLines )

              // Make a gradient color for this line segment.
              // Line color is black with the alpha transparency fading from
              // oldest segment (mostly transparent) to newest (no
              // transparency).
              var gradient = canvas.createLinearGradient( previousX, previousY, x, y )
              gradient.addColorStop( 0, 'rgba( 0, 0, 0, ' + alphaStart + ' )' )
              gradient.addColorStop( 1, 'rgba( 0, 0, 0, ' + alphaFinish + ' )' )
              canvas.strokeStyle = gradient

              // Draw line segment.
              canvas.stroke()
            }

            // Next starting location is the finishing location of the segment
            // just drawn.
            previousX = x
            previousY = y
          }
        }

        // If there is a starting point and X/Y is in motion.
        if ( ( null !== startingX )
          && ( null !== startingY )
          && ( ( motorStatus.motor[ "xMoving" ] )
            || ( motorStatus.motor[ "yMoving" ] ) ) )
        {
          canvas.beginPath()

          var startX =
            rescale( startingX, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, LINE_OFFSET_X )

          var startY =
            rescale( startingY, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, LINE_OFFSET_Y )

          var endX =
            rescale( xPosition, MIN_X, MAX_X, MIN_X_POSITION, MAX_X_POSITION, LINE_OFFSET_X )

          var endY =
            rescale( yPosition, MIN_Y, MAX_Y, MIN_Y_POSITION, MAX_Y_POSITION, LINE_OFFSET_Y )

          canvas.moveTo( startX, startY )
          canvas.lineTo( endX, endY )

          canvas.strokeStyle = "brown"
          canvas.stroke()
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

    // Scaling can take place after machine calibration has been read.
    // So read the calibration and start the setup when we have this data.
    winder.remoteAction
    (
      "machineCalibration.__dict__",
      function( data )
      {
        machineCaliration = data
        setupCallback()
      }
    )

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

  //
  // Load all images.
  //

  $( "<img />" )
    .attr( "src", "Images/Base.png" )
    .attr( "id", "baseImage" )
    .attr( "alt", "Front view" )
    .load( rescale )
    .appendTo( "#sideGraphic" )

  $( "<canvas />" )
    .attr( "id", "baseCanvas" )
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

}

var positionGraphic = new PositionGraphic()
