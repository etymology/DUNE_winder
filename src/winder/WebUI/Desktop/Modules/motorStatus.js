function MotorStatus()
{
  // Pointer to self.
  self = this

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
  // Uses:
  //   Setup progress bars.  (Private)
  // Input:
  //   axis - The axis to setup.
  // Notes:
  //   Function exists to avoid needing 'let' operator.
  //-----------------------------------------------------------------------------
  var barSetup = function( axis )
  {
    winder.addPeriodicRemoteCallback
    (
      "io." + axis + "Axis.getSeekStartPosition()",
      function( value )
      {
        self.motor[ axis + "SeekStartPosition" ] = value
      }
    )

    winder.addPeriodicEndCallback
    (
      function()
      {
        var rawVelocity = self.motor[ axis + "Velocity" ]
        var acceleration = self.motor[ axis + "Acceleration" ]
        var topAcceleration = self.motor[ "maxAcceleration" ]
        var direction = ( acceleration < 0 ) ^ ( rawVelocity < 0 )
        if ( direction )
          topAcceleration = self.motor[ "maxDeceleration" ]

        topAcceleration *= Math.sign( acceleration )

        var level = 0
        if ( topAcceleration != 0 )
        {
          level = acceleration / topAcceleration
          level = Math.min( level, 1.0 )
        }

        level *= $( "#" + axis + "AccelerationBar" ).parent().width() + 10
        $( "#" + axis + "AccelerationBar" ).width( "" + Math.round( level ) + "px" )

        var desiredPosition = self.motor[ axis + "DesiredPosition" ]
        var position = self.motor[ axis + "Position" ]
        var startPosition = self.motor[ axis + "SeekStartPosition" ]

        level = Math.abs( position - startPosition ) / Math.abs( desiredPosition - startPosition )
        level = Math.min( level, 1.0 )

        level *= $( "#" + axis + "PositionBar" ).parent().width() + 10
        $( "#" + axis + "PositionBar" ).width( "" + Math.round( level ) + "px" )

        var maxVelocity = self.motor[ "maxVelocity" ]
        var velocity = Math.abs( self.motor[ axis + "Velocity" ] )

        var level = 0
        if ( maxVelocity != 0 )
        {
          level = velocity / maxVelocity
          level = Math.min( level, 1.0 )
        }

        level *= $( "#" + axis + "VelocityBar" ).parent().width() + 10
        $( "#" + axis + "VelocityBar" ).width( "" + Math.round( level ) + "px" )
      }
    )
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

  //-----------------------------------------------------------------------------
  // Constructor
  //-----------------------------------------------------------------------------

  var AXIES = [ "x", "y", "z" ]
  for ( var index in AXIES )
  {
    var axis = AXIES[ index ]
    winder.addPeriodicRemoteDisplay
    (
      "io." + axis + "Axis.isSeeking()",
      "#" + axis + "Moving",
      this.motor,
      axis + "Moving"
    )

    winder.addPeriodicRemoteDisplay
    (
      "io." + axis + "Axis.getDesiredPosition()",
      "#" + axis + "DesiredPosition",
      this.motor,
      axis + "DesiredPosition",
      formatFunction,
      1
    )

    winder.addPeriodicRemoteDisplay
    (
      "io." + axis + "Axis.getPosition()",
      "#" + axis + "Position",
      this.motor,
      axis + "Position",
      formatFunction,
      1
    )

    winder.addPeriodicRemoteDisplay
    (
      "io." + axis + "Axis.getVelocity()",
      "#" + axis + "Velocity",
      this.motor,
      axis + "Velocity",
      formatFunction,
      2
    )

    winder.addPeriodicRemoteDisplay
    (
      "io." + axis + "Axis.getAcceleration()",
      "#" + axis + "Acceleration",
      this.motor,
      axis + "Acceleration",
      formatFunction,
      2
    )

    readConfig()
    winder.addErrorClearCallback( this.readConfig )

    barSetup( axis )
  }

}

var motorStatus = new MotorStatus()
