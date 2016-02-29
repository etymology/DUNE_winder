###############################################################################
# Name: ControlThread.py
# Uses: Primary system control thread.  Loop runs master state machine.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-04 - QUE - Creation.
###############################################################################
from Control.Settings import Settings
from PrimaryThread import PrimaryThread

import time

class ControlThread( PrimaryThread ) :

  #---------------------------------------------------------------------
  def __init__( self, io, stateMachine ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      stateMachine: Instance of state machine.
    """

    PrimaryThread.__init__( self, "ControlThread" )
    self.io = io
    self.stateMachine = stateMachine

  #---------------------------------------------------------------------
  def run( self ) :
    """
    Body of control thread--the "main loop" of the program.
    """
    while PrimaryThread.isRunning :

      self.io.pollInputs()
      self.stateMachine.update()

      # Wait before updating again.
      time.sleep( Settings.IO_UPDATE_TIME )

# end class
