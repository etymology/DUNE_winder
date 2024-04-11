###############################################################################
# Name: MultiAxisMotor.py
# Uses: Group of several motors that are controlled together.
# Date: 2016-02-09
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   Motors can be grouped to act together.  This is most useful for an x/y
#   set where to the motors act in unison.
###############################################################################

class MultiAxisMotor :
  #---------------------------------------------------------------------
  def __init__( self, name, motors ) :
    """
    Constructor.

    Args:
      name: Name of IO device.
      motors: A list of IO.Primitives.Motor types to be grouped.

    """

    self._motors = motors

  #---------------------------------------------------------------------
  def setEnable( self, isEnabled ) :
    """
    Enable/disable motors.

    Args:
      isEnabled: True if enabled, False if not.

    """

    for motor in self._motors :
      motor.setEnable( isEnabled )

  #---------------------------------------------------------------------
  def getPosition( self ):
    """
    Return current motor positions.

    Returns:
      Array of motor positions (in motor units).
    """
    return [motor.getPosition() for motor in self._motors]

  #---------------------------------------------------------------------
  def setDesiredPosition( self, positions ):
    """
    Go to a location specified by a list.

    Args:
      positions: A list of position. Must have one value for each motor.

    """
    assert( len( positions ) == len( self._motors ) )

    for index, motor in enumerate(self._motors):
      motor.setDesiredPosition( positions[ index ] )

  #---------------------------------------------------------------------
  def isSeeking( self ) :
    """
    See if the motors are in motion.

    Returns:
      True if seeking desired position, False if at desired position.
    """

    result = False
    for motor in self._motors :
      result |= motor.isSeeking()

    return result

  #---------------------------------------------------------------------
  def seekWait( self ) :
    """
    Block until seek is obtained.

    """

    for motor in self._motors :
      motor.seekWait()

  #---------------------------------------------------------------------
  def setMaxVelocity( self, maxVelocity ) :
    """
    Set maximum velocity motors may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    for motor in self._motors :
      motor.setMaxVelocity( maxVelocity )

  #---------------------------------------------------------------------
  def getMaxVelocity( self ) :
    """
    Get maximum velocity motors may move.

    Returns:
      Maximum velocity motors may move.
    """

    return self._motor[ 0 ].getMaxVelocity()

  #---------------------------------------------------------------------
  def setVelocity( self, velocities ):
    """
    Set motor velocities.  Useful for jogging motor.  Set to 0 to stop.

    Args:
      velocity: Desired velocity.  Negative velocity is reverse direction.
    """

    assert( len( velocities ) == len( self._motors ) )

    for index, motor in enumerate(self._motors):
      motor.setVelocity( velocities[ index ] )

  #---------------------------------------------------------------------
  def setMaxAcceleration( self, maxAcceleration ) :
    """
    Set maximum acceleration motors may move.

    Args:
      maxAcceleration: Maximum acceleration motors may move.

    """

    for motor in self._motors :
      motor.setMaxAcceleration( maxAcceleration )

  #---------------------------------------------------------------------
  def getMaxAcceleration( self ) :
    """
    Get maximum acceleration motors may move.

    Returns:
      Maximum acceleration motors may move.
    """

    return self._motor[ 0 ].getMaxAcceleration()

# end class
