###############################################################################
# Name: SimulatedIO.py
# Uses: Map of I/O used by simulator.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
# Notes:
#   This is the I/O map for the machine simulator.  It should contain the same
#   variables as the main I/O map, but using software I/O instead of actual
#   I/O.
###############################################################################
from IO.Devices.SimulatedPLC import SimulatedPLC
from IO.Types.SoftwareInput import SoftwareInput
from IO.Types.SoftwareMotor import SoftwareMotor
from IO.Types.SoftwareTag import SoftwareTag
from IO.Systems.MultiAxisMotor import MultiAxisMotor
from Simulator.SimulationTime import SimulationTime

class SimulatedIO:
  #---------------------------------------------------------------------
  def isFunctional( self ) :
    """
    $$$DEBUG
    """

    #Motor.pollAll()

    return True

  #---------------------------------------------------------------------
  def pollInputs( self ) :
    """$$$DEBUG
    """
    pass

  def __init__( self ) :
    """$$$DEBUG"""

    self.simulationTime = SimulationTime()

    self.plc = SimulatedPLC()

    self.estop = SoftwareInput( "estop" )
    self.park  = SoftwareInput( "park" )

    self.xAxis = SoftwareMotor( "xAxis", self.simulationTime )
    self.yAxis = SoftwareMotor( "yAxis", self.simulationTime )
    self.zAxis = SoftwareMotor( "zAxis", self.simulationTime )

    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    self.start = SoftwareInput( "start" )
    self.stop  = SoftwareInput( "stop" )

    self.moveType = SoftwareTag( "Move type", self.plc, "MOVE_TYPE", tagType="INT" )
    self.state    = SoftwareTag( "State", self.plc, "STATE", tagType="DINT" )
    self.maxVelocity     = SoftwareTag( "MaxVelocity", self.plc, "XY_MAX_VELOCITY", tagType="REAL" )
    self.maxAcceleration = SoftwareTag( "MaxAcceleration", self.plc, "XY_MAX_ACCELERATION", tagType="REAL" )
    self.maxDeceleration = SoftwareTag( "MaxDeceleration", self.plc, "XY_MAX_DECELERATION", tagType="REAL" )
    self.dummy  = SoftwareTag( "Dummy", self.plc, "DUMMY", tagType="DINT" )
    self.blinky = SoftwareTag( "BLINKY", self.plc, "BLINKY", tagType="BOOL" )

# end class
