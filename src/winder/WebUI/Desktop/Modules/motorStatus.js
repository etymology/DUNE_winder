function MotorStatus()
{
  self = this
  this.motor = {}

  //-----------------------------------------------------------------------------
  // Uses:
  //   Read configuration variables related to motor limits.
  //-----------------------------------------------------------------------------
  this.readConfig = function()
  {
    winder.remoteAction
    (
      'float( configuration.get( "maxAcceleration" ) )',
      function( data )
      {
        self.motor[ "maxAcceleration" ] = data
      }
    )

    winder.remoteAction
    (
      'float( configuration.get( "maxDeceleration" ) )',
      function( data )
      {
        self.motor[ "maxDeceleration" ] = data
      }
    )

    winder.remoteAction
    (
      'float( configuration.get( "maxVelocity" ) )',
      function( data )
      {
        self.motor[ "maxVelocity" ] = data
      }
    )
  }

  var AXIES = [ "x", "y", "z" ]
  for ( var index in AXIES )
  {
    formatFunction = function( data, decimals )
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

    let localAxis = axis

    // $$$DEBUG
    winder.addPeriodicRemoteCallback
    (
      "io." + axis + "Axis.getSeekStartPosition()",
      function( value )
      {
        self.motor[ localAxis + "SeekStartPosition" ] = value
      }
    )

    this.readConfig()
    winder.addErrorClearCallback( this.readConfig )

    winder.addPeriodicEndCallback
    (
      function()
      {
        var rawVelocity = self.motor[ localAxis + "Velocity" ]
        var acceleration = self.motor[ localAxis + "Acceleration" ]
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
        $( "#" + localAxis + "AccelerationBar" ).width( "" + Math.round( level ) + "px" )

        var desiredPosition = self.motor[ localAxis + "DesiredPosition" ]
        var position = self.motor[ localAxis + "Position" ]
        var startPosition = self.motor[ localAxis + "SeekStartPosition" ]

        level = Math.abs( position - startPosition ) / Math.abs( desiredPosition - startPosition )
        level = Math.min( level, 1.0 )

        level *= $( "#" + localAxis + "PositionBar" ).parent().width() + 10
        $( "#" + localAxis + "PositionBar" ).width( "" + Math.round( level ) + "px" )

        var maxVelocity = self.motor[ "maxVelocity" ]
        var velocity = Math.abs( self.motor[ localAxis + "Velocity" ] )

        var level = 0
        if ( maxVelocity != 0 )
        {
          level = velocity / maxVelocity
          level = Math.min( level, 1.0 )
        }

        level *= $( "#" + axis + "VelocityBar" ).parent().width() + 10
        $( "#" + localAxis + "VelocityBar" ).width( "" + Math.round( level ) + "px" )
      }
    )


  }

}

var motorStatus = new MotorStatus()
