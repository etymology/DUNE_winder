###############################################################################
# Name: WindMode.py
# Uses: Main control mode for winding process.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
###############################################################################

#from IO.IO import self.io.
#from Library.GCode import GCode
#from Control.GCodeHandler import GCodeHandler
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
    self._temp = 0   # $$$DEBUG

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Function called when entering this state.

    Returns:
      True if there was an error, false if not.
    """
    isError = False

    if self.io.stop.get() :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because stop is still requested."
      )

    if None == self.stateMachine.gCodeHandler or None == self.stateMachine.gCodeHandler.gCode :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because no there is no G-Code file loaded to execute."
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

    # We didn't finish this line.  Run it again.
    self.stateMachine.gCodeHandler.gCode.setRelativeLine( -1 )

    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """

    # If ESTOP or I/O isn't ready...
    if self.io.estop.get() :
      self.changeState( self.stateMachine.States.STOP )
    #elif self.io.stop.get() :
    elif self.stateMachine.stopRequest :
      # We didn't finish this line.  Run it again.
      self.io.plcLogic.stopXY()
      self.changeState( self.stateMachine.States.STOP )
      self.stateMachine.stopRequest = False
    else:
      # Done moving?
      if self.io.plcLogic.isXY_SeekComplete() :

        # Done with G-Code script?
        if self.stateMachine.gCodeHandler.isDone() :
          self.stateMachine.gCodeHandler.gCode.rewind()
          self.log.add(
            self.__class__.__name__,
            "WIND",
            "G-Code execution complete"
          )

          self.changeState( self.stateMachine.States.STOP )
        else :
          self._temp += 1
          if 5 == self._temp :
            self.stateMachine.gCodeHandler.runNextLine()
            self._temp = 0

