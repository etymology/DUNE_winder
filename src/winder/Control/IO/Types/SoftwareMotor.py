###############################################################################
# Name: SoftwareMotor.py
# Uses: Motor simulation.
# Date: 2016-02-07
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from IO.Primitives.Motor import Motor
from Simulator.Motion import Motion

class SoftwareMotor( Motor ) :
  #---------------------------------------------------------------------
  def __init__( self, name, simulationTime ) :
    """
    Constructor.

    Args:
      name: Name of motor.

    """

    Motor.__init__( self, name )
    self._simulationTime  = simulationTime
    self._wasEnabled      = False
    #self._isEnabled       = False
    self._inMotion        = False
    self._torque          = 0
    self._maxTorque       = 1000
    self._seekPosition    = 0
    self._position        = 0
    self._velocity        = 0
    self._acceleration    = 0
    self._position        = 0
    self._jerk            = 200
    self._maxAcceleration = 100
    self._maxVelocity     = 200
    self._startTime       = simulationTime.get()
    self._motion          = Motion()

  #---------------------------------------------------------------------
  def isFunctional( self ) :
    """
    Check to see if motor is ready to run.

    Returns:
      True if functional, False if not.
    """
    return True

  #---------------------------------------------------------------------
  def setDesiredPosition( self, position ) :
    """
    Go to a location.

    Args:
      positions: Position to seek (in motor units).

    """

    if not position == self._position :
        self._inMotion = True
        self._seekPosition = position
        self._startTime = self._simulationTime.get()
        self._motion =                    \
          Motion                          \
          (                               \
            self._jerk,                   \
            self._maxAcceleration,        \
            self._maxVelocity,            \
            self._position,               \
            position                      \
          )

  #---------------------------------------------------------------------
  def getDesiredPosition( self ) :
    """
    Return the desired (seeking) position.

    Returns:
      Desired motor position.
    """

    return self._seekPosition

  #---------------------------------------------------------------------
  def isSeeking( self ) :
    """
    See if the motor is in motion.

    Returns:
      True if seeking desired position, False if at desired position.
    """

    return self._inMotion

  # #---------------------------------------------------------------------
  # def seekWait( self ) :
  #   """
  #   Block until seek is obtained.
  #
  #   """
  #
  #   if self._inMotion:
  #     self._seekSemaphore = SystemSemaphore( 0 )
  #     self._seekSemaphore.acquire()

  #---------------------------------------------------------------------
  def getPosition( self ) :
    """
    Return current motor position.

    Returns:
      Motor position (in motor units).
    """

    return self._position

  #---------------------------------------------------------------------
  def setMaxVelocity( self, maxVelocity ) :
    """
    Set maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    self._maxVelocity = maxVelocity

  #---------------------------------------------------------------------
  def getMaxVelocity( self ) :
    """
    Get maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    return self._maxVelocity

  #---------------------------------------------------------------------
  def getVelocity( self ) :
    """
    Get current motor velocity.

    Returns:
      Current motor velocity (in motor units/second).
    """

    return self._velocity

  #---------------------------------------------------------------------
  def setVelocity( self, velocity ) :
    """
    Set motor velocity.  Useful for jogging motor.  Set to 0 to stop.

    Args:
      velocity: Desired velocity.  Negative velocity is reverse direction.
    """

    # $$$FUTURE - This doesn't work.
    self._velocity = velocity

  #---------------------------------------------------------------------
  def setMaxAcceleration( self, maxAcceleration ) :
    """
    Set maximum acceleration motor may move.

    Args:
      maxAcceleration: Maximum acceleration motor may move.

    """

    self._maxAcceleration = maxAcceleration

  #---------------------------------------------------------------------
  def getMaxAcceleration( self ) :
    """
    Get maximum acceleration motor may move.

    Returns:
      Maximum acceleration motor may move.
    """

    return self._maxAcceleration

  #---------------------------------------------------------------------
  def getAcceleration( self ) :
    """
    Get current motor acceleration.

    Returns:
      Motor acceleration (in motor units/second squared).
    """

    return self._acceleration

  #---------------------------------------------------------------------
  def setMaxTorque( self, maxTorque ) :
    """
    Set maximum torque motor may exert.

    Args:
      maxTorque: Maximum torque motor may exert.

    """

    self._maxTorque = maxTorque

  #---------------------------------------------------------------------
  def getMaxTorque( self ) :
    """
    Get maximum torque motor may exert.

    Returns:
      Maximum torque.
    """

    return self._maxTorque

  #---------------------------------------------------------------------
  def getTorque( self ) :
    """
    Get the current torque on motor shaft.

    Returns:
      Torque on motor shaft (in motor torque units).
    """

    return self._torque

  #---------------------------------------------------------------------
  def setTorque( self, torque ) :
    """
    Set the amount of torque the motor reports.

    Returns:
      Torque the motor reports.
    """

    self._torque = torque

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update motion. Call after a change to simulation time.

    """

    delta = self._simulationTime.get() - self._startTime
    time = delta.total_seconds()

    if self._inMotion :
      self._inMotion     = self._motion.isMoving( time )
      self._position     = self._motion.interpolatePosition( time )
      self._velocity     = self._motion.interpolateVelocity( time )
      self._acceleration = self._motion.interpolateAcceleration( time )

      #if not self._inMotion and None != self._seekSemaphore :
      #  self._seekSemaphore.release()
      #  self._seekSemaphore = None
    elif self._wasEnabled :
      self._motion.hardStop( time )
      self._position     = self._motion.interpolatePosition( time )
      self._velocity     = self._motion.interpolateVelocity( time )
      self._acceleration = self._motion.interpolateAcceleration( time )

    self._wasEnabled = self._inMotion

# end class
