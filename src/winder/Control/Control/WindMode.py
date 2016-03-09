###############################################################################
# Name: WindMode.py
# Uses: Main control mode for winding process.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.StateMachineState import StateMachineState

class WindMode( StateMachineState ) :

  #---------------------------------------------------------------------
  def __init__( self, stateMachine, state, io, log ) :
    """
    Constructor.

    Args:
      stateMachine: Parent state machine.
      state: Integer representation of state.
      io: Instance of I/O map.
      gCodeHandler: Instance of G-Code handler.
    """

    StateMachineState.__init__( self, stateMachine, state )
    self.io = io
    self.log = log
    self._PAUSE = 0         # $$$DEBUG
    self._pauseCount = 0   # $$$DEBUG

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Function called when entering this state.

    Returns:
      True if there was an error, false if not.
    """
    isError = False

    if None == self.stateMachine.gCodeHandler or None == self.stateMachine.gCodeHandler.gCode :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because no there is no G-Code file loaded to execute."
      )

    if not isError and self.stateMachine.gCodeHandler.isOutOfWire() :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because there isn't enough wire on spool."
      )

    if not isError and self.stateMachine.gCodeHandler.isDone() :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because G-Code is finished."
      )

    if not isError :
      self.stateMachine.stopRequest = False
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "G-Code execution begins at line "
          + str( self.stateMachine.gCodeHandler.gCode.getLine() ),
        [ self.stateMachine.gCodeHandler.gCode.getLine() ]
      )

    return isError

  #---------------------------------------------------------------------
  def exit( self ) :
    """
    Function called when exiting this state.

    Returns:
      True if there was an error, false if not.
    """

    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.
    """

    # If stop requested...
    if self.stateMachine.stopRequest :
      # We didn't finish this line.  Run it again.
      self.io.plcLogic.stopSeek()
      self.changeState( self.stateMachine.States.STOP )
      self.stateMachine.stopRequest = False
    else:

      # Update G-Code handler.
      isDone = self.stateMachine.gCodeHandler.poll()

      # Is G-Code execution complete?
      if isDone :
        # Log message that wind is complete.
        self.log.add(
          self.__class__.__name__,
          "WIND",
          "G-Code execution complete"
        )

        if self.stateMachine.loopMode :
          # Rewind.
          self.stateMachine.gCodeHandler.setLine( 0 )
        else :
          # Return to stopped state.
          self.changeState( self.stateMachine.States.STOP )
