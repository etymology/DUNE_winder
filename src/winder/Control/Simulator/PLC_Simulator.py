###############################################################################
# Name: PLC_Simulator.py
# Uses: Simulate the PLC control logic.
# Date: 2016-02-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
from Simulator.SimulationTime import SimulationTime
from Simulator.SimulatedMotor import SimulatedMotor
from Simulator.Delay import Delay

from Machine.MachineGeometry import MachineGeometry

class PLC_Simulator :

  # Error margin (in mm) to allow position (for simulated jitter).
  POSITION_ERROR = 2

  # Error (in mm/s) to allow in velocity (for simulated jitter).
  VELOCITY_ERROR = 0.1

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

    def speedCheck( axis, last ) :

      speed = axis.getSpeedTag()

      # Speed change?
      if last != speed :
        # Speed of 0 means stop request.
        if 0 == speed :
          axis.stop()
        else:
          # $$$FUTURE - Modify speed
          pass

      return speed

    # Look for speed changes on both X and Y, and propagate these to the
    # axies.
    xySpeed = self._io.plc.getTag( self._maxXY_VelocityTag )
    if self._lastXY_Speed != xySpeed :
      self._xAxis.setSpeedTag( xySpeed )
      self._yAxis.setSpeedTag( xySpeed )
      self._lastXY_Speed = xySpeed

    # Check for speed changes on each axis.
    self._lastX_Speed = speedCheck( self._xAxis, self._lastX_Speed )
    self._lastY_Speed = speedCheck( self._yAxis, self._lastY_Speed )
    self._lastZ_Speed = speedCheck( self._zAxis, self._lastZ_Speed )

    moveType = self._io.plc.getTag( self._moveTypeTag )
    if self._lastMoveType != moveType :
      # Reset?
      if self._io.plcLogic.MoveTypes.RESET == moveType :
        self._xAxis.hardStop()
        self._yAxis.hardStop()
        self._zAxis.hardStop()
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.READY )

      # Seek in X/Y?
      elif self._io.plcLogic.MoveTypes.SEEK_XY == moveType :
        # Start with the linear distance to travel.
        xDelta = abs( self._xAxis.positionDelta() )
        yDelta = abs( self._yAxis.positionDelta() )
        delta = math.sqrt( xDelta**2 + yDelta**2 )

        # Calculate the ratio of total distance handled by each axis.
        # Each of the limits must be scaled by this ratio such that the
        # magnitude of each limit is divided evenly amongst both axises.
        if 0 != delta :
          xRatio = xDelta / delta
          yRatio = yDelta / delta
        else:
          xRatio = 0
          yRatio = 0

        # Calculate the limiting velocity for X/Y.
        velocity = self._io.plc.getTag( self._maxXY_VelocityTag )
        xVelocity = velocity * xRatio
        yVelocity = velocity * yRatio

        # Calculate the limiting acceleration for X/Y.
        acceleration = self._io.plc.getTag( self._maxXY_AccelerationTag )
        xAcceleration = acceleration * xRatio
        yAcceleration = acceleration * yRatio

        # Calculate the limiting deceleration for X/Y.
        deceleration = self._io.plc.getTag( self._maxXY_DecelerationTag )
        xDeceleration = deceleration * xRatio
        yDeceleration = deceleration * yRatio

        # Move axises at their respective ratios.
        self._xAxis.startSeek( xVelocity, xAcceleration, xDeceleration )
        self._yAxis.startSeek( yVelocity, yAcceleration, yDeceleration )

        # Change state to moving.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.XY_SEEK )
      # Jog in X/Y?
      elif self._io.plcLogic.MoveTypes.JOG_XY == moveType :
        velocity = self._io.plc.getTag( self._maxXY_VelocityTag )
        acceleration = self._io.plc.getTag( self._maxXY_AccelerationTag )
        deceleration = self._io.plc.getTag( self._maxXY_DecelerationTag )
        self._xAxis.startJog( acceleration, deceleration )
        self._yAxis.startJog( acceleration, deceleration )
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
        acceleration = self._io.plc.getTag( self._maxZ_AccelerationTag )
        deceleration = self._io.plc.getTag( self._maxZ_DecelerationTag )
        self._zAxis.startJog( acceleration, deceleration )
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.Z_JOG )

      # Change latch?
      elif self._io.plcLogic.MoveTypes.LATCH == moveType :
        # Change latch position.
        # (Currently change is instantaneous.)
        latchPosition = self._io.plc.getTag( self._actuatorPosition ) + 1
        if latchPosition > self.LatchPosition.BOTTOM :
          latchPosition = 0

        self._io.plc.write( self._actuatorPosition, latchPosition )

        # State is now latching.
        self._io.plc.write( self._stateTag, self._io.plcLogic.States.LATCHING )

        # Wait 1/2 second for transition.
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
        if   ( ( velocity + self.VELOCITY_ERROR ) < 0 and position < positionMin ) \
          or ( ( velocity - self.VELOCITY_ERROR ) > 0 and position > positionMax ) :

          print axisIO.getName(), "out of range", positionMin, "<=", position, "<=", positionMax

          # Change to an error state.
          self._io.plc.write( self._stateTag, self._io.plcLogic.States.ERROR )

          # Stop all motion.
          self._xAxis.hardStop()
          self._yAxis.hardStop()
          self._zAxis.hardStop()

    # Verify that all axis potions are within limits.
    verifyPositionLimits( self._xAxis, self._io.xAxis, self._xMin, self._xMax )
    verifyPositionLimits( self._yAxis, self._io.yAxis, self._yMin, self._yMax )
    verifyPositionLimits( self._zAxis, self._io.zAxis, self._zMin, self._zMax )

    #
    # Simulate inputs based on machine state.
    #

    # Extended and retracted inputs.
    isExtended = ( self._io.zAxis.getPosition() >= self._machineGeometry.zTravel - self.POSITION_ERROR )
    isRetected = ( self._io.zAxis.getPosition() <= 0 + self.POSITION_ERROR )
    self.Z_Extended.set( isExtended )
    self.Z_Retracted_1A.set( isRetected )

    # End-of-travels.
    if self._io.zAxis.getPosition() > self._zMax \
      or self._io.zAxis.getPosition() < self._zMin :
      self.Z_End_of_Travel.set( True )
    else :
      self.Z_End_of_Travel.set( False )

    # Latch and present sensors.
    latchPosition = self._io.plc.getTag( self._actuatorPosition )
    if latchPosition == self.LatchPosition.TOP :
      self.Z_Fixed_Latched.set( True )
      self.Z_Stage_Latched.set( False )
      self.Latch_Actuator_Top.set( True )
      self.Latch_Actuator_Mid.set( True )
      self.Z_Stage_Present.set( isExtended )
      self.Z_Fixed_Present.set( True )
    elif latchPosition == self.LatchPosition.MIDDLE :
      self.Z_Fixed_Latched.set( True )
      self.Z_Stage_Latched.set( False )
      self.Latch_Actuator_Top.set( False )
      self.Latch_Actuator_Mid.set( True )
      self.Z_Stage_Present.set( isExtended )
      self.Z_Stage_Present.set( isExtended )
    elif latchPosition == self.LatchPosition.BOTTOM :
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
  def __init__( self, io, systemTime ) :
    """
    Construct.

    Args:
      io - Instance of I/O map.
    """
    self._io = io

    # Simulation time.
    # (So we could run at speeds other than real-time.)
    self._simulationTime = systemTime

    # Add self to I/O polling callback list.
    io.pollCallbacks.insert( 0, self.poll )

    # Simulated motors.
    self._xAxis = SimulatedMotor( io.plc, "X", self._simulationTime )
    self._yAxis = SimulatedMotor( io.plc, "Y", self._simulationTime )
    self._zAxis = SimulatedMotor( io.plc, "Z", self._simulationTime )

    # Tags for top-level PLC control.
    self._actuatorPosition   = io.plc.setupTag( "actuator_pos", io.plcLogic.LatchPosition.DOWN )
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
    self._lastX_Speed = None
    self._lastY_Speed = None
    self._lastZ_Speed = None

    self._latchDelay = Delay( self._simulationTime )

    self._machineGeometry = MachineGeometry()

    self._xMin = self._machineGeometry.limitLeft - self.POSITION_ERROR
    self._xMax = self._machineGeometry.limitRight + self.POSITION_ERROR
    self._yMin = self._machineGeometry.limitBottom - self.POSITION_ERROR
    self._yMax = self._machineGeometry.limitTop + self.POSITION_ERROR
    self._zMin = self._machineGeometry.limitRetracted - self.POSITION_ERROR
    self._zMax = self._machineGeometry.limitExtended + self.POSITION_ERROR

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

    # True to use real-time for simulations, False for using a time delta.
    self._realTime = True

    # When '_realTime' is False, use this time delta between ticks.
    self._timeDelta = 100
