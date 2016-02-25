#==============================================================================
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
#==============================================================================
from IO.Types.SoftwareInput import SoftwareInput
from IO.Types.SoftwareMotor import SoftwareMotor
from IO.Systems.MultiAxisMotor import MultiAxisMotor
from Simulator.SimulationTime import SimulationTime

class SimulatedIO:

  simulationTime = SimulationTime()

  estop = SoftwareInput( "estop" )
  park  = SoftwareInput( "park" )

  xAxis = SoftwareMotor( "xAxis", simulationTime )
  yAxis = SoftwareMotor( "yAxis", simulationTime )
  zAxis = SoftwareMotor( "zAxis", simulationTime )

  xyAxis = MultiAxisMotor( "xyAxis", [ xAxis, yAxis ] )

  start = SoftwareInput( "start" )


  def pollInputs( self ) :
    pass

# end class
