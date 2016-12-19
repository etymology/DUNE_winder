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
    UNSERVO       = 9
    ERROR         = 10
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
    UNSERVO    = 8
  # end class

  class LatchPosition :
    FULL_UP    = 0
    PARTIAL_UP = 1
    DOWN       = 2
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
  def isError( self ) :
    """
    Check to see if PLC state machine is in error.

    Returns:
      True if in error, False if not.
    """

    return self.States.ERROR == self._state.get()

  #---------------------------------------------------------------------
  def stopSeek( self ) :
    """
    Stop all motor position seeks.
    """
    #self._moveType.set( self.MoveTypes.RESET )
    self._maxXY_Velocity.set( 0 )
    self._maxZ_Velocity.set( 0 )

  #---------------------------------------------------------------------
  def setXY_Position( self, x, y, velocity=None, acceleration=None, deceleration=None ) :
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

    if None != acceleration :
      self._maxXY_Acceleration.set( float( acceleration ) )

    if None != deceleration :
      self._maxXY_Deceleration.set( float( deceleration ) )

    self._maxXY_Velocity.set( self._velocity )
    self._xyAxis.setDesiredPosition( [ x, y ] )
    self._moveType.set( self.MoveTypes.SEEK_XY )

  #---------------------------------------------------------------------
  def jogXY( self, xVelocity, yVelocity, acceleration=None, deceleration=None ) :
    """
    Jog the X/Y axis at a given velocity.

    Args:
      xVelocity: Speed of travel on x-axis.  0 for no motion or stop, negative
        for seeking in reverse direction.
      yVelocity: Speed of travel on y-axis.  0 for no motion or stop, negative
        for seeking in reverse direction.
    """

    if None != acceleration :
      self._maxXY_Acceleration.set( float( acceleration ) )

    if None != deceleration :
      self._maxXY_Deceleration.set( float( deceleration ) )

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
  def getLatchPosition( self ) :
    """
    Get the current latch position.

    Returns:
      One of the PLC_Logic.LatchPosition elements.
    """
    return self._actuatorPosition.get()

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
  def maxVelocity( self, maxVelocity=None ) :
    """
    Set/get the maximum velocity.

    Args:
      maxVelocity: New maximum velocity (optional).

    Returns:
      Maximum velocity.
    """
    if None != maxVelocity :
      self._velocity = maxVelocity

    self._maxXY_Velocity.set( self._velocity )

    return self._velocity

  #---------------------------------------------------------------------
  def maxAcceleration( self, maxAcceleration=None ) :
    """
    Set/get the maximum positive acceleration.

    Args:
      maxVelocity: New maximum positive acceleration (optional).

    Returns:
      Maximum positive acceleration.
    """
    if None != maxAcceleration :
      self._maxAcceleration = maxAcceleration

    self._maxXY_Acceleration.set( self._maxAcceleration )
    self._maxZ_Acceleration.set( self._maxAcceleration )

    return self._maxAcceleration

  #---------------------------------------------------------------------
  def maxDeceleration( self, maxDeceleration=None ) :
    """
    Set/get the maximum negative acceleration.

    Args:
      maxVelocity: New maximum negative acceleration (optional).

    Returns:
      Maximum positive acceleration.
    """
    if None != maxDeceleration :
      self._maxDeceleration = maxDeceleration

    self._maxXY_Deceleration.set( self._maxDeceleration )
    self._maxZ_Deceleration.set( self._maxDeceleration )

    return self._maxDeceleration

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
  def servoDisable( self ) :
    """
    Disable servo control of motors.
    """
    self._moveType.set( self.MoveTypes.UNSERVO )

  #---------------------------------------------------------------------
  # $$$FUTURE
  def isInTransferArea( self ) :

    # $$$DEBUG - Fix.
    positions = self._xyAxis.getPosition()

    result = ( 0 == positions[ 0 ] and 0 == positions[ 1 ] )

    return result

  #---------------------------------------------------------------------
  # $$$FUTURE
  def setCameraTrigger( self, deltaX, deltaY ) :
    """
    Setup the PLC for camera triggering.

    Args:
      deltaX - Change in X after which to trigger camera.  0 to disable.
      deltaY - Change in Y after which to trigger camera.  0 to disable.
    """
    pass

  #---------------------------------------------------------------------
  # $$$FUTURE
  def flushCameraFIFO( self ) :
    pass

  #---------------------------------------------------------------------
  # $$$FUTURE
  def getCameraFIFO( self ) :
    """
    Return any new elements in camera FIFO.

    Returns:
      Array of new capture elements from camera.
    """
    pass

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
    self._latchPosition = 0

    attributes = PLC.Tag.Attributes()
    attributes.isPolled = True
    self._state           = PLC.Tag( plc, "STATE", attributes, tagType="DINT" )

    self._actuatorPosition   = PLC.Tag( plc, "ACTUATOR_POS",    tagType="DINT" )
    self._moveType           = PLC.Tag( plc, "MOVE_TYPE",       tagType="INT" )
    self._maxXY_Velocity     = PLC.Tag( plc, "XY_SPEED",        tagType="REAL" )
    self._maxXY_Acceleration = PLC.Tag( plc, "XY_ACCELERATION", tagType="REAL" )
    self._maxXY_Deceleration = PLC.Tag( plc, "XY_DECELERATION", tagType="REAL" )
    self._maxZ_Velocity      = PLC.Tag( plc, "Z_SPEED",         tagType="REAL" )
    self._maxZ_Acceleration  = PLC.Tag( plc, "Z_ACCELERATION",  tagType="REAL" )
    self._maxZ_Deceleration  = PLC.Tag( plc, "Z_DECELLERATION", tagType="REAL" )
    self.errorCode           = PLC.Tag( plc, "ERROR_CODE",      tagType="DINT" )

    self._velocity = 0.0
    self._maxAcceleration = 0
    self._maxDeceleration = 0

# end class
