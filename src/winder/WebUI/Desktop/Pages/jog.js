function Jog()
{
  var MIN_VELOCITY = 1.0
  var maxVelocity

  //-----------------------------------------------------------------------------
  // Uses:
  //   Get the desired velocity.
  //-----------------------------------------------------------------------------
  this.getVelocity = function()
  {
    // Start with the level of the velocity slider.
    var velocity = parseFloat( $( "#velocitySlider" ).slider( "value" )  )

    // Correctly scale the velocity.
    velocity /= 100.0
    velocity *= ( maxVelocity - MIN_VELOCITY )
    velocity += MIN_VELOCITY

    return velocity
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

    winder.remoteAction( "process.jogXY(" + x + "," + y + ")" )
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
    winder.remoteAction( "process.manualSeekXY(" + x + "," + y + "," + velocity + ")"  )
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
  this.seekZ = function()
  {
    var z = $( "#seekZ" ).val()
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
    var velocity = $( "#velocitySlider" ).slider( "value" ) * direction
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

  // Callback function to initialize position graphic.
  // Called twice--once when the position graphic page is loaded, and again
  // when the motor status page is loaded.  Both must be loaded before
  // initialization can take place, and either could load first.
  var positionGraphicCount = 2
  positionGraphicInitialize = function()
  {
    positionGraphicCount -= 1
    if ( 0 == positionGraphicCount )
      positionGraphic.initialize( 0.7 )
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

  // Fetch fully extended position from machine calibration.
  winder.remoteAction
  (
    "machineCalibration.zBack",
    function( data )
    {
      $( "#extendedPosition" ).val( data )
    }
  )

  // Maximum velocity.
  winder.remoteAction
  (
    'configuration.get( "maxVelocity" )',
    function( data )
    {
      maxVelocity = parseFloat( data )

      // Callback when slider is changed.
      sliderFunction =
        function( event, ui )
        {
          var velocity = ui.value / 100.0 * ( maxVelocity - MIN_VELOCITY ) + MIN_VELOCITY
          var value = Math.round( velocity * 10.0 ) / 10.0
          $( "#velocityValue" ).html( value + " mm/s" )
        }

      // Run slider callback with initial value.
      ui = new function() { this.value = 100 }
      sliderFunction( null, ui )

      // Setup slider.
      $( "#velocitySlider" )
        .slider
        (
          {
            min: 0,
            max: 100,
            value: 100,
            change: sliderFunction,
            slide: sliderFunction
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
    jog = new Jog()
  }
);
