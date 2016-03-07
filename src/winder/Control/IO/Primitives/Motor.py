###############################################################################
# Name: Motor.py
# Uses: Abstract class for motor control.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from IO_Point import IO_Point
from abc import ABCMeta, abstractmethod

class Motor( IO_Point ) :
  # Make class abstract.
  __metaclass__ = ABCMeta

  # Static list of all motors.
  list = []

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of motor.

    """

    IO_Point.__init__( self, name )

    Motor.list.append( self )

  #---------------------------------------------------------------------
  @abstractmethod
  def stop( self ) :
    """
    Stop the motor.

    """

    pass

  # #---------------------------------------------------------------------
  # @abstractmethod
  # def setEnable( self, isEnabled ) :
  #   """
  #   Enable/disable motor.
  #
  #   Args:
  #     isEnabled: True if enabled, False if not.
  #
  #   """
  #
  #   pass

  #---------------------------------------------------------------------
  @abstractmethod
  def setDesiredPosition( self, position ) :
    """
    Go to a location.

    Args:
      positions: Position to seek (in motor units).

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getDesiredPosition( self ) :
    """
    Return the desired (seeking) position.

    Returns:
      Desired motor position.
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def isSeeking( self ) :
    """
    See if the motor is in motion.

    Returns:
      True if seeking desired position, False if at desired position.
    """

    pass

  # #---------------------------------------------------------------------
  # @abstractmethod
  # def seekWait( self ) :
  #   """
  #   Block until seek is obtained.
  #
  #   """
  #
  #   pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getPosition( self ) :
    """
    Return current motor position.

    Returns:
      Motor position (in motor units).
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def setMaxVelocity( self, maxVelocity ) :
    """
    Set maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getMaxVelocity( self ) :
    """
    Get maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getVelocity( self ) :
    """
    Get current motor velocity.

    Returns:
      Current motor velocity (in motor units/second).
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def setVelocity( self, velocity ) :
    """
    Set motor velocity.  Useful for jogging motor.  Set to 0 to stop.

    Args:
      velocity: Desired velocity.  Negative velocity is reverse direction.
    """
    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def setMaxAcceleration( self, maxAcceleration ) :
    """
    Set maximum acceleration motor may move.

    Args:
      maxAcceleration: Maximum acceleration motor may move.

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getMaxAcceleration( self ) :
    """
    Get maximum acceleration motor may move.

    Returns:
      Maximum acceleration motor may move.
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getAcceleration( self ) :
    """
    Get current motor acceleration.

    Returns:
      Motor acceleration (in motor units/second squared).
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def setMaxTorque( self, maxTorque ) :
    """
    Set maximum torque motor may exert.

    Args:
      maxTorque: Maximum torque motor may exert.

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getMaxTorque( self ) :
    """
    Get maximum torque motor may exert.

    Returns:
      Maximum torque.
    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def getTorque( self ) :
    """
    Get the current torque on motor shaft.

    Returns:
      Torque on motor shaft (in motor torque units).
    """

    pass

  #---------------------------------------------------------------------
  def get( self ) :
    """
    Get function. Not meaningful.

    Returns:
      Returns motor position.
    """

    return self.getPosition()

  #---------------------------------------------------------------------
  @abstractmethod
  def poll( self ) :
    """
    Periodic update function used to update internal status.
    """
    pass

  #---------------------------------------------------------------------
  @staticmethod
  def pollAll() :
    """
    Update all motors.
    """

    for instance in Motor.list :
      instance.poll()

# end class
