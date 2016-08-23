function Increment()
{
  var self = this

  // Public motor status data.
  this.motor = {}

  //-----------------------------------------------------------------------------
  // Uses:
  //   Read configuration variables related to motor limits. (Private)
  //-----------------------------------------------------------------------------
  var readConfig = function()
  {
    winder.remoteAction
    (
      'configuration.get( "maxAcceleration" )',
      function( data )
      {
        self.motor[ "maxAcceleration" ] = parseFloat( data )
      }
    )

    winder.remoteAction
    (
      'configuration.get( "maxDeceleration" )',
      function( data )
      {
        self.motor[ "maxDeceleration" ] = parseFloat( data )
      }
    )

    winder.remoteAction
    (
      'configuration.get( "maxVelocity" )',
      function( data )
      {
        self.motor[ "maxVelocity" ] = parseFloat( data )
      }
    )
  }

  //-----------------------------------------------------------------------------
  // $$$DEBUG
  //-----------------------------------------------------------------------------
  this.seekPin = function()
  {
    var pin = $( "#seekPin" ).val().toUpperCase()
    var velocity = this.motor[ "maxVelocity" ]
    winder.remoteAction( "process.seekPin( '" + pin + "', " + velocity + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   $$$DEBUG
  //-----------------------------------------------------------------------------
  this.moveX = function( offset )
  {
    var velocity = this.motor[ "maxVelocity" ]
    var x = this.motor[ "xPosition" ] + offset
    var y = "None"
    winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + "," + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   $$$DEBUG
  //-----------------------------------------------------------------------------
  this.moveY = function( offset )
  {
    var velocity = this.motor[ "maxVelocity" ]
    var x = "None"
    var y = this.motor[ "yPosition" ] + offset
    winder.remoteAction( "process.manualSeekXY( " + x + ", " + y + "," + velocity + ")"  )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Format a number with request number of decimal places.  (Private)
  // Input:
  //   data - Number to format.
  //   decimals - Number of decimal places.
  // Output:
  //   Number rounded to the requested decimal places.
  //-----------------------------------------------------------------------------
  var formatFunction = function( data, decimals )
  {
    if ( $.isNumeric( data ) )
    {

      var multiplier = Math.pow( 10, decimals )
      data = Math.round( data * multiplier ) / multiplier
    }
    else
      data = "-"

    return data
  }

  readConfig()
  var AXIES = [ "x", "y" ]
  for ( var index in AXIES )
  {
    var axis = AXIES[ index ]

    winder.addPeriodicDisplay
    (
      "io." + axis + "Axis.getPosition()",
      "#" + axis + "Position",
      this.motor,
      axis + "Position",
      formatFunction,
      1
    )

    winder.addPeriodicDisplay
    (
      "io." + axis + "Axis.getPosition()",
      "#" + axis + "Position",
      this.motor,
      axis + "Position",
      formatFunction,
      1
    )
  }
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
);
