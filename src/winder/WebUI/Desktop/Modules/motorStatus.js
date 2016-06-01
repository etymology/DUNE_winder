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
      "round( io." + axis + "Axis.getDesiredPosition(), 1 ) + 0",
      "#" + axis + "DesiredPosition",
      this.motor,
      axis + "DesiredPosition"
    )

    winder.addPeriodicRemoteDisplay
    (
      "round( io." + axis + "Axis.getPosition(), 1 ) + 0",
      "#" + axis + "Position",
      this.motor,
      axis + "Position"
    )

    winder.addPeriodicRemoteDisplay
    (
      "round( io." + axis + "Axis.getVelocity(), 2 ) + 0",
      "#" + axis + "Velocity",
      this.motor,
      axis + "Velocity"
    )

    winder.addPeriodicRemoteDisplay
    (
      "round( io." + axis + "Axis.getAcceleration(), 2 ) + 0",
      "#" + axis + "Acceleration",
      this.motor,
      axis + "Acceleration"
    )

    this.readConfig()
    winder.addErrorClearCallback( this.readConfig )

    let localAxis = axis
    winder.addPeriodicEndCallback
    (
      function()
      {
        var acceleration = self.motor[ localAxis + "Acceleration" ]
        var topAcceleration = self.motor[ "maxAcceleration" ]
        if ( acceleration < 0 )
          topAcceleration = -self.motor[ "maxAcceleration" ]

        var level = 0
        if ( topAcceleration != 0 )
          level = acceleration / topAcceleration

        level *= $( "#" + axis + "AccelerationBar" ).parent().width() + 10
        $( "#" + localAxis + "AccelerationBar" ).width( "" + Math.round( level ) + "px" )

        var desiredPosition = self.motor[ localAxis + "DesiredPosition" ]
        var position = self.motor[ localAxis + "Position" ]

        // $$$DEBUG - Put geometry readings in here.
        var top = 435
        if ( "x" == localAxis )
          top = 6500
        else
        if ( "y" == localAxis )
          top = 2800

        level = Math.abs( position / top )

        level *= $( "#" + localAxis + "PositionBar" ).parent().width() + 10
        $( "#" + localAxis + "PositionBar" ).width( "" + Math.round( level ) + "px" )

        var maxVelocity = self.motor[ "maxVelocity" ]
        var velocity = Math.abs( self.motor[ localAxis + "Velocity" ] )

        var level = 0
        if ( maxVelocity != 0 )
          level = velocity / maxVelocity

        level *= $( "#" + axis + "VelocityBar" ).parent().width() + 10
        $( "#" + localAxis + "VelocityBar" ).width( "" + Math.round( level ) + "px" )
      }
    )


  }

}

var motorStatus = new MotorStatus()
