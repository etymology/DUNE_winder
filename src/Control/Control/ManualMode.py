#==============================================================================
# Name: ManualMode.py
# Uses: Update function for manual mode.
# Date: 2016-02-16
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-16 - QUE - Creation.
#==============================================================================

#from IO.IO import self.io.
from Library.StateMachineState import StateMachineState

class ManualMode( StateMachineState ) :

  #---------------------------------------------------------------------
  def __init__( self, stateMachine, state, io, manualCommand ) :
    """
    Constructor.

    Args:
      stateMachine: Parent state machine.
      state: Integer representation of state.
      self.io.: Instance of I/O map.
      manualCommand: Instance of Control.ManualCommand
    """

    StateMachineState.__init__( self, stateMachine, state )
    self.io = io
    self.manualCommand = manualCommand

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Enter into manual mode.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    result = False

    # Cannot switch into manual mode if no request has been made.
    if not self.manualCommand.isManualRequest :
      result = True
    else:
      #
      # Seek to the requested location.  Resets seek positions.
      #
      if self.manualCommand.seekX :
        self.io.xAxis.setDesiredPosition( self.manualCommand.seekX )
        self.manualCommand.seekX = None

      if self.manualCommand.seekY :
        self.io.yAxis.setDesiredPosition( self.manualCommand.seekY )
        self.manualCommand.seekY = None

      if self.manualCommand.seekZ :
        self.io.zAxis.setDesiredPosition( self.manualCommand.seekZ )
        self.manualCommand.seekZ = None

    return result

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """

    # Is movement done?
    if not self.io.xyAxis.isSeeking() and not self.io.zAxisisSeeking() :
      self.changeState( self.stateMachine.States.STOP )


#end class