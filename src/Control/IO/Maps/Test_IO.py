###############################################################################
# Name: Test_IO.py
# Uses: Map of I/O used by test hardware.
# Date: 2016-02-23
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-23 - QUE - Creation.
# Notes:
#   This I/O map is for the borrowed test hardware demo unit.
###############################################################################
from IO.Devices.ControllogixPLC import ControllogixPLC
from IO.Types.PLC_Input import PLC_Input
from IO.Types.PLC_Output import PLC_Output
from IO.Types.PLC_Motor import PLC_Motor

from IO.Types.SoftwareInput import SoftwareInput
from IO.Types.SoftwareMotor import SoftwareMotor

from IO.Systems.MultiAxisMotor import MultiAxisMotor
from IO.Systems.PLC_Logic import PLC_Logic

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
    self.plcLogic.poll()

  #---------------------------------------------------------------------
  def __init__( self, plcAddress ) :
    """
    Constructor.
    """
    self.count = 0
    self.simulationTime = SimulationTime()

    self.plc = ControllogixPLC( plcAddress )

    self.estop = PLC_Input( "estop", self.plc, "Point_IO:1:I", 0, True )
    self.park  = PLC_Input( "park", self.plc, "Point_IO:1:I", 1 )

    self.xAxis = PLC_Motor( "xAxis", self.plc, "X" )
    self.yAxis = PLC_Motor( "yAxis", self.plc, "Y" )
    self.zAxis = SoftwareMotor( "zAxis", self.simulationTime )

    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    self.plcLogic = PLC_Logic( self.plc, self.xyAxis )

    #
    # $$$DEBUG - All I/O below this line is temporary.
    # $$$DEBUG - NOTE: There should be no reason to have tags in the I/O
    #   map.  Tags should only be in used with-in the I/O package.
    #
    self.start = SoftwareInput( "start" )
    self.stop  = SoftwareInput( "stop" )

    self.debugLight = PLC_Output( "BLINKY", self.plc, "BLINKY" )

# end class
