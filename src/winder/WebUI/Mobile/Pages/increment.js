function Increment()
{
  var self = this

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to seek to specified pin.
  //-----------------------------------------------------------------------------
  this.seekPin = function()
  {
    var pin = $( "#seekPin" ).val().toUpperCase()
    var velocity = position.motor[ "maxVelocity" ]
    winder.remoteAction( "process.seekPin( '" + pin + "', " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Make an incremental move in X.
  // Input:
  //   offset - Value (+/-) to move.
  //-----------------------------------------------------------------------------
  this.moveX = function( offset )
  {
    var velocity = position.motor[ "maxVelocity" ]
    var x = position.motor[ "xPosition" ] + offset
    var y = "None"
    winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + "," + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Make an incremental move in Y.
  // Input:
  //   offset - Value (+/-) to move.
  //-----------------------------------------------------------------------------
  this.moveY = function( offset )
  {
    var velocity = position.motor[ "maxVelocity" ]
    var x = "None"
    var y = position.motor[ "yPosition" ] + offset
    winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + "," + velocity + ")"  )
  }

  winder.loadSubPage
  (
    "/Mobile/Modules/position",
    "#position"
  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Called when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    increment = new Increment()
  }
)
