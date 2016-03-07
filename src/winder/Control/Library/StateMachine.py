###############################################################################
# Name: StateMachine.py
# Uses: Template of a state machine.
# Date: 2016-02-10
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
class StateMachine :
  #---------------------------------------------------------------------
  def __init__( self, name = None ) :
    """
    Constructor.

    Args:
      name: A name for the state machine (optional).

    """


    if None == name :
      name = self.__class__.__name__

    self.name = name

    self.state = None
    self.states = {}

  #---------------------------------------------------------------------
  def getState( self ) :
    """
    Return the state (as a number).

    Returns:
      Current state (as number).  -1 for uninitialized state.
    """
    result = -1
    if self.state :
      result = (key for key,value in self.states.items() if value==self.state).next()

    return result

  #---------------------------------------------------------------------
  def changeState( self, newState ) :
    """
    Transition to a new state.

    Args:
      newState: The state to transition into.

    Returns:
      True if there was an error, false if not.
    """


    newState = self.states[ newState ]
    isError = newState.enter()

    if not isError :
      # Exit from the previous state (if it exists).
      if self.state :
        isError = self.state.exit()

      # Change to this state.
      if not isError :
        self.state = newState

    return isError

  #---------------------------------------------------------------------
  def addState( self, state, index ) :
    """
    Add a new state to the state machine. Called as part of the initialization process.

    Args:
      state: A 'StateMachineMode' to include.
      index: A number to represent this state.

    """

    self.states[ index ] = state

  #---------------------------------------------------------------------
  def update( self ) :
    """
    Update the state machine logic. Call periodically.

    """

    if self.state :
      self.state.update()
