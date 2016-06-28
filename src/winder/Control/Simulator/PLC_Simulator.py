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

from Machine.MachineGeometry import MachineGeometry

class PLC_Simulator :

  # Enumeration for latch positions.
  class LatchPosition :
    TOP    = 0
    MIDDLE = 1
    BOTTOM = 2
  # end class

  #=====================================================================
  # Logical input mapped to a bit of a tag.
  #=====================================================================
  class SimulatedInput :

    #-------------------------------------------------------------------
    def __init__( self, io, tagName, bit, default=False ) :
      """
      Constructor.

      Args:
        io: Instance of IO map.
        tagName: Name of the tag in which the input resides.
        bit: The bit of the tag in which the input resides.
        default: Initial state of input.
      """
      self._tagName = tagName
      self._bit = bit
      self._io = io
      self.set( default )

    #-------------------------------------------------------------------
    def get( self ) :
      """
      Return the value of the input.

      Returns:
        Value of the input.
      """
      value = self._io.plc.getTag( self._tagName )
      value = value >> self._bit
      value = value & 0x01

      return value

    #-------------------------------------------------------------------
    def set( self, state ) :
      """
      Set the state of this input.

      Args:
        state: State to set the input.
      """
      mask = ( 1 << self._bit )
      value = self._io.plc.getTag( self._tagName )
      value = value & ~mask

      if state :
        value = value | mask

      self._io.plc.setupTag( self._tagName, value )

  # end class

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update simulator.  Call periodically.
    """
    self._simulationTime.setLocal()

    xySpeed = self._io.plc.getTag( self._maxXY_VelocityTag )
    if self._lastXY_Speed != xySpeed :

      if 0 == xySpeed :
        self._xAxis.stop()
        self._yAxis.stop()
      else:
        # $$$FUTURE - Modify speed
        pass

      self._lastXY_Speed = xySpeed

    zSpeed = self._zAxis.getSpeedTag()
    if self._lastZ_Speed != zSpeed :

      if 0 == zSpeed :
        self._zAxis.stop()
      else:
        # $$$FUTURE - Modify speed
        pass

      self._lastZ_Speed = zSpeed

    moveType = self._io.plc.getTag( self._moveTypeTag )
    if self._lastMoveType != moveType :
      # Reset?
      if self._io.plcLogic.MoveTypes.RESET == moveType :
        self._xAxis.stop()
        self._yAxis.stop()
        self._zAxis.stop()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.READY )

      # Seek in X/Y?
      elif self._io.plcLogic.MoveTypes.SEEK_XY == moveType :
        velocity = self._io.plc.getTag( self._maxXY_VelocityTag )
        acceleration = self._io.plc.getTag( self._maxXY_AccelerationTag )
        deceleration = self._io.plc.getTag( self._maxXY_DecelerationTag )

        xTime = self._xAxis.travelTime( velocity, acceleration, deceleration )
        yTime = self._yAxis.travelTime( velocity, acceleration, deceleration )

        xVelocity = velocity
        yVelocity = velocity

        if xTime > 0 and yTime > 0 :
          if xTime < yTime :
            xVelocity = self._xAxis.computeVelocity( acceleration, deceleration, yTime )
          else:
            yVelocity = self._yAxis.computeVelocity( acceleration, deceleration, xTime )

        self._xAxis.startSeek( xVelocity, acceleration, deceleration )
        self._yAxis.startSeek( yVelocity, acceleration, deceleration )

        self._io.plc.write( self._stateTag, self._io.plcLogic.States.XY_SEEK )
      # Jog in X/Y?
      elif self._io.plcLogic.MoveTypes.JOG_XY == moveType :
        self._xAxis.startJog()
        self._yAxis.startJog()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.XY_JOG )

      # Seek in Z?
      elif self._io.plcLogic.MoveTypes.SEEK_Z == moveType :
        velocity = self._zAxis.getSpeedTag()
        acceleration = self._io.plc.getTag( self._maxZ_AccelerationTag )
        deceleration = self._io.plc.getTag( self._maxZ_DecelerationTag )

        self._zAxis.startSeek( velocity, acceleration, deceleration )
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

        # State is now latching.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCHING )

        # Wait 1 second for transition.
        self._latchDelay.set( 500 )

      # Re-home latch?
      # (Does nothing.)
      elif self._io.plcLogic.MoveTypes.HOME_LATCH == moveType :
        # State is now homing.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCH_HOMEING )

        # Wait 5 seconds for transition.
        self._latchDelay.set( 5000 )

      # Unlock latch?
      elif self._io.plcLogic.MoveTypes.LATCH_UNLOCK == moveType :
        # Just stay in this mode until reset.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCH_RELEASE )

      self._lastMoveType = moveType

    self._xAxis.poll()
    self._yAxis.poll()
    self._zAxis.poll()

    # Local function to validate that motor positions are within limits.
    def verifyPositionLimits( axis, axisIO, positionMin, positionMax ) :
      if axis.isInMotion() :
        position = axisIO.getPosition()
        velocity = axisIO.getVelocity()
        if   ( velocity < 0 and position < positionMin ) \
          or ( velocity > 0 and position > positionMax ) :

          print axisIO.getName(), "out of range", positionMin, "<=", position, "<=", positionMax

          # Change to an error state.
          self._io.plc.write( self._stateTag, self._io.plcLogic.States.ERROR )

          # Stop all motion.
          self._xAxis.stop()
          self._yAxis.stop()
          self._zAxis.stop()

    # Verify that all axis potions are within limits.
    verifyPositionLimits( self._xAxis, self._io.xAxis, self._xMin, self._xMax )
    verifyPositionLimits( self._yAxis, self._io.yAxis, self._yMin, self._yMax )
    verifyPositionLimits( self._zAxis, self._io.zAxis, self._zMin, self._zMax )

    #
    # Simulate inputs based on machine state.
    #

    # Extended and retracted inputs.
    isExtended = ( self._io.zAxis.getPosition() >= self._machineGeometry.zTravel )
    isRetected = ( self._io.zAxis.getPosition() <= 0 )
    self.Z_Extended.set( isExtended )
    self.Z_Retracted_1A.set( isRetected )

    # End-of-travels.
    if self._io.zAxis.getPosition() > self._zMax \
      or self._io.zAxis.getPosition() < self._zMin :
      self.Z_End_of_Travel.set( True )
    else :
      self.Z_End_of_Travel.set( False )

    # Latch and present sensors.
    if self._latchPosition == self.LatchPosition.TOP :
      self.Z_Fixed_Latched.set( True )
      self.Z_Stage_Latched.set( False )
      self.Latch_Actuator_Top.set( True )
      self.Latch_Actuator_Mid.set( True )
      self.Z_Stage_Present.set( isExtended )
      self.Z_Fixed_Present.set( True )
    elif self._latchPosition == self.LatchPosition.MIDDLE :
      self.Z_Fixed_Latched.set( True )
      self.Z_Stage_Latched.set( False )
      self.Latch_Actuator_Top.set( False )
      self.Latch_Actuator_Mid.set( True )
      self.Z_Stage_Present.set( isExtended )
      self.Z_Stage_Present.set( isExtended )
    elif self._latchPosition == self.LatchPosition.BOTTOM :
      self.Z_Fixed_Latched.set( False )
      self.Z_Stage_Latched.set( True )
      self.Latch_Actuator_Top.set( False )
      self.Latch_Actuator_Mid.set( False )
      self.Z_Stage_Present.set( True )
      self.Z_Fixed_Present.set( isExtended )

    state = self._io.plc.getTag( self._stateTag )

    # All motions and delays finished?
    if not self._xAxis.isInMotion() \
      and not self._yAxis.isInMotion() \
      and not self._zAxis.isInMotion() \
      and self._latchDelay.hasExpired() \
      and self._io.plcLogic.States.LATCH_RELEASE != state \
      and self._io.plcLogic.States.ERROR != state :

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
    self._maxXY_VelocityTag     = io.plc.setupTag( "XY_SPEED", 0.0 )
    self._maxXY_AccelerationTag = io.plc.setupTag( "XY_ACCELERATION", 0.0 )
    self._maxXY_DecelerationTag = io.plc.setupTag( "XY_DECELERATION", 0.0 )
    self._maxZ_AccelerationTag  = io.plc.setupTag( "Z_ACCELERATION", 0.0 )
    self._maxZ_DecelerationTag  = io.plc.setupTag( "Z_DECELLERATION", 0.0 )

    # Initial states of PLC state machine.
    self._lastState = io.plcLogic.States.READY
    self._lastMoveType = io.plcLogic.MoveTypes.RESET
    self._lastXY_Speed = None
    self._lastZ_Speed = None

    self._latchDelay = Delay( self._simulationTime )
    self._latchPosition = PLC_Simulator.LatchPosition.BOTTOM

    self._machineGeometry = MachineGeometry()

    self._xMin = self._machineGeometry.limitLeft
    self._xMax = self._machineGeometry.limitRight
    self._yMin = self._machineGeometry.limitBottom
    self._yMax = self._machineGeometry.limitTop
    self._zMin = self._machineGeometry.limitRetracted
    self._zMax = self._machineGeometry.limitExtended




    # self.Z_EndOfTravel    = io.plc.setupTag( "Z_EOT",             False )
    # self.Z_StageLatched   = io.plc.setupTag( "Z_Stage_Latched",   False )
    # self.Z_FixedLatched   = io.plc.setupTag( "Z_Fixed_Latched",   False )
    # self.Z_Retracted_1a   = io.plc.setupTag( "Z_Retracted1A",     False )
    # self.Z_Retracted_1b   = io.plc.setupTag( "Z_Retracted1B",     False )
    # self.Z_Retracted_2a   = io.plc.setupTag( "Z_Retracted2A",     False )
    # self.Z_Retracted_2b   = io.plc.setupTag( "Z_Retracted2B",     False )
    # self.Z_StagePresent   = io.plc.setupTag( "Z_Stage_Present",   False )
    # self.Z_FixedPresent   = io.plc.setupTag( "Z_Fixed_Present",   False )
    # self.Z_Extended       = io.plc.setupTag( "Z_Extended",        False )
    # self.Z_Compressed     = io.plc.setupTag( "Z_Spring_Comp",     False )
    # self.Z_StageUnlatched = io.plc.setupTag( "Z_Stage_Unlatched", False )
    # self.Z_ClearToEngage  = io.plc.setupTag( "Z_OK_To_Engage",    False )

    self._machine_SW_Stat = io.plc.setupTag( "Machine_SW_Stat", 0 )

    self.Latch_Homed          = self.SimulatedInput( io, "Machine_SW_Stat", 0, False )
    self.Z_Retracted_1A       = self.SimulatedInput( io, "Machine_SW_Stat", 1, False )
    self.Z_Retracted_2B       = self.SimulatedInput( io, "Machine_SW_Stat", 2, False )
    self.Z_Retracted_2A       = self.SimulatedInput( io, "Machine_SW_Stat", 3, False )
    self.Z_Retracted_2B       = self.SimulatedInput( io, "Machine_SW_Stat", 4, False )
    self.Z_Extended           = self.SimulatedInput( io, "Machine_SW_Stat", 5, False )
    self.Z_Stage_Latched      = self.SimulatedInput( io, "Machine_SW_Stat", 6, False )
    self.Z_Fixed_Latched      = self.SimulatedInput( io, "Machine_SW_Stat", 7, False )
    self.Z_End_of_Travel      = self.SimulatedInput( io, "Machine_SW_Stat", 8, False )
    self.Z_Stage_Present      = self.SimulatedInput( io, "Machine_SW_Stat", 9, False )
    self.Z_Fixed_Present      = self.SimulatedInput( io, "Machine_SW_Stat", 10, False )
    self.Z_Spring_Comp        = self.SimulatedInput( io, "Machine_SW_Stat", 11, False )
    self.Latch_Actuator_Top   = self.SimulatedInput( io, "Machine_SW_Stat", 12, False )
    self.Latch_Actuator_Mid   = self.SimulatedInput( io, "Machine_SW_Stat", 13, False )
