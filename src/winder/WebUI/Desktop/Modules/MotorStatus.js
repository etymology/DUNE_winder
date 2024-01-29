function MotorStatus( modules )
{
  // Pointer to self.
  var self = this

  // Public motor status data.
  this.motor = {}

  var winder = modules.get( "Winder" )

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
    winder.addPeriodicCallback
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
        var isFunctional = self.motor[ axis + "Functional" ]
        var isMoving = self.motor[ axis + "Moving" ]
        var rawVelocity = self.motor[ axis + "Velocity" ]
        var acceleration = self.motor[ axis + "Acceleration" ]
        var topAcceleration = self.motor[ "maxAcceleration" ]
        var direction = ( acceleration < 0 ) ^ ( rawVelocity < 0 )
        if (direction) {
          topAcceleration = self.motor[ "maxDeceleration" ]
        }

        topAcceleration *= Math.sign( acceleration )

        if (! isFunctional) {
          $( "#" + axis + "Label" ).addClass( "inError" )
        } else {
                  $( "#" + axis + "Label" ).removeClass( "inError" )
                  if (isMoving) {
                    $( "#" + axis + "Label" ).addClass( "inMotion" )
                  } else {
                    $( "#" + axis + "Label" ).removeClass( "inMotion" )
                  }
                }

        var level = 0
        if ( topAcceleration != 0 )
        {
          level = acceleration / topAcceleration
          level = Math.min( level, 1.0 )
        }

        if (! isMoving) {
          level = 0
        }

        level *= $( "#" + axis + "AccelerationBar" ).parent().width() + 10
        $( "#" + axis + "AccelerationBar" ).width( "" + Math.round( level ) + "px" )

        var desiredPosition = self.motor[ axis + "DesiredPosition" ]
        var position = self.motor[ axis + "Position" ]
        var startPosition = self.motor[ axis + "SeekStartPosition" ]

        level = Math.abs( position - startPosition ) / Math.abs( desiredPosition - startPosition )
        level = Math.min( level, 1.0 )

        if (! isMoving) {
          level = 1
        }

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

        if (! isMoving) {
          level = 0
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
    if ($.isNumeric( data )) {
      var multiplier = Math.pow( 10, decimals )
      data = Math.round( data * multiplier ) / multiplier
    } else {
      data = "-"
    }

    return data
  }

  //-----------------------------------------------------------------------------
  // Constructor
  //-----------------------------------------------------------------------------

  winder.addPeriodicCallback
  (
    "[ io.Z_Stage_Present.get(), io.Z_Fixed_Present.get() ]",
    function( value )
    {
      var headPosition = 0
      if ( value )
      {
        if (value[ 0 ]) {
          headPosition += 1
        }

        if (value[ 1 ]) {
          headPosition += 2
        }
      }

      self.motor[ "headSide" ] = headPosition
    }
  )

  var AXIES = [ "x", "y", "z" ]
  for ( var index in AXIES )
  {
    var axis = AXIES[ index ]

    winder.addPeriodicRead
    (
      "io." + axis + "Axis.isFunctional()",
      this.motor,
      axis + "Functional"
    )

    winder.addPeriodicRead
    (
      "io." + axis + "Axis.isSeeking()",
      this.motor,
      axis + "Moving"
    )

    winder.addPeriodicDisplay
    (
      "io." + axis + "Axis.getDesiredPosition()",
      "#" + axis + "DesiredPosition",
      this.motor,
      axis + "DesiredPosition",
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

    winder.addPeriodicDisplay
    (
      "io." + axis + "Axis.getVelocity()",
      "#" + axis + "Velocity",
      this.motor,
      axis + "Velocity",
      formatFunction,
      2
    )

    winder.addPeriodicDisplay
    (
      "io." + axis + "Axis.getAcceleration()",
      "#" + axis + "Acceleration",
      this.motor,
      axis + "Acceleration",
      formatFunction,
      2
    )

    readConfig()
    winder.addErrorClearCallback( readConfig )

    barSetup( axis )
  }

}
