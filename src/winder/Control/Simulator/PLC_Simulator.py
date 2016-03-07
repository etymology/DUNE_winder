###############################################################################
# Name: PLC_Simulator.py
# Uses: Simulate the PLC control logic.
# Date: 2016-02-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Simulator.SimulatedMotor import SimulatedMotor

class PLC_Simulator :

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update simulator.  Call periodically.
    """
    moveType = self._io.plc.getTag( self._moveTypeTag )

    if self._lastMoveType != moveType :
      # Stop?
      if self._io.plcLogic.MoveTypes.IDLE == moveType :
        self._xAxis.stop()
        self._yAxis.stop()
      # Seek in X/Y?
      elif self._io.plcLogic.MoveTypes.SEEK_XY == moveType :
        velocity = self._io.plc.getTag( self._maxVelocityTag )
        self._xAxis.startSeek( velocity )
        self._yAxis.startSeek( velocity )

        self._io.plc.write( self._stateTag, self._io.plcLogic.States.MOVING )
      # Jog in X/Y?
      elif self._io.plcLogic.MoveTypes.JOG_XY == moveType :
        self._xAxis.startJog()
        self._yAxis.startJog()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.MOVING )
      # Seek in Z?
      elif self._io.plcLogic.MoveTypes.SEEK_Z == moveType :
        velocity = self._io.plc.getTag( self._maxVelocityTag )
        self._zAxis.startSeek( velocity )

        self._io.plc.write( self._stateTag, self._io.plcLogic.States.MOVING )
      # Jog in Z?
      elif self._io.plcLogic.MoveTypes.JOG_XY == moveType :
        self._zAxis.startJog()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.MOVING )

      self._lastMoveType = moveType

    self._xAxis.poll()
    self._yAxis.poll()
    self._zAxis.poll()

    if not self._xAxis.isInMotion() and not self._yAxis.isInMotion() :
      self._io.plc.write( self._moveTypeTag, self._io.plcLogic.MoveTypes.IDLE )
      self._io.plc.write( self._stateTag, self._io.plcLogic.States.READY )

      # Force an update of move state machine.
      # NOTE: We use None because the winder may immediately request an other
      # move, putting the move type back to where it was.
      self._lastMoveType = None

  #---------------------------------------------------------------------
  def _writeCallback( self, tag, data ) :
    """
    Callback run whenever a tag is written.

    Args:
      tag: Ignored.
      data: Ignored.
    """
    self.poll()

  #---------------------------------------------------------------------
  def __init__( self, io ) :
    """
    Construct.

    Args:
      io - Instance of I/O map.
    """
    self._io = io

    # Add self to I/O polling callback list.
    io.pollCallbacks.append( self.poll )

    # Simulated motors.
    self._xAxis = SimulatedMotor( io.plc, "X", io.simulationTime )
    self._yAxis = SimulatedMotor( io.plc, "Y", io.simulationTime )
    self._zAxis = SimulatedMotor( io.plc, "Z", io.simulationTime )

    # Simulated I/O points.
    io.plc.setupTag( "Point_IO:1:I", 0 )

    # Tags for top-level PLC control.
    self._moveTypeTag        = io.plc.setupTag( "MOVE_TYPE", io.plcLogic.MoveTypes.IDLE )
    self._stateTag           = io.plc.setupTag( "STATE", io.plcLogic.States.READY )
    self._maxVelocityTag     = io.plc.setupTag( "XY_MAX_VELOCITY", 0.0 )
    self._maxAccelerationTag = io.plc.setupTag( "XY_MAX_ACCELERATION", 0.0 )
    self._maxDecelerationTag = io.plc.setupTag( "XY_MAX_DECELERATION", 0.0 )
    self._blinky             = io.plc.setupTag( "BLINKY", 0.0 )

    # Initial states of PLC state machine.
    self._lastState = io.plcLogic.States.READY
    self._lastMoveType = io.plcLogic.MoveTypes.IDLE
