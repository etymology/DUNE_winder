###############################################################################
# Name: Test_IO.py
# Uses: Map of I/O used by test hardware.
# Date: 2016-02-23
# Author(s):
#   Andrew Que <aque@bb7.com>
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
    """
    Check to see that all hardware is functional.

    Returns:
      True if all hardware is functional, False for any error.
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
    Update inputs.  Call periodically.
    """
    self.plcLogic.poll()

  #---------------------------------------------------------------------
  def __init__( self, plcAddress ) :
    """
    Constructor.
    """
    self.simulationTime = SimulationTime()

    self.plc = ControllogixPLC( plcAddress )

    self.xAxis = PLC_Motor( "xAxis", self.plc, "X" )
    self.yAxis = PLC_Motor( "yAxis", self.plc, "Y" )
    self.zAxis = SoftwareMotor( "zAxis", self.simulationTime )

    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    self.plcLogic = PLC_Logic( self.plc, self.xyAxis )

    #
    # Inputs
    # NOTE: Most of these inputs do not exist on the test hardware fixture.
    #

    self.estop = PLC_Input( "estop", self.plc, "Point_IO:1:I", 0, True )

    # End of travel sensors.
    self.endOfTravelPositiveX = PLC_Input( "endOfTravelX+", self.plc, "Point_IO:2:I", 0 )
    self.endOfTravelNegativeX = PLC_Input( "endOfTravelX-", self.plc, "Point_IO:2:I", 1 )
    self.endOfTravelPositiveY = PLC_Input( "endOfTravelY+", self.plc, "Point_IO:2:I", 2 )
    self.endOfTravelNegativeY = PLC_Input( "endOfTravelY-", self.plc, "Point_IO:2:I", 3 )
    self.endOfTravelPositiveZ = PLC_Input( "endOfTravelZ+", self.plc, "Point_IO:2:I", 4 )
    self.endOfTravelNegativeZ = PLC_Input( "endOfTravelZ-", self.plc, "Point_IO:2:I", 5 )

    # Transfer sensors.
    self.park      = PLC_Input( "park",      self.plc, "Point_IO:1:I", 1 )
    self.xTransfer = PLC_Input( "xTransfer", self.plc, "Point_IO:1:I", 2 )
    self.yTransfer = PLC_Input( "yTransfer", self.plc, "Point_IO:1:I", 3 )
    self.yMount    = PLC_Input( "yMount",    self.plc, "Point_IO:1:I", 4 )

    # Z-Control
    self.zExtended    = PLC_Input( "zExtended",    self.plc, "Point_IO:1:I", 5 )
    self.zRetract1    = PLC_Input( "zRetract1",    self.plc, "Point_IO:1:I", 6 )
    self.zRetract2    = PLC_Input( "zRetract2",    self.plc, "Point_IO:1:I", 7 )
    self.zLatch       = PLC_Input( "zLatch",       self.plc, "Point_IO:1:I", 8 )
    self.zCompensator = PLC_Input( "zCompensator", self.plc, "Point_IO:1:I", 9 )
    self.zFixedLatch  = PLC_Input( "zFixedLatch",  self.plc, "Point_IO:1:I", 10 )
    self.zFixedSense  = PLC_Input( "zFixedSense",  self.plc, "Point_IO:1:I", 11 )


    #
    # $$$DEBUG - All I/O below this line is temporary.
    # $$$DEBUG - NOTE: There should be no reason to have tags in the I/O
    #   map.  Tags should only be in used with-in the I/O package.
    #

    self.debugLight = PLC_Output( "BLINKY", self.plc, "BLINKY" )

# end class
