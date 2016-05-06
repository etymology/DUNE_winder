###############################################################################
# Name: PLC_Logic.py
# Uses: Interface for special logic inside PLC.
# Date: 2016-02-26
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   This unit is designed to work with specific PLC logic.  It handles how
#   operations must be preformed for the given setup, such as how to initiate
#   a synchronized X/Y movement, or other multi-step operation.  The scope of
#   this unit is limited to operations performed by the ladder logic in the
#   PLC.  No operation that isn't specific to the ladder logic should be in
#   this unit.
###############################################################################
from IO.Devices.PLC import PLC

class PLC_Logic :

  # States for primary state machine.
  class States :
    INIT          = 0
    READY         = 1
    XY_JOG        = 2
    XY_SEEK       = 3
    Z_JOG         = 4
    Z_SEEK        = 5
    LATCHING      = 6
    LATCH_HOMEING = 7
    LATCH_RELEASE = 8
  # end class

  # States for move type state machine.
  class MoveTypes :
    RESET      = 0
    JOG_XY     = 1
    SEEK_XY    = 2
    JOG_Z      = 3
    SEEK_Z     = 4
    LATCH      = 5
    HOME_LATCH = 6
    LATCH_UNLOCK = 7
  # end class

  #---------------------------------------------------------------------
  def isReady( self ) :
    """
    Check to see if the PLC is in a ready state.  This can be used to determine
    if all motion has completed, including all motor motion and latching
    operations.

    Returns:
      True if ready, False if some other operation is taking place.
    """
    state = self._state.get()

    if self.States.READY == state :
      result = True
    else :
      result = False

    return result

  #---------------------------------------------------------------------
  def stopSeek( self ) :
    """
    Stop all motor position seeks.
    """
    self._moveType.set( self.MoveTypes.RESET )

  #---------------------------------------------------------------------
  def setXY_Position( self, x, y, velocity=None ) :
    """
    Make a coordinated move of the X/Y axis.

    Args:
      x: Position to seek in x-axis (in millimeters).
      y: Position to seek in y-axis (in millimeters).
      velocity: Maximum velocity at which to make move.  None to use last
        velocity.
    """
    if None != velocity :
      self._velocity = velocity

    self._maxXY_Velocity.set( self._velocity )
    self._xyAxis.setDesiredPosition( [ x, y ] )
    self._moveType.set( self.MoveTypes.SEEK_XY )

  #---------------------------------------------------------------------
  def jogXY( self, xVelocity, yVelocity ) :
    """
    Jog the X/Y axis at a given velocity.

    Args:
      xVelocity: Speed of travel on x-axis.  0 for no motion or stop, negative
        for seeking in reverse direction.
      yVelocity: Speed of travel on y-axis.  0 for no motion or stop, negative
        for seeking in reverse direction.
    """

    self._xyAxis.setVelocity( [ xVelocity, yVelocity ] )
    self._moveType.set( self.MoveTypes.JOG_XY )

  #---------------------------------------------------------------------
  def setZ_Position( self, position, velocity=None ) :
    """
    Move Z-axis to a position.

    Args:
      position: Position to seek in z-axis (in millimeters).
      velocity: Maximum velocity at which to make move.  None to use last
        velocity.
    """
    if None != velocity :
      self._velocity = velocity

    self._zAxis.setVelocity( self._velocity )
    self._zAxis.setDesiredPosition( position )
    self._moveType.set( self.MoveTypes.SEEK_Z )

  #---------------------------------------------------------------------
  def jogZ( self, velocity ) :
    """
    Jog the Z axis at a given velocity.

    Args:
      velocity: Speed of travel.  0 for no motion or stop, negative
        for seeking in reverse direction.
    """

    self._zAxis.setVelocity( velocity )
    self._moveType.set( self.MoveTypes.JOG_Z )

  #---------------------------------------------------------------------
  def latch( self ) :
    """
    Start a latching operation.
    """
    self._moveType.set( self.MoveTypes.LATCH )

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Internal update. Call periodically.
    """
    PLC.Tag.pollAll( self._plc )

  #---------------------------------------------------------------------
  def getMoveType( self ) :
    """
    Return the move type tag value.

    Returns:
      Move type tag value, number from PLC_Logic.MoveTypes.
    """
    return self._moveType.get()

  #---------------------------------------------------------------------
  def getState( self ) :
    """
    Return the state tag value.

    Returns:
      State tag value, number from PLC_Logic.States.
    """
    return self._state.get()

  #---------------------------------------------------------------------
  def reset( self ) :
    """
    Reset PLC logic.  Clears errors.
    """
    self._moveType.set( self.MoveTypes.RESET )

  #---------------------------------------------------------------------
  def latchHome( self ) :
    """
    Start a latch homing operation.
    """
    self._moveType.set( self.MoveTypes.HOME_LATCH )

  #---------------------------------------------------------------------
  def latchUnlock( self ) :
    """
    Unlock latch motor for manual operation.  Requires PLC_Logic.reset after
    complete.
    """
    self._moveType.set( self.MoveTypes.LATCH_UNLOCK )

  #---------------------------------------------------------------------
  def setupLimits( self, maxVelocity=None, maxAcceleration=None, maxDeceleration=None ) :
    """
    Setup the velocity and acceleration limits.

    Args:
      maxVelocity: Maximum velocity.
      maxAcceleration: Maximum positive acceleration.
      maxDeceleration: Maximum negative acceleration.
    """
    if None != maxVelocity :
      self._velocity = maxVelocity

    if None != maxAcceleration :
      self._maxAcceleration = maxAcceleration

    if None != maxDeceleration :
      self._maxDeceleration = maxDeceleration

    self._maxXY_Velocity.set( self._velocity )
    self._maxXY_Acceleration.set( self._maxAcceleration )
    self._maxXY_Deceleration.set( self._maxDeceleration )
    self._maxZ_Acceleration.set( self._maxAcceleration )
    self._maxZ_Deceleration.set( self._maxDeceleration )

  #---------------------------------------------------------------------
  def __init__( self, plc, xyAxis, zAxis ) :
    """
    Constructor.

    Args:
      plc: Instance of PLC.
      xyAxis: Instance of MultiAxisMotor for X/Y axis.
    """
    self._plc = plc
    self._xyAxis = xyAxis
    self._zAxis = zAxis

    attributes = PLC.Tag.Attributes()
    attributes.isPolled = True
    self._state           = PLC.Tag( plc, "STATE", attributes, tagType="DINT" )

    self._moveType           = PLC.Tag( plc, "MOVE_TYPE", tagType="INT" )
    self._maxXY_Velocity     = PLC.Tag( plc, "XY_VELOCITY", tagType="REAL" )
    self._maxXY_Acceleration = PLC.Tag( plc, "XY_ACCELERATION", tagType="REAL" )
    self._maxXY_Deceleration = PLC.Tag( plc, "XY_DECELERATION", tagType="REAL" )
    self._maxZ_Acceleration  = PLC.Tag( plc, "Z_ACCELERATION", tagType="DINT" )
    self._maxZ_Deceleration  = PLC.Tag( plc, "Z_DECELLERATION", tagType="DINT" )

    self._velocity = 0.0
    self._maxAcceleration = 0
    self._maxDeceleration = 0

# end class
