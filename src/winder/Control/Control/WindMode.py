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
    self._io = io
    self._log = log
    self._startTime = None
    self._currentLine = 0 

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Function called when entering this state.

    Returns:
      True if there was an error, false if not.
    """
    isError = False

    if None == self.stateMachine.gCodeHandler \
     or not self.stateMachine.gCodeHandler.isG_CodeLoaded() :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because no there is no G-Code file loaded to execute."
      )

    if not isError and self.stateMachine.gCodeHandler.isOutOfWire() :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because there isn't enough wire on spool."
      )

    if not isError and self.stateMachine.gCodeHandler.isDone() :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because G-Code is finished."
      )

    if not isError :
      self._startTime = self.stateMachine.systemTime.get()
      self.stateMachine.windTime = 0
      self.stateMachine.stopRequest = False
      self._log.add(
        self.__class__.__name__,
        "WIND",
        "G-Code execution begins at line "
          + str( self.stateMachine.gCodeHandler.getLine() ),
        [ self.stateMachine.gCodeHandler.getLine() ]
      )

    return isError

  #---------------------------------------------------------------------
  def exit( self ) :
    """
    Function called when exiting this state.

    Returns:
      True if there was an error, false if not.
    """

    self.stateMachine.windTime += \
      self.stateMachine.systemTime.getDelta( self._startTime )

    deltaString = self.stateMachine.systemTime.getElapsedString( self.stateMachine.windTime )

    # Log message that wind is complete.
    self._log.add(
      self.__class__.__name__,
      "WIND_TIME",
      "Wind ran for " + deltaString + ".",
      [ self.stateMachine.windTime ]
    )

    self.stateMachine.gCodeHandler.stop()
    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.
    """
    #Want to print G-Code line
    
    # If stop requested...
    if self.stateMachine.stopRequest :
      # We didn't finish this line.  Run it again.
      self._io.plcLogic.stopSeek()
      self.changeState( self.stateMachine.States.STOP )
      self.stateMachine.stopRequest = False
    else:

      # Update G-Code handler.
      isDone = self.stateMachine.gCodeHandler.poll()

      if self.stateMachine.gCodeHandler.isG_CodeError() :
        # Log message that wind is complete.
        self._log.add(
          self.__class__.__name__,
          "WIND_ERROR",
          "G-Code error.  " + self.stateMachine.gCodeHandler.getG_CodeErrorMessage(),
          self.stateMachine.gCodeHandler.getG_CodeErrorData()
        )

        self.stateMachine.gCodeHandler.clearCodeError()

        isDone = True

      # Is G-Code execution complete?
      if not isDone :
        if self.stateMachine.gCodeHandler.isG_CodeLoaded() :
          line = self.stateMachine.gCodeHandler.getLine()
          if self._currentLine != line :
            # Log message that wind is complete.
            self._log.add(
              self.__class__.__name__,
              "LINE",
              "G-Code executing line N"+str(line), [self._currentLine, line]
             )
          self._currentLine = line


      # Is G-Code execution complete?
      if isDone :
        # Log message that wind is complete.
        self._log.add(
          self.__class__.__name__,
          "WIND",
          "G-Code execution complete"
        )

        if self.stateMachine.loopMode :
          # Rewind.
          self.stateMachine.gCodeHandler.setLine( -1 )
        else :
          # Return to stopped state.
          self.changeState( self.stateMachine.States.STOP )
