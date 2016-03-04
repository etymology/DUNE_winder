###############################################################################
# Name: ManualMode.py
# Uses: Update function for manual mode.
# Date: 2016-02-16
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-16 - QUE - Creation.
###############################################################################

from Library.StateMachineState import StateMachineState

class ManualMode( StateMachineState ) :

  #---------------------------------------------------------------------
  def __init__( self, stateMachine, state, io, log ) :
    """
    Constructor.

    Args:
      stateMachine: Parent state machine.
      state: Integer representation of state.
      io: Instance of I/O map.
      manualCommand: Instance of Control.ManualCommand
    """

    StateMachineState.__init__( self, stateMachine, state )
    self._io   = io
    self._log  = log
    self._jogX = 0
    self._jogY = 0
    self._jogZ = 0

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Enter into manual mode.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    isError = True

    # X/Y axis move?
    if None != self.stateMachine.seekX or None != self.stateMachine.seekY :

      x = self.stateMachine.seekX
      if None == x :
        x = self._io.xAxis.getPosition()

      y = self.stateMachine.seekX
      if None == y :
        y = self._io.yAxis.getPosition()

      self._io.plcLogic.setXY_Position( x, y, self.stateMachine.seekVelocity )
      self.stateMachine.seekX = None
      self.stateMachine.seekY = None
      self.stateMachine.seekVelocity = None
      isError = False

    if self.stateMachine.isJogging :
      isError = False

    if None != self.stateMachine.seekZ :
      self._io.zAxis.setDesiredPosition( self.stateMachine.seekZ )
      self.stateMachine.seekZ = None
      isError = False

    return isError

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """

    # Is movement done?
    if not self._io.xyAxis.isSeeking()   \
      and not self._io.zAxis.isSeeking() \
      and not self.stateMachine.isJogging :
        self.changeState( self.stateMachine.States.STOP )


#end class