###############################################################################
# Name: LoggedStateMachine.py
# Uses: A state machine whose transitions are logged.
# Date: 2016-02-10
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################
from .StateMachine import StateMachine

class LoggedStateMachine( StateMachine ) :
  #---------------------------------------------------------------------
  def __init__( self, log ) :
    """
    Constructor.

    Args:
      log: Log file to write transitions.

    """

    StateMachine.__init__( self )
    self.log = log

  #---------------------------------------------------------------------
  def changeState( self, newState ):
    """
    Transition to a new state.

    Args:
      newState: The state to transition into.

    Returns:
      True if there was an error, false if not.
    """


    oldModeName = self.state.__class__.__name__ if self.state else "<None>"
    isError = StateMachine.changeState( self, newState )

    newModeName = "<None>"
    if newState := self.states[newState]:
      newModeName = newState.__class__.__name__

    message = "Failed to change mode from " if isError else "Mode changed from "
    # Log mode change.
    self.log.add(
      self.__class__.__name__,
      "MODE",
        message
        + oldModeName
        + " to "
        + newModeName,
      [ oldModeName, newModeName ]
    )

    return isError
