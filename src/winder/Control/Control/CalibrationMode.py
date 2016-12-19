###############################################################################
# Name: CalibrationMode.py
# Uses: Update function for calibration mode.
# Date: 2016-12-16
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.StateMachineState import StateMachineState

class CalibrationMode( StateMachineState ) :

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
    self._noteSeekStop = False

  #---------------------------------------------------------------------
  def enter( self ) :
    """
    Enter into calibration mode.
    This acts much like manual mode, except a seek is the only allowed command.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    isError = True

    self._noteSeekStop = False

    # X/Y axis move?
    if None != self.stateMachine.seekX or None != self.stateMachine.seekY :

      x = self.stateMachine.seekX
      if None == x :
        x = self._io.xAxis.getPosition()

      y = self.stateMachine.seekY
      if None == y :
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
        "CALIBRATION_STOP",
        "Seek stop requested"
      )
      self._noteSeekStop = True
      self.stateMachine.stopRequest = False

    # Is movement done?
    if self._io.plcLogic.isReady() :

      # If we were seeking and stopped pre-maturely, note where.
      if self._noteSeekStop :
        x = self._io.xAxis.getPosition()
        y = self._io.yAxis.getPosition()
        z = self._io.zAxis.getPosition()
        self._log.add(
          self.__class__.__name__,
          "CALIBRATION_STOP_LOCATION",
          "Seek stopped at (" + str( x ) + "," + str( y ) + "," + str( z ) + ")",
          [ x, y, z ]
        )

      self._io.camera.endScan()
      self.changeState( self.stateMachine.States.STOP )


#end class