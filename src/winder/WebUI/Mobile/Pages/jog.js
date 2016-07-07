function Jog()
{
  var self = this

  var MIN_VELOCITY = 1.0
  var maxVelocity

  var MIN_ACCELERATION = 1.0
  var maxAcceleration = 200
  var maxDeceleration = 50

  var lastAcceleration
  var lastDeceleration
  var extendedPosition

  //-----------------------------------------------------------------------------
  // $$$DEBUG
  //-----------------------------------------------------------------------------
  this.scaleBar = function( tag, maximum, minimum )
  {
    // Start with the level of the velocity slider.
    var value = parseFloat( $( "#" + tag ).slider( "value" )  )

    // Correctly scale the velocity.
    value /= 100.0
    value *= ( maximum - minimum )
    value += minimum

    return value
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Get the desired velocity.
  //-----------------------------------------------------------------------------
  this.getVelocity = function()
  {
    return maxVelocity
    //this.scaleBar( "velocitySlider", maxVelocity, MIN_VELOCITY )
  }

  //-----------------------------------------------------------------------------
  // $$$DEBUG
  //-----------------------------------------------------------------------------
  this.getAcceleration = function()
  {
    return maxAcceleration
    //this.scaleBar( "accelerationSlider", maxAcceleration, MIN_ACCELERATION )
  }

  //-----------------------------------------------------------------------------
  // $$$DEBUG
  //-----------------------------------------------------------------------------
  this.getDeceleration = function()
  {
    return maxDeceleration
    //this.scaleBar( "decelerationSlider", maxDeceleration, MIN_ACCELERATION )
  }

  // //-----------------------------------------------------------------------------
  // // $$$DEBUG
  // //-----------------------------------------------------------------------------
  // this.updateAcceleration = function()
  // {
  //   var acceleration = parseFloat( $( "#accelerationSlider" ).slider( "value" )  )
  //
  //   // Correctly scale the acceleration.
  //   acceleration /= 100.0
  //   acceleration *= ( maxAcceleration - MIN_ACCELERATION )
  //   acceleration += MIN_ACCELERATION
  //
  //   if ( acceleration != lastAcceleration )
  //   {
  //     lastAcceleration = acceleration
  //   }
  //
  //   var deceleration = parseFloat( $( "#decelerationSlider" ).slider( "value" )  )
  //
  //   // Correctly scale the acceleration.
  //   deceleration /= 100.0
  //   deceleration *= ( maxDeceleration - MIN_ACCELERATION )
  //   deceleration += MIN_ACCELERATION
  //
  //   if ( deceleration != lastDeceleration )
  //   {
  //     lastDeceleration = deceleration
  //   }
  // }

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
    var velocity = this.getVelocity() * 0.1
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
    var velocity = this.getVelocity() * direction * 0.01
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
    winder.remoteAction( "process.manualSeekZ( " + extendedPosition + ", " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Partly extend Z axis.
  //-----------------------------------------------------------------------------
  this.zMid = function()
  {
    var velocity = this.getVelocity()
    var position = extendedPosition / 2
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
  //-----------------------------------------------------------------------------
  this.seekPin = function()
  {
    var pin = $( "#seekPin" ).val().toUpperCase()
    var velocity = this.getVelocity()
    winder.remoteAction( "process.seekPin( '" + pin + "', " + velocity + " )" )
  }

  // Fetch fully extended position from machine calibration.
  winder.remoteAction
  (
    "machineCalibration.zBack",
    function( data )
    {
      extendedPosition = data
    }
  )




  // Maximum velocity.
  winder.remoteAction
  (
    'configuration.get( "maxAcceleration" )',
    function( data )
    {
      maxAcceleration = parseFloat( data )
    }
  )

  // Maximum velocity.
  winder.remoteAction
  (
    'configuration.get( "maxDeceleration" )',
    function( data )
    {
      maxDeceleration = parseFloat( data )
    }
  )

  // Maximum velocity.
  winder.remoteAction
  (
    'configuration.get( "maxVelocity" )',
    function( data )
    {
      maxVelocity = parseFloat( data )
    }
  )





    //
    // Bind the touch start/end events for each jog button.
    // (This cannot be done via HTML.)
    //

    $( "#jogXY_ul" )
      .bind( 'touchstart', function() { self.jogXY_Start( -1, +1 ) } )
      .bind( 'touchend', self.jogXY_Stop )

    $( "#jogXY_u" )
      .bind( 'touchstart', function() { self.jogXY_Start(  0, +1 ) } )
      .bind( 'touchend', self.jogXY_Stop )

    $( "#jogXY_ur" )
      .bind( 'touchstart', function() { self.jogXY_Start( +1, +1 ) } )
      .bind( 'touchend', self.jogXY_Stop )


    $( "#jogXY_l" )
      .bind( 'touchstart', function() { self.jogXY_Start( -1,  0 ) } )
      .bind( 'touchend', self.jogXY_Stop )

    $( "#jogXY_r" )
      .bind( 'touchstart', function() { self.jogXY_Start( +1,  0 ) } )
      .bind( 'touchend', self.jogXY_Stop )


    $( "#jogXY_dl" )
      .bind( 'touchstart', function() { self.jogXY_Start( -1, -1 ) } )
      .bind( 'touchend', self.jogXY_Stop )

    $( "#jogXY_d" )
      .bind( 'touchstart', function() { self.jogXY_Start(  0, -1 ) } )
      .bind( 'touchend', self.jogXY_Stop )

    $( "#jogXY_dr" )
      .bind( 'touchstart', function() { self.jogXY_Start( +1, -1 ) } )
      .bind( 'touchend', self.jogXY_Stop )


    $( "#jogZ_b" )
      .bind( 'touchstart', function() { self.jogZ_Start( -1 ) } )
      .bind( 'touchend', self.jogZ_Stop )

    $( "#jogZ_f" )
      .bind( 'touchstart', function() { self.jogZ_Start( +1 ) } )
      .bind( 'touchend', self.jogZ_Stop )


}

//-----------------------------------------------------------------------------
// Uses:
//   Call when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    jog = new Jog()
  }
);
