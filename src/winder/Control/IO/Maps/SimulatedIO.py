###############################################################################
# Name: SimulatedIO.py
# Uses: Map of I/O used by simulator.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   This is the I/O map for the machine simulator.  It should contain the same
#   variables as the main I/O map, but using software I/O instead of actual
#   I/O.
###############################################################################
from IO.Devices.SimulatedPLC import SimulatedPLC

from IO.Types.PLC_Input import PLC_Input
from IO.Types.PLC_Output import PLC_Output
from IO.Types.PLC_Motor import PLC_Motor

from IO.Systems.MultiAxisMotor import MultiAxisMotor
from IO.Systems.PLC_Logic import PLC_Logic

from Simulator.SimulationTime import SimulationTime

class SimulatedIO:
  #---------------------------------------------------------------------
  def isFunctional( self ) :
    """
    Check to see that all hardware is functional.

    Returns:
      True if all hardware is functional, False for any error.
    """

    # Simulator currently does not implement failing hardware.
    return True

  #---------------------------------------------------------------------
  def pollInputs( self ) :
    """
    Update inputs.  Call periodically.
    """

    for callback in self.pollCallbacks :
      callback()

    self.plcLogic.poll()

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.  This function should be kept as similar to production
    hardware as possible.
    """

    self.pollCallbacks = []

    self.simulationTime = SimulationTime()

    #self.plc = ControllogixPLC( plcAddress )
    self.plc = SimulatedPLC( "PLC" )

    self.estop = PLC_Input( "estop", self.plc, "Point_IO:1:I", 0, True )
    self.park  = PLC_Input( "park", self.plc, "Point_IO:1:I", 1 )

    self.xAxis = PLC_Motor( "xAxis", self.plc, "X" )
    self.yAxis = PLC_Motor( "yAxis", self.plc, "Y" )
    self.zAxis = PLC_Motor( "zAxis", self.plc, "Z" )

    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    self.plcLogic = PLC_Logic( self.plc, self.xyAxis, self.zAxis )

    #
    # $$$DEBUG - All I/O below this line is temporary.
    #

    self.debugLight = PLC_Output( "BLINKY", self.plc, "BLINKY" )

# end class
