//-----------------------------------------------------------------------------
// Uses:
//   Callback to start X/Y axis jog.
// Input:
//   x - Direction (1,-1, 0) for x-axis.
//   y - Direction (1,-1, 0) for y-axis.
//-----------------------------------------------------------------------------
function jogXY_Start( x, y )
{
  // Convert direction to velocity.
  var velocity = $( "#velocitySlider" ).slider( "value" )
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
function jogXY_Stop()
{
  winder.remoteAction( "process.jogXY( 0, 0 )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback to start X/Y axis seek.
//-----------------------------------------------------------------------------
function seekXY( x, y )
{
  if ( null == x )
    x = $( "#seekX" ).val()

  if ( null == y )
    y = $( "#seekY" ).val()

  var velocity = $( "#velocitySlider" ).slider( "value" )
  winder.remoteAction( "process.manualSeekXY(" + x + "," + y + "," + velocity + ")"  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback to start Z axis seek.
//-----------------------------------------------------------------------------
function seekZ()
{
  var z = $( "#seekZ" ).val()
  var velocity = $( "#velocitySlider" ).slider( "value" )
  winder.remoteAction( "process.manualSeekZ(" + z + "," + velocity + ")"  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback to stop Z axis jogging.
//-----------------------------------------------------------------------------
function jogZ_Stop()
{
  winder.remoteAction( "process.jogZ( 0 )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback to start Z axis jogging.
// Input:
//   direction - Direction (1,-1, 0) of jog.
//-----------------------------------------------------------------------------
function jogZ_Start( direction )
{
  var velocity = $( "#velocitySlider" ).slider( "value" ) * direction
  winder.remoteAction( "process.jogZ(" + velocity + ")"  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Fully retract Z axis.
//-----------------------------------------------------------------------------
function zRetract()
{
  var velocity = $( "#velocitySlider" ).slider( "value" )
  winder.remoteAction( "process.manualSeekZ( 0, " + velocity + " )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Fully extend Z axis.
//-----------------------------------------------------------------------------
function zExtend()
{
  var velocity = $( "#velocitySlider" ).slider( "value" )
  var position = $( "#extendedPosition" ).val()
  winder.remoteAction( "process.manualSeekZ( " + position + ", " + velocity + " )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Run a latching operation.
//-----------------------------------------------------------------------------
function latch()
{
  winder.remoteAction.get( "io.plcLogic.latch()" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Switch to latch homing sequence.
//-----------------------------------------------------------------------------
function latchHome()
{
  winder.remoteAction.get( "io.plcLogic.latchHome()" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Switch to latch unlock.
//-----------------------------------------------------------------------------
function latchUnlock()
{
  winder.remoteAction.get( "io.plcLogic.latchUnlock()" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Call when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    winder.loadSubPage( "/Desktop/Modules/motorStatus", "#motorStatusDiv" )

    sliderFunction =
      function( event, ui )
      {
        $( "#velocityValue" )
          .html( $( "#velocitySlider" ).slider( "value" ) );
      }

    $( "#velocitySlider" )
      .slider
      (
        {
          min: 1,
          max: 500,
          value: 100,
          change: sliderFunction,
          slide: sliderFunction
        }
      )

    winder.periodicRemoteUpdate();
  }
);