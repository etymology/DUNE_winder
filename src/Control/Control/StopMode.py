#==============================================================================
# Name: StopMode.py
# Uses: Root state in which there is no machine motion.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================

from IO.IO import io
from Library.StateMachineState import StateMachineState
from Library.LoggedStateMachine import LoggedStateMachine

class StopMode( StateMachineState ) :

  #====================================
  # Idle mode.
  # Idle means the machine isn't moving, but is ready to move.
  #====================================
  class Idle( StateMachineState ) :
    #-------------------------------------------------------------------
    def __init__( self, stateMachine, state, control ) :
      """
      Constructor.

      Args:
        stateMachine: Parent state machine.
        state: Integer representation of state.
        control: Instance of primary control state machine.

      """

      StateMachineState.__init__( self, stateMachine, state )
      self.control = control

    #-------------------------------------------------------------------
    def update( self ) :
      """
      Periodic update function. Checks for critical I/O changes or a request for mode change.

      """

      # Check for E-Stop.
      if io.estop.get() :
        self.changeState( self.stateMachine.States.ESTOP )
      elif io.park.get() :
        self.changeState( self.stateMachine.States.PARK )
      elif io.start.get() :
        self.control.changeState( self.control.States.WIND )
      else:
        #
        # $$$ DEBUG - Allowed to change to other modes.
        #
        pass

  #====================================
  # Emergency stop.
  # Emergency stop is active and machine cannot change into any other mode
  # until this is clear.
  #====================================
  class EStop( StateMachineState ) :
    #-------------------------------------------------------------------
    def __init__( self, stateMachine, state, control ) :
      """
      Constructor.

      Args:
        stateMachine: Parent state machine.
        state: Integer representation of state.
        control: Instance of primary control state machine.

      """

      StateMachineState.__init__( self, stateMachine, state )
      self.control = control

    #-------------------------------------------------------------------
    def update( self ) :
      """
      Periodic update function. Waits for E-Stop to clear.

      """

      # Not allowed to change to other modes until E-Stop is clear.
      if not io.estop.get() :
        self.changeState( self.stateMachine.States.IDLE )

  #====================================
  # Parked.
  # Head is locked in the park position.  Motors are unable to move and
  # mode changes are not allowed until park is clear.  Can switch to ESTOP
  # should that occur.
  #====================================
  class Park( StateMachineState ) :
    #-------------------------------------------------------------------
    def __init__( self, stateMachine, state, control ) :
      """
      Constructor.

      Args:
        stateMachine: Parent state machine.
        state: Integer representation of state.
        control: Instance of primary control state machine.

      """

      StateMachineState.__init__( self, stateMachine, state )
      self.control = control

    #-------------------------------------------------------------------
    def update( self ) :
      """
      Periodic update function. Waits for Park to clear, or E-Stop.

      """

      # Check for E-Stop.
      if io.estop.get() :
        self.changeState( self.stateMachine.States.ESTOP )
      # See if still in park.
      elif not io.park.get() :
        self.changeState( self.stateMachine.States.IDLE )

  #=====================================================================
  # Sub-state machine for stop modes.
  #=====================================================================
  class StopStateMachine( LoggedStateMachine ) :
    class States :
      IDLE  = 0
      ESTOP = 1
      PARK  = 2
    #end class

    #-------------------------------------------------------------------
    def __init__( self, control, log ) :
      """
      Constructor.

      Args:
        control: Instance of primary control state machine.
        log: Log file to write state changes.

      """

      LoggedStateMachine.__init__( self, log )
      StopMode.Idle(  self, self.States.IDLE, control )
      StopMode.EStop( self, self.States.ESTOP, control )
      StopMode.Park(  self, self.States.PARK, control )

      self.changeState( self.States.IDLE )
  #end class

  #---------------------------------------------------------------------
  def __init__( self, stateMachine, state, log ) :
    """
    Constructor.

    Args:
      stateMachine: Parent state machine.
      state: Integer representation of state.
      log: Log file to write state changes.

    """

    StateMachineState.__init__( self, stateMachine, state )

    self.stopStateMachine = self.StopStateMachine( stateMachine, log )

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """

    # Update active sub-state.
    self.stopStateMachine.update()
