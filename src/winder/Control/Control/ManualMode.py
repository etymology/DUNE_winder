###############################################################################
# Name: ManualMode.py
# Uses: Update function for manual mode.
# Date: 2016-02-16
# Author(s):
#   Andrew Que <aque@bb7.com>
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
    self._wasJoggingXY = False
    #self._wasSeekingXY = False
    self._noteSeekStop = False

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Enter into manual mode.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    isError = True

    self._wasJoggingXY = False
    self._noteSeekStop = False

    # X/Y axis move?
    if None != self.stateMachine.seekX or None != self.stateMachine.seekY :

      x = self.stateMachine.seekX
      if None == x :
        x = self._io.xAxis.getPosition()

      y = self.stateMachine.seekY
      if None == y :
        y = self._io.yAxis.getPosition()

      self._io.plcLogic.setXY_Position( x, y, self.stateMachine.seekVelocity )
      self.stateMachine.seekX = None
      self.stateMachine.seekY = None
      self.stateMachine.seekVelocity = None
      #self._wasSeekingXY = True
      isError = False

    if self.stateMachine.isJogging :
      self._wasJoggingXY = True
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

    # If stop requested...
    if self.stateMachine.stopRequest :
      # We didn't finish this line.  Run it again.
      self._io.plcLogic.stopSeek()
      self._log.add(
        self.__class__.__name__,
        "SEEK_STOP",
        "Seek stop requested"
      )
      self._noteSeekStop = True
      self.stateMachine.stopRequest = False

    # Is movement done?
    if self._io.plcLogic.isReady() \
      and not self.stateMachine.isJogging :

      # If we were seeking X/Y axis, note where stopped.
      if self._noteSeekStop :
        x = self._io.xAxis.getPosition()
        y = self._io.yAxis.getPosition()
        self._log.add(
          self.__class__.__name__,
          "SEEK_STOP_LOCATION",
          "X/Y seek stopped at (" + str( x ) + "," + str( y ) + ")",
          [ x, y ]
        )

      # If we were jogging X/Y axis, note where stopped.
      if self._wasJoggingXY :
        x = self._io.xAxis.getPosition()
        y = self._io.yAxis.getPosition()
        self._log.add(
          self.__class__.__name__,
          "JOG_STOP",
          "X/Y jog stopped at (" + str( x ) + "," + str( y ) + ")",
          [ x, y ]
        )

      self.changeState( self.stateMachine.States.STOP )


#end class