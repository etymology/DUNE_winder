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
  def __init__( self, stateMachine, state, io, log, gCodeHandler ) :
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
    self.gCodeHandler = gCodeHandler
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

    if None == self.gCodeHandler.gCode :
      isError = True
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "Wind cannot start because no there is no G-Code file loaded to execute."
      )

    if not isError :
      self.log.add(
        self.__class__.__name__,
        "WIND",
        "G-Code execution of "
          + self.gCodeHandler.gCode.fileName
          + " begins at line "
          + str( self.gCodeHandler.gCode.getLine() ),
        [ self.gCodeHandler.gCode.fileName, self.gCodeHandler.gCode.getLine() ]
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
    self.gCodeHandler.gCode.setRelativeLine( -1 )

    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """


    # If ESTOP or I/O isn't ready...
    if self.io.estop.get() :
      self.changeState( self.stateMachine.States.STOP )
    elif self.io.stop.get() :
      # We didn't finish this line.  Run it again.
      self.io.plcLogic.stopXY()
      self.changeState( self.stateMachine.States.STOP )
    else:
      # Done moving?
      if self.io.plcLogic.isXY_SeekComplete() :

        # Done with G-Code script?
        if self.gCodeHandler.isDone() :
          self.gCodeHandler.gCode.rewind()
          self.log.add(
            self.__class__.__name__,
            "WIND",
            "G-Code execution complete"
          )

          self.changeState( self.stateMachine.States.STOP )
        else :
          self._temp += 1
          if 2 == self._temp :
            self.gCodeHandler.runNextLine()
            self._temp = 0

