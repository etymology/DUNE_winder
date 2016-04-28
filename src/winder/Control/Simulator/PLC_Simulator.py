###############################################################################
# Name: PLC_Simulator.py
# Uses: Simulate the PLC control logic.
# Date: 2016-02-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Simulator.SimulationTime import SimulationTime
from Simulator.SimulatedMotor import SimulatedMotor
from Simulator.Delay import Delay

class PLC_Simulator :

  class LatchPosition :
    TOP    = 0
    MIDDLE = 1
    BOTTOM = 2
  # end class

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update simulator.  Call periodically.
    """
    self._simulationTime.setLocal()
    moveType = self._io.plc.getTag( self._moveTypeTag )

    if self._lastMoveType != moveType :
      # Reset?
      if self._io.plcLogic.MoveTypes.RESET == moveType :
        self._xAxis.stop()
        self._yAxis.stop()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.READY )

      # Seek in X/Y?
      elif self._io.plcLogic.MoveTypes.SEEK_XY == moveType :
        velocity = self._io.plc.getTag( self._maxVelocityTag )
        self._xAxis.startSeek( velocity )
        self._yAxis.startSeek( velocity )

        self._io.plc.write( self._stateTag, self._io.plcLogic.States.XY_SEEK )
      # Jog in X/Y?
      elif self._io.plcLogic.MoveTypes.JOG_XY == moveType :
        self._xAxis.startJog()
        self._yAxis.startJog()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.XY_JOG )

      # Seek in Z?
      elif self._io.plcLogic.MoveTypes.SEEK_Z == moveType :
        velocity = self._zAxis.getSpeedTag()
        self._zAxis.startSeek( velocity )
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.Z_SEEK )

      # Jog in Z?
      elif self._io.plcLogic.MoveTypes.JOG_Z == moveType :
        self._zAxis.startJog()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.Z_JOG )

      # Change latch?
      elif self._io.plcLogic.MoveTypes.LATCH == moveType :
        # Change latch position.
        # (Currently change is instantaneous.)
        self._latchPosition += 1
        if self._latchPosition > self.LatchPosition.BOTTOM :
          self._latchPosition = 0

        # State is now homing.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCHING )

        # Wait 2 seconds for transition.
        self._latchDelay.set( 2000 )

      # Re-home latch?
      # (Does nothing.)
      elif self._io.plcLogic.MoveTypes.HOME_LATCH == moveType :
        # State is now homing.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCH_HOMEING )

        # Wait 2 seconds for transition.
        self._latchDelay.set( 2000 )

      # Unlock latch?
      elif self._io.plcLogic.MoveTypes.LATCH_UNLOCK == moveType :
        # Just stay in this mode until reset.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCH_RELEASE )

      self._lastMoveType = moveType

    self._xAxis.poll()
    self._yAxis.poll()
    self._zAxis.poll()

    state = self._io.plc.getTag( self._stateTag )
    # All motions and delays finished?
    if not self._xAxis.isInMotion() \
      and not self._yAxis.isInMotion() \
      and not self._zAxis.isInMotion() \
      and self._latchDelay.hasExpired() \
      and self._io.plcLogic.States.LATCH_RELEASE != state :

      self._io.plc.write( self._moveTypeTag, self._io.plcLogic.MoveTypes.RESET )
      self._io.plc.write( self._stateTag, self._io.plcLogic.States.READY )

      # Force an update of move state machine.
      # NOTE: We use None because the winder may immediately request an other
      # move, putting the move type back to where it was.
      self._lastMoveType = None

  #---------------------------------------------------------------------
  def __init__( self, io ) :
    """
    Construct.

    Args:
      io - Instance of I/O map.
    """
    self._io = io

    # Simulation time.
    # (So we could run at speeds other than real-time.)
    self._simulationTime = SimulationTime()

    # Add self to I/O polling callback list.
    io.pollCallbacks.insert( 0, self.poll )

    # Simulated motors.
    self._xAxis = SimulatedMotor( io.plc, "X", self._simulationTime )
    self._yAxis = SimulatedMotor( io.plc, "Y", self._simulationTime )
    self._zAxis = SimulatedMotor( io.plc, "Z", self._simulationTime )

    # Simulated I/O points.
    io.plc.setupTag( "Point_IO:1:I", 0 )

    # Tags for top-level PLC control.
    self._moveTypeTag        = io.plc.setupTag( "MOVE_TYPE", io.plcLogic.MoveTypes.RESET )
    self._stateTag           = io.plc.setupTag( "STATE", io.plcLogic.States.READY )
    self._maxVelocityTag     = io.plc.setupTag( "XY_VELOCITY", 0.0 )
    self._maxAccelerationTag = io.plc.setupTag( "XY_ACCELERATION", 0.0 )
    self._maxDecelerationTag = io.plc.setupTag( "XY_DECELERATION", 0.0 )

    # Initial states of PLC state machine.
    self._lastState = io.plcLogic.States.READY
    self._lastMoveType = io.plcLogic.MoveTypes.RESET

    self._latchDelay = Delay( self._simulationTime )
    self._latchPosition = PLC_Simulator.LatchPosition.TOP
