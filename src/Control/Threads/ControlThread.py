#==============================================================================
# Name: ControlThread.py
# Uses: Primary system control thread.  Loop runs master state machine.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-04 - QUE - Creation.
#==============================================================================
from PrimaryThread import PrimaryThread
from Control.ControlStateMachine import ControlStateMachine

import time  # $$$DEBUG

class ControlThread( PrimaryThread ) :

  #---------------------------------------------------------------------
  def __init__( self, stateMachine ) :
    """
    Constructor.

    """

    PrimaryThread.__init__( self, "ControlThread" )
    self.stateMachine = stateMachine

  #---------------------------------------------------------------------
  def run( self ) :
    """
    Body of thread. $$$DEBUG

    """


    while PrimaryThread.isRunning :
      self.stateMachine.update()

      # $$$DEBUG - This should be a wait for an I/O event.
      time.sleep( 0.1 )

# end class
