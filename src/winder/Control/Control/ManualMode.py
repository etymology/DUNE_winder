###############################################################################
# Name: ManualMode.py
# Uses: Update function for manual mode.
# Date: 2016-02-16
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
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
    self._wasJogging = False
    self._wasSeekingZ  = False
    self._noteSeekStop = False

  #---------------------------------------------------------------------
  def enter( self ):
    """
    Enter into manual mode.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    isError = True

    self._wasJogging = False
    self._noteSeekStop = False

    # If executing a G-Code line.
    if self.stateMachine.executeGCode :
      self.stateMachine.executeGCode = False
      isError = False

    # X/Y axis move?
    if self.stateMachine.seekX != None or self.stateMachine.seekY != None:
      isError = self.xySeek()

    if self.stateMachine.isJogging :
      self._wasJogging = True
      isError = False

    if self.stateMachine.seekZ != None:
      self._io.plcLogic.setZ_Position( self.stateMachine.seekZ, self.stateMachine.seekVelocity )
      self.stateMachine.seekZ = None
      isError = False

    # Move the head?
    if self.stateMachine.setHeadPosition != None:
      isError = self._io.head.setPosition(
        self.stateMachine.setHeadPosition,
        self.stateMachine.seekVelocity
      )

      if isError :
        self._log.add(
          self.__class__.__name__,
          "SEEK_HEAD",
          "Head position request failed."
        )

      self.stateMachine.setHeadPosition = None

    # Shutoff servo control.
    if self.stateMachine.idleServos :
      self._io.plcLogic.servoDisable()
      self.stateMachine.idleServos = False
      isError = False

    return isError

  def xySeek(self):
    x = self.stateMachine.seekX
    if x is None:
      x = self._io.xAxis.getPosition()

    y = self.stateMachine.seekY
    if y is None:
      y = self._io.yAxis.getPosition()

    self._io.plcLogic.setXY_Position(
      x,
      y,
      self.stateMachine.seekVelocity,
      self.stateMachine.seekAcceleration,
      self.stateMachine.seekDeceleration
    )

    self.stateMachine.seekX = None
    self.stateMachine.seekY = None
    self.stateMachine.seekVelocity = None
    self.stateMachine.seekAcceleration = None
    self.stateMachine.seekDeceleration = None
    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """

    # If stop requested...
    if self.stateMachine.stopRequest :
      # We didn't finish this line.  Run it again.
      self._io.plcLogic.stopSeek()
      self._io.head.stop()
      self._log.add(
        self.__class__.__name__,
        "SEEK_STOP",
        "Seek stop requested"
      )
      self._noteSeekStop = True
      self.stateMachine.stopRequest = False

    # Is movement done?
    if self._io.plcLogic.isReady() and self._io.head.isIdle():

      # If we were seeking and stopped pre-maturely, note where.
      if self._noteSeekStop:
        self.logCurrentPosition("SEEK_STOP_LOCATION", 'Seek stopped at (')
      # If we were jogging, note where it stopped.
      if self._wasJogging:
        self.logCurrentPosition("JOG_STOP", 'Jog stopped at (')
      self.changeState( self.stateMachine.States.STOP )

  def logCurrentPosition(self, status, message):
    x = self._io.xAxis.getPosition()
    y = self._io.yAxis.getPosition()
    z = self._io.zAxis.getPosition()
    self._log.add(
        self.__class__.__name__,
        status,
        f"{message}{str(x)},{str(y)},{str(z)})",
        [x, y, z],
    )


#end class