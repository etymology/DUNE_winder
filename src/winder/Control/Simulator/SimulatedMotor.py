###############################################################################
# Name: SimulatedMotor.py
# Uses: Simulated PLC motor logic.
# Date: 2016-02-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Simulator.TrapezoidalMotion import TrapezoidalMotion

class SimulatedMotor :

  #---------------------------------------------------------------------
  def travelTime( self, velocity, acceleration, deceleration ) :
    """
    Compute travel time of the motion.

    Args:
      velocity: Maximum velocity.
      acceleration: Maximum positive acceleration.
      deceleration: Maximum negative acceleration.

    Returns:
      Time it will take to travel seek distance.
    """

    seekPosition = self._plc.getTag( self._desiredPositionTag )

    return TrapezoidalMotion.computeTravelTime(
      acceleration,
      deceleration,
      velocity,
      self._position,
      seekPosition
    )

  #---------------------------------------------------------------------
  def computeVelocity( self, acceleration, deceleration, desiredTime ) :
    """
    Compute travel time of the motion.

    Args:
      acceleration: Maximum positive acceleration.
      deceleration: Maximum negative acceleration.
      desiredTime: Time to traverse motion.

    Returns:
      Velocity to traverse the seek distance with the given time.
    """
    seekPosition = self._plc.getTag( self._desiredPositionTag )

    return TrapezoidalMotion.computeLimitingVelocity(
      acceleration,
      deceleration,
      self._position,
      seekPosition,
      desiredTime
    )

  #---------------------------------------------------------------------
  def startSeek( self, velocity, acceleration, deceleration ) :
    """
    Begin moving to a new position.

    Args:
      velocity: Maximum velocity for seek.
      acceleration: Maximum positive acceleration.
      deceleration: Maximum negative acceleration.
    """
    self._inMotion = True
    self._seekPosition = self._plc.getTag( self._desiredPositionTag )
    self._isSeek = True

    self._startTime = self._simulationTime.get()
    self._motion =                                          \
      TrapezoidalMotion                                     \
      (                                                     \
        acceleration,                                       \
        deceleration,                                       \
        velocity,                                           \
        self._position,                                     \
        self._seekPosition                                  \
      )

  #---------------------------------------------------------------------
  def startJog( self ) :
    """
    Start jogging.
    """
    self._startTime = self._simulationTime.get()
    velocity = self._plc.getTag( self._speedTag )
    if velocity != 0 :
      self._startPosition = self._position
      self._inMotion = True
      self._isJog = True

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop current motion.
    """
    self._inMotion = False
    self._velocity = 0
    self._acceleration = 0

  #---------------------------------------------------------------------
  def isInMotion( self ) :
    """
    See if motor is in motion.

    Returns:
      True if motor is in motion, False if not.
    """
    return self._inMotion

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update motion. Call after a change to simulation time.
    """
    delta = self._simulationTime.get() - self._startTime
    time = delta.total_seconds()

    saveMotion = self._inMotion
    if self._inMotion :
      if self._isSeek :
        self._inMotion     = self._motion.isMoving( time )
        self._position     = self._motion.interpolatePosition( time )
        self._velocity     = self._motion.interpolateVelocity( time )
        self._acceleration = self._motion.interpolateAcceleration( time )

      if self._isJog :
        self._velocity = self._plc.getTag( self._speedTag )
        direction = self._plc.getTag( self._directionTag )
        if 1 == direction :
          self._velocity = -self._velocity

        if 0 == self._velocity :
          self._inMotion = False
          self._isJog = False
        else:
          self._position = self._startPosition + time * self._velocity

    elif self._wasEnabled :
      if self._isSeek :
        self._motion.hardStop( time )
        self._position     = self._motion.interpolatePosition( time )
        self._velocity     = self._motion.interpolateVelocity( time )
        self._acceleration = self._motion.interpolateAcceleration( time )
        self._isSeek = False

    self._plc.write( self._motionTag, self._inMotion )
    self._plc.write( self._positionTag, self._position )
    self._plc.write( self._velocityTag, self._velocity )
    self._plc.write( self._accelerationTag, self._acceleration )

    self._wasEnabled = saveMotion


  #---------------------------------------------------------------------
  def __init__( self, plc, tagBase, simulationTime ) :
    """
    Constructor.
    """
    self._plc = plc
    self._simulationTime  = simulationTime

    self._startPosition   = 0
    self._startTime       = simulationTime.get()
    self._isSeek          = False
    self._isJog           = False
    self._simulationTime  = simulationTime
    self._wasEnabled      = False
    self._inMotion        = False
    self._seekPosition    = 0
    self._position        = 0
    self._velocity        = 0
    self._acceleration    = 0
    self._maxVelocity     = 0
    self._startTime       = simulationTime.get()
    self._motion          = None

    self._desiredPositionTag = plc.setupTag( tagBase + "_POSITION", 0                     )
    self._desiredVelocityTag = plc.setupTag( tagBase + "_Axis.CommandVelocity", 0         )
    self._speedTag           = plc.setupTag( tagBase + "_SPEED", 0                        )
    self._directionTag       = plc.setupTag( tagBase + "_DIR", 0                          )
    self._positionTag        = plc.setupTag( tagBase + "_Axis.ActualPosition", 0          )
    self._velocityTag        = plc.setupTag( tagBase + "_Axis.ActualVelocity", 0          )
    self._accelerationTag    = plc.setupTag( tagBase + "_Axis.CommandAcceleration", 0     )
    self._motionTag          = plc.setupTag( tagBase + "_Axis.CoordinatedMotionStatus", 0 )
    self._faultTag           = plc.setupTag( tagBase + "_Axis.ModuleFault", 0             )

  #---------------------------------------------------------------------
  def getSpeedTag( self ) :
    """
    Return the desired velocity tag.

    Returns:
      Desired velocity tag.
    """
    return self._plc.getTag( self._speedTag )
