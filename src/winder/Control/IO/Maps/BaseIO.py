###############################################################################
# Name: BaseIO.py
# Uses: Base map of I/O used by all hardware with only PLC undefined.
# Date: 2016-04-21
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from IO.Types.PLC_Input import PLC_Input
from IO.Types.PLC_Output import PLC_Output
from IO.Types.PLC_Motor import PLC_Motor

from IO.Systems.MultiAxisMotor import MultiAxisMotor
from IO.Systems.PLC_Logic import PLC_Logic
from IO.Systems.Head import Head

class BaseIO:

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
    result &= not self.plcLogic.isError()

    return result

  #---------------------------------------------------------------------
  def pollInputs( self ) :
    """
    Update inputs.  Call periodically.
    """

    # Run each callback in list.
    # (Allows I/O to sign up to have a periodic update callback.)
    for callback in self.pollCallbacks :
      callback()

  #---------------------------------------------------------------------
  def __init__( self, plc ) :
    """
    Constructor.
    """

    # List of callbacks that update I/O.
    self.pollCallbacks = []

    # Use the PLC passed in.
    self.plc = plc

    # Individual axises.
    self.xAxis = PLC_Motor( "xAxis", self.plc, "X" )
    self.yAxis = PLC_Motor( "yAxis", self.plc, "Y" )
    self.zAxis = PLC_Motor( "zAxis", self.plc, "Z" )

    # X/Y treated together.
    self.xyAxis = MultiAxisMotor( "xyAxis", [ self.xAxis, self.yAxis ] )

    # PLC logic system, including its polling.
    self.plcLogic = PLC_Logic( self.plc, self.xyAxis, self.zAxis )
    self.pollCallbacks.append( self.plcLogic.poll )
    self.head = Head( self.plcLogic )

    #
    # Inputs
    # NOTE: Most of these inputs do not exist on the test hardware fixture.
    #

    # $$$DEBUG - Restore default to True
    self.estop = PLC_Input( "estop", self.plc, "Point_IO:1:I", 0, False )
    self.park  = PLC_Input( "park",  self.plc, "Point_IO:1:I", 1 )

    # Z-Stage sensors.
    self.Latch_Homed          = PLC_Input( "Latch_Homed",        self.plc, "Machine_SW_Stat", 0 )
    self.Z_Retracted_1A       = PLC_Input( "Z_Retracted_1A",     self.plc, "Machine_SW_Stat", 1 )
    self.Z_Retracted_2B       = PLC_Input( "Z_Retracted_2B",     self.plc, "Machine_SW_Stat", 2 )
    self.Z_Retracted_2A       = PLC_Input( "Z_Retracted_2A",     self.plc, "Machine_SW_Stat", 3 )
    self.Z_Retracted_2B       = PLC_Input( "Z_Retracted_2B",     self.plc, "Machine_SW_Stat", 4 )
    self.Z_Extended           = PLC_Input( "Z_Extended",         self.plc, "Machine_SW_Stat", 5 )
    self.Z_Stage_Latched      = PLC_Input( "Z_Stage_Latched",    self.plc, "Machine_SW_Stat", 6 )
    self.Z_Fixed_Latched      = PLC_Input( "Z_Fixed_Latched",    self.plc, "Machine_SW_Stat", 7 )
    self.Z_End_of_Travel      = PLC_Input( "Z_End_of_Travel",    self.plc, "Machine_SW_Stat", 8 )
    self.Z_Stage_Present      = PLC_Input( "Z_Stage_Present",    self.plc, "Machine_SW_Stat", 9 )
    self.Z_Fixed_Present      = PLC_Input( "Z_Fixed_Present",    self.plc, "Machine_SW_Stat", 10 )
    self.Z_Spring_Comp        = PLC_Input( "Z_Spring_Comp",      self.plc, "Machine_SW_Stat", 11 )
    self.Latch_Actuator_Top   = PLC_Input( "Latch_Actuator_Top", self.plc, "Machine_SW_Stat", 12 )
    self.Latch_Actuator_Mid   = PLC_Input( "Latch_Actuator_Mid", self.plc, "Machine_SW_Stat", 13 )

# end class
