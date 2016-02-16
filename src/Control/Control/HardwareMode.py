#==============================================================================
# Name: HardwareMode.py
# Uses: Root state in which the system attempts to connect to hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================

from IO.IO import io
from Library.StateMachineState import StateMachineState

class HardwareMode( StateMachineState ) :
  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """


    #
    # $$$DEBUG - Check that hardware is functional.
    #

    self.changeState( self.stateMachine.States.STOP )
