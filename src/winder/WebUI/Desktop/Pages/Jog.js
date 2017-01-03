function Jog( modules )
{
  var self = this
  var winder = modules.get( "Winder" )
  var page = modules.get( "Page" )
  var motorStatus
  modules.load
  (
    "/Desktop/Modules/MotorStatus",
    function()
    {
      motorStatus = modules.get( "MotorStatus" )
    }
  )

  var MIN_VELOCITY = 1.0
  var maxVelocity

  var MIN_ACCELERATION = 1.0
  var maxAcceleration = 200
  var maxDeceleration = 50

  var lastAcceleration
  var lastDeceleration

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for reset button.
  //-----------------------------------------------------------------------------
  this.reset = function()
  {
    winder.remoteAction( 'process.acknowledgeError()' )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for servo disable button.
  //-----------------------------------------------------------------------------
  this.servoDisable = function()
  {
    winder.remoteAction( 'process.servoDisable()' )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Get the desired velocity.
  //-----------------------------------------------------------------------------
  this.getVelocity = function()
  {
    return document.getElementById( "velocitySlider" ).scaledValue()
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Get the desired positive acceleration.
  //-----------------------------------------------------------------------------
  this.getAcceleration = function()
  {
    return document.getElementById( "accelerationSlider" ).scaledValue()
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Get the desired negative acceleration.
  //-----------------------------------------------------------------------------
  this.getDeceleration = function()
  {
    return document.getElementById( "decelerationSlider" ).scaledValue()
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to start X/Y axis jog.
  // Input:
  //   x - Direction (1,-1, 0) for x-axis.
  //   y - Direction (1,-1, 0) for y-axis.
  //-----------------------------------------------------------------------------
  this.jogXY_Start = function( x, y )
  {
    // Convert direction to velocity.
    var velocity = this.getVelocity()
    x *= velocity
    y *= velocity

    // When both velocities are the same, calculate the maximum linear velocity
    // and use that.
    if ( ( 0 != x )
      && ( 0 != y )
      && ( Math.abs( x ) == Math.abs( y ) ) )
    {
      velocity = Math.sqrt( x * x / 2.0 )

      if ( x < 0 )
        x = -velocity
      else
        x = velocity

      if ( y < 0 )
        y = -velocity
      else
        y = velocity
    }

    var acceleration = this.getAcceleration()
    var deceleration = this.getDeceleration()

    winder.remoteAction
    (
      "process.jogXY(" + x + "," + y + "," + acceleration + "," + deceleration + ")"
    )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to stop X/Y jogging.
  //-----------------------------------------------------------------------------
  this.jogXY_Stop = function()
  {
    winder.remoteAction( "process.jogXY( 0, 0 )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to start X/Y axis seek.
  //-----------------------------------------------------------------------------
  this.seekXY = function( x, y )
  {
    if ( null == x )
      x = $( "#seekX" ).val()

    if ( null == y )
      y = $( "#seekY" ).val()

    var velocity = this.getVelocity()
    var acceleration = this.getAcceleration()
    var deceleration = this.getDeceleration()
    winder.remoteAction
    (
      "process.manualSeekXY("
      + x + ","
      + y + ","
      + velocity + ","
      + acceleration + ","
      + deceleration + ")"
    )
  }

  // $$$DEBUG
  this.seekXY_Set = function( setName )
  {
    var x = $( "#seekX_" + setName ).val()
    var y = $( "#seekY_" + setName ).val()
    this.seekXY( x, y )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Seek a point in machine geometry.
  // Input:
  //   x - Name of geometry variable that defines x position.
  //   y - Name of geometry variable that defines y position.
  //-----------------------------------------------------------------------------
  this.seekLocation = function( x, y )
  {
    var velocity = this.getVelocity()

    if ( x )
      x = "process.apa._gCodeHandler." + x
    else
      x = "None"

    if ( y )
      y = "process.apa._gCodeHandler." + y
    else
      y = "None"

    winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + "," + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to start Z axis seek.
  //-----------------------------------------------------------------------------
  this.seekZ = function( position )
  {
    var z = position
    if ( null == z )
      z = $( "#seekZ" ).val()

    var velocity = this.getVelocity()
    winder.remoteAction( "process.manualSeekZ(" + z + "," + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to stop Z axis jogging.
  //-----------------------------------------------------------------------------
  this.jogZ_Stop = function()
  {
    winder.remoteAction( "process.jogZ( 0 )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to start Z axis jogging.
  // Input:
  //   direction - Direction (1,-1, 0) of jog.
  //-----------------------------------------------------------------------------
  this.jogZ_Start = function( direction )
  {
    var velocity = this.getVelocity() * direction
    winder.remoteAction( "process.jogZ(" + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Fully retract Z axis.
  //-----------------------------------------------------------------------------
  this.zRetract = function()
  {
    var velocity = this.getVelocity()
    winder.remoteAction( "process.manualSeekZ( 0, " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Fully extend Z axis.
  //-----------------------------------------------------------------------------
  this.zExtend = function()
  {
    var velocity = this.getVelocity()
    var position = $( "#extendedPosition" ).val()
    winder.remoteAction( "process.manualSeekZ( " + position + ", " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Partly extend Z axis.
  //-----------------------------------------------------------------------------
  this.zMid = function()
  {
    var velocity = this.getVelocity()
    var position = $( "#extendedPosition" ).val() / 2
    winder.remoteAction( "process.manualSeekZ( " + position + ", " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Run a latching operation.
  //-----------------------------------------------------------------------------
  this.latch = function()
  {
    winder.remoteAction( "io.plcLogic.latch()" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Switch to latch homing sequence.
  //-----------------------------------------------------------------------------
  this.latchHome = function()
  {
    winder.remoteAction( "io.plcLogic.latchHome()" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Switch to latch unlock.
  //-----------------------------------------------------------------------------
  this.latchUnlock = function()
  {
    winder.remoteAction( "io.plcLogic.latchUnlock()" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Set the position of the head.
  //-----------------------------------------------------------------------------
  this.headPosition = function( position )
  {
    var velocity = this.getVelocity()
    winder.remoteAction( "process.manualHeadPosition( " + position + "," + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to seek to specified pin.
  //-----------------------------------------------------------------------------
  this.seekPin = function()
  {
    var pin = $( "#seekPin" ).val().toUpperCase()
    var velocity = this.getVelocity()
    winder.remoteAction( "process.seekPin( '" + pin + "', " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to set the anchor point.
  //-----------------------------------------------------------------------------
  this.setAnchor = function()
  {
    var pin = $( "#anchorPin" ).val().toUpperCase()

    var parameters = '"' + pin + '"'
    if ( pin.indexOf( "," ) >= 0 )
    {
      var pins = pin.split( "," )
      parameters = '"' + pins[ 0 ] + '", "' + pins[ 1 ] + '"'
    }

    winder.remoteAction( 'process.setAnchorPoint( ' + parameters + ' )' )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to set the anchor point.
  //-----------------------------------------------------------------------------
  this.executeGCode = function()
  {
    $( "#gExecutionCodeStatus" ).html( "Request G-Code execution..." )

    var gCode = $( "#manualGCode" ).val()
    winder.remoteAction
    (
      'process.executeG_CodeLine( "' + gCode + '" )',
      function( data )
      {
        if ( ! data )
          $( "#gExecutionCodeStatus" ).html( "Executed with no errors." )
        else
          $( "#gExecutionCodeStatus" ).html( "Error interpreting line: " + data )
      }
    )
  }

  page.loadSubPage
  (
    "/Desktop/Modules/PositionGraphic",
    "#positionGraphicDiv",
    function()
    {
      var positionGraphic = modules.get( "PositionGraphic" )
      positionGraphic.initialize( 0.7, motorStatus )
    }
  )

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

  // Incremental jog.
  page.loadSubPage
  (
    "/Desktop/Modules/IncrementalJog",
    "#smallMotionsDiv",
    function()
    {
      var incrementalJog = modules.get( "IncrementalJog" )
      incrementalJog.velocityCallback( self.getVelocity )
    }
  )

  // Fetch fully extended position from machine calibration.
  winder.remoteAction
  (
    "machineCalibration.zBack",
    function( data )
    {
      $( "#extendedPosition" ).val( data )
    }
  )

  var sliderValues =
  {
   "velocitySlider"     : 100,
   "accelerationSlider" : 100,
   "decelerationSlider" : 100
  }

  var createSlider = function( query, sliderTag, valueTag, valueUnits, minimum )
  {
    // Maximum velocity.
    winder.remoteAction
    (
      query,
      function( data )
      {
        var maximum = parseFloat( data )

        // Callback when slider is changed.
        sliderFunction =
          function( event, ui )
          {
            sliderValues[ sliderTag ] = ui.value
            var value = ui.value / 100.0 * ( maximum - minimum ) + minimum
            value = Math.round( value * 10.0 ) / 10.0
            $( "#" + valueTag ).html( value + " " + valueUnits )
          }

        ui = new function() { this.value = sliderValues[ sliderTag ] }
        sliderFunction( null, ui )

        // Function to get the scaled value of slider.
        document.getElementById( sliderTag ).scaledValue =
            function()
            {
              // Start with the level of the velocity slider.
              var value = parseFloat( $( this ).slider( "value" )  )

              // Correctly scale the velocity.
              value /= 100.0
              value *= ( maximum - minimum )
              value += minimum

              return value
            }

        $( "#" + sliderTag )
          .slider
          (
            {
              min: 0,
              max: 100,
              value: sliderValues[ sliderTag ],
              change: sliderFunction,
              slide: sliderFunction
            }
          )

      }
    )

  }

  var createSliders = function()
  {
    createSlider
    (
      'process.maxVelocity()',
      "velocitySlider",
      "velocityValue",
      "mm/s",
      MIN_VELOCITY
    )

    createSlider
    (
      'io.plcLogic.maxAcceleration()',
      "accelerationSlider",
      "accelerationValue",
      "mm/s<sup>2</sup>",
      MIN_ACCELERATION
    )

    createSlider
    (
      'io.plcLogic.maxDeceleration()',
      "decelerationSlider",
      "decelerationValue",
      "mm/s<sup>2</sup>",
      MIN_ACCELERATION
    )
  }

  createSliders()
  winder.addErrorClearCallback( createSliders )


  // // Maximum velocity.
  // winder.remoteAction
  // (
  //   'configuration.get( "maxAcceleration" )',
  //   function( data )
  //   {
  //     maxAcceleration = parseFloat( data )
  //
  //     // Callback when slider is changed.
  //     sliderFunction =
  //       function( event, ui )
  //       {
  //         var velocity = ui.value / 100.0 * ( maxAcceleration - MIN_ACCELERATION ) + MIN_ACCELERATION
  //         var value = Math.round( velocity * 10.0 ) / 10.0
  //         $( "#accelerationValue" ).html( value + " mm/s<sup>2</sup>" )
  //       }
  //
  //     ui = new function() { this.value = 100 }
  //     sliderFunction( null, ui )
  //
  //     // Setup slider.
  //     $( "#accelerationSlider" )
  //       .slider
  //       (
  //         {
  //           min: 0,
  //           max: 100,
  //           value: 100,
  //           change: sliderFunction,
  //           slide: sliderFunction
  //         }
  //       )
  //
  //   }
  // )
  //
  // // Maximum velocity.
  // winder.remoteAction
  // (
  //   'configuration.get( "maxDeceleration" )',
  //   function( data )
  //   {
  //     maxDeceleration = parseFloat( data )
  //
  //     // Callback when slider is changed.
  //     sliderFunction =
  //       function( event, ui )
  //       {
  //         var velocity = ui.value / 100.0 * ( maxDeceleration - MIN_ACCELERATION ) + MIN_ACCELERATION
  //         var value = Math.round( velocity * 10.0 ) / 10.0
  //         $( "#decelerationValue" ).html( value + " mm/s<sup>2</sup>" )
  //       }
  //
  //     ui = new function() { this.value = 100 }
  //     sliderFunction( null, ui )
  //
  //     // Setup slider.
  //     $( "#decelerationSlider" )
  //       .slider
  //       (
  //         {
  //           min: 0,
  //           max: 100,
  //           value: 100,
  //           change: sliderFunction,
  //           slide: sliderFunction
  //         }
  //       )
  //
  //   }
  // )
  //
  // // Maximum velocity.
  // winder.remoteAction
  // (
  //   'process.maxVelocity()',
  //   function( data )
  //   {
  //     maxVelocity = parseFloat( data )
  //
  //     // Callback when slider is changed.
  //     sliderFunction =
  //       function( event, ui )
  //       {
  //         var velocity = ui.value / 100.0 * ( maxVelocity - MIN_VELOCITY ) + MIN_VELOCITY
  //         var value = Math.round( velocity * 10.0 ) / 10.0
  //         $( "#velocityValue" ).html( value + " mm/s" )
  //       }
  //
  //     ui = new function() { this.value = 100 }
  //     sliderFunction( null, ui )
  //
  //     // Setup slider.
  //     $( "#velocitySlider" )
  //       .slider
  //       (
  //         {
  //           min: 0,
  //           max: 100,
  //           value: 100,
  //           change: sliderFunction,
  //           slide: sliderFunction
  //         }
  //       )
  //   }
  // )

  window[ "jog" ] = this
}
