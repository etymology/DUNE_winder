###############################################################################
# Name: SimulatedMotor.py
# Uses: Simulated PLC motor logic.
# Date: 2016-02-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
import random
from Simulator.TrapezoidalMotion import TrapezoidalMotion

class SimulatedMotor :

  # Standard deviation for position jitter.  Emulates servo error.
  # (Currently 0 because machine limits in rest of simulator don't like it).
  JITTER = 0.025

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
  def computeTimeLimited( self, acceleration, deceleration, maxVelocity, desiredTime ) :
    """
    Calculate a limiting velocity and accelerations that will result in the
    desired time as well as keep the same acceleration time.  Useful
    for synchronizing multi-axis motion.

    Args:
      acceleration: Maximum positive acceleration.
      deceleration: Maximum negative acceleration.
      maxVelocity: Maximum velocity.
      desiredTime: Amount of time to traverse this distance.

    Returns:
      An array with three elements (in order): Limiting positive acceleration,
      negative acceleration, and velocity.
    """
    seekPosition = self._plc.getTag( self._desiredPositionTag )

    return TrapezoidalMotion.computeTimeLimited(
      acceleration,
      deceleration,
      maxVelocity,
      self._position,
      seekPosition,
      desiredTime
    )


  #---------------------------------------------------------------------
  def computeVelocity( self, acceleration, deceleration, desiredTime ) :
    """
    Calculate a limiting velocity that will result in the desired time.  Useful
    for synchronizing multi-axis motion.

    Args:
      acceleration: Maximum positive acceleration.
      deceleration: Maximum negative acceleration.
      desiredTime: Amount of time to traverse this distance.

    Returns:
      Limiting velocity needed to obtain this time.  0 if the time needed is
      greater than desired time denoting the operation cannot be done.
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
    self._maxAcceleration = acceleration
    self._maxDeceleration = deceleration
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
  def startJog( self, acceleration, deceleration ) :
    """
    Start jogging.
    """
    velocity = seekPosition = self._plc.getTag( self._speedTag )

    if velocity != 0 :
      direction = self._plc.getTag( self._directionTag )

      if direction :
        velocity = -velocity

      self._startTime = self._simulationTime.get()
      self._maxAcceleration = acceleration
      self._maxDeceleration = deceleration

      self._motion =                                          \
        TrapezoidalMotion                                     \
        (                                                     \
          acceleration,                                       \
          deceleration,                                       \
          velocity,                                           \
          self._position,                                     \
          None
        )

      self._startPosition = self._position
      self._inMotion = True
      self._isJog = True

  #---------------------------------------------------------------------
  def hardStop( self ) :
    """
    Hard motion stop.  Used for E-stops.
    """
    delta = self._simulationTime.get() - self._startTime
    time = delta.total_seconds()
    self._motion.hardStop( time )
    self._isJog = False
    self._inMotion = False
    self._velocity = 0
    self._acceleration = 0

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop current motion.  Use deceleration.
    """

    if self._isSeek or self._isJog :
      delta = self._simulationTime.get() - self._startTime
      time = delta.total_seconds()
      self._motion.computeStop( self._maxDeceleration, time )
      self._isJog = False
      self._isSeek = False

  #---------------------------------------------------------------------
  def isInMotion( self ) :
    """
    See if motor is in motion.

    Returns:
      True if motor is in motion, False if not.
    """
    return self._inMotion

  #---------------------------------------------------------------------
  def computeJitter( self ) :
    """
    Compute a random amount of position jitter.
    Uses Box-Muller transform.

    Returns:
      Random amount of error (+/-) to add to position.
    """
    r1 = random.random()
    r2 = random.random()

    result  = math.sqrt( -2 * math.log( r1 ) )
    result *= math.cos( 2 * math.pi * r2 )
    result *= SimulatedMotor.JITTER

    return result

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update motion. Call after a change to simulation time.
    """
    delta = self._simulationTime.get() - self._startTime
    time = delta.total_seconds()
    timeDelta = time - self._lastTime

    saveMotion = self._inMotion
    if self._inMotion :
      self._inMotion = self._motion.isMoving( time )
    elif self._wasEnabled :
      if self._isSeek :
        self._motion.hardStop( time )
        self._isSeek = False

    # Interpolate motion.
    self._position     = self._motion.interpolatePosition( time )
    self._velocity     = self._motion.interpolateVelocity( time )
    self._acceleration = self._motion.interpolateAcceleration( time )

    # Simulate servo error.
    self._position     += self.computeJitter()
    self._velocity     += self.computeJitter() * timeDelta
    self._acceleration += 1/2 * self.computeJitter() * timeDelta**2

    # Update the tag data.
    self._plc.write( self._motionTag, self._inMotion )
    self._plc.write( self._positionTag, self._position )
    self._plc.write( self._velocityTag, self._velocity )
    self._plc.write( self._accelerationTag, self._acceleration )

    self._wasEnabled = saveMotion
    self._lastTime   = time


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
    self._maxAcceleration = 0
    self._maxDeceleration = 0
    self._maxVelocity     = 0
    self._startTime       = simulationTime.get()
    self._lastTime        = 0
    self._motion = TrapezoidalMotion( 0, 0, 0, 0, 0 )

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

  #---------------------------------------------------------------------
  def setSpeedTag( self, speed ) :
    """
    Set the speed tag.

    Args:
      speed: New speed to write.
    """
    return self._plc.setupTag( self._speedTag, speed )
