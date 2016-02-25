#==============================================================================
# Name: Test_IO.py
# Uses: Map of I/O used by test hardware.
# Date: 2016-02-23
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-23 - QUE - Creation.
# Notes:
#   This I/O map is for the borrowed test hardware demo unit.
#==============================================================================
from IO.Devices.AB_PLC import AB_PLC
from IO.Types.AB_Input import AB_Input
from IO.Types.AB_Motor import AB_Motor
from IO.Types.AB_Tag import AB_Tag

from IO.Types.SoftwareInput import SoftwareInput
from IO.Types.SoftwareMotor import SoftwareMotor
from IO.Systems.MultiAxisMotor import MultiAxisMotor

from Simulator.SimulationTime import SimulationTime

class Test_IO:

  #---------------------------------------------------------------------
  def isFunctional( self ) :
    """$$$DEBUG
    """
    result = True
    result &= not self.plc.isNotFunctional()
    result &= self.xAxis.isFunctional()
    result &= self.yAxis.isFunctional()
    result &= self.zAxis.isFunctional()

    return result

  #---------------------------------------------------------------------
  def pollInputs( self ) :
    """
    $$$DEBUG
    """
    AB_Input.pollAll()
    AB_Motor.pollAll()
    self.state.poll()

    # self.count += 1
    # if 20 == self.count :
    #   self.xAxis.setVelocity( 1.0 )
    #   self.moveType.set( 1 )
    #
    # if 30 == self.count :
    #   self.xAxis.setVelocity( 0.0 )
    #   self.count = 0
    #
    #
    # self.dummy.set( self.count )

  #---------------------------------------------------------------------
  def __init__( self, plcAddress ) :
    """
    Constructor.
    """
    self.count = 0
    self.simulationTime = SimulationTime()

    self.plc = AB_PLC( plcAddress )

    self.estop = AB_Input( "estop", self.plc, "Point_IO:1:I", 0, True )
    self.park  = AB_Input( "park", self.plc, "Point_IO:1:I", 1 )

    self.xAxis = AB_Motor( "xAxis", self.plc, "X" )
    self.yAxis = AB_Motor( "yAxis", self.plc, "Y" )
    self.zAxis = SoftwareMotor( "zAxis", self.simulationTime )

    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    self.start = SoftwareInput( "start" )
    self.stop  = SoftwareInput( "stop" )
    #AB_Input( "start", self.plc, "Point_IO:3:I.Data", 0 )

    #self.position = AB_Tag( "X/Y Position", self.plc, "MOVE_TYPE", type="INT" )
    self.moveType = AB_Tag( "Move type", self.plc, "MOVE_TYPE", tagType="INT" )
    self.state    = AB_Tag( "State", self.plc, "STATE", tagType="DINT" )
    self.maxVelocity     = AB_Tag( "MaxVelocity", self.plc, "XY_MAX_VELOCITY", tagType="REAL" )
    self.maxAcceleration = AB_Tag( "MaxAcceleration", self.plc, "XY_MAX_ACCELERATION", tagType="REAL" )
    self.maxDeceleration = AB_Tag( "MaxDeceleration", self.plc, "XY_MAX_DECELERATION", tagType="REAL" )

    self.dummy = AB_Tag( "Dummy", self.plc, "DUMMY", tagType="DINT" )
    self.blinky = AB_Tag( "BLINKY", self.plc, "BLINKY", tagType="BOOL" )

    #

# end class
