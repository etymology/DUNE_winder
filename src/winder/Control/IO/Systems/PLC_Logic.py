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
    INIT   = 0
    READY  = 1
    MOVING = 2  # $$$DEBUG - Is this correct?
  # end class

  # States for move type state machine.
  class MoveTypes :
    IDLE    = 0
    JOG_XY  = 1
    SEEK_XY = 2
    JOG_Z   = 3
    SEEK_Z  = 4
  # end class

  #---------------------------------------------------------------------
  def stopXY( self ) :
    """
    Stop X/Y position seek.
    """
    self._moveType.set( self.MoveTypes.IDLE )

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

    self._maxVelocity.set( self._velocity )
    self._xyAxis.setDesiredPosition( [ x, y ] )
    self._moveType.set( self.MoveTypes.SEEK_XY )

  #---------------------------------------------------------------------
  def isXY_SeekComplete( self ) :
    """
    Check to see if an X/Y seek is complete.

    Returns:
      True if seek complete, False if not.

    Notes:
      Checks to see if the movement state machine is idle.  So this
      also returns False when jogging.
    """
    state = self._state.get()

    if self.States.READY == state :
      result = True
    else :
      result = False

    return result

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
  def poll( self ) :
    """
    Internal update. Call periodically.
    """
    PLC.Tag.pollAll( self._plc )

  #---------------------------------------------------------------------
  def __init__( self, plc, xyAxis ) :
    """
    Constructor.

    Args:
      plc: Instance of PLC.
      xyAxis: Instance of MultiAxisMotor for X/Y axis.
    """
    self._plc = plc
    self._xyAxis = xyAxis

    attributes = PLC.Tag.Attributes()
    attributes.isPolled = True
    self._moveType = PLC.Tag( "Move type", plc, "MOVE_TYPE", attributes, tagType="INT" )
    self._state    = PLC.Tag( "State", plc, "STATE", attributes, tagType="DINT" )

    self._maxVelocity = PLC.Tag( "MaxVelocity", plc, "XY_MAX_VELOCITY", tagType="REAL" )
    self._maxAcceleration = PLC.Tag( "MaxAcceleration", plc, "XY_MAX_ACCELERATION", tagType="REAL" )
    self._maxDeceleration = PLC.Tag( "MaxDeceleration", plc, "XY_MAX_DECELERATION", tagType="REAL" )

    self._velocity = 1.0

# end class
