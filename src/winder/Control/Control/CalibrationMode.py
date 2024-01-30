###############################################################################
# Name: CalibrationMode.py
# Uses: Update function for calibration mode.
# Date: 2016-12-16
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from Library.StateMachineState import StateMachineState

class CalibrationMode( StateMachineState ) :

  # After reaching the finial location, there is a pause to allow the camera
  # FIFO to be emptied.  This is the number of counts of that pause.
  # (At 100 ms/update, this is 500 ms.)
  SHUTDOWN_COUNT = 5

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
    self._shutdownCount = None

  #---------------------------------------------------------------------
  def enter( self ):
    """
    Enter into calibration mode.
    This acts much like manual mode, except a seek is the only allowed command.

    Returns:
      True if there was an error, false if not.  The error can happen
      if there isn't a manual action to preform.
    """
    self._noteSeekStop = False
    self._shutdownCount = None

    return (self.xySeek() if self.stateMachine.seekX != None
            or self.stateMachine.seekY != None else True)

  # TODO Rename this here and in `enter`
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
  def exit( self ) :
    """
    Function called when exiting this state.

    Returns:
      True if there was an error, false if not.
    """

    self._io.camera.endScan()

    return False

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.
    """

    self.stateMachine.cameraCalibration.poll()

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

    if self._shutdownCount > 0 :
      self._shutdownCount -= 1

    isMotionCompleat = self._io.plcLogic.isReady()

    if isMotionCompleat and self._shutdownCount is None:
      self._shutdownCount = CalibrationMode.SHUTDOWN_COUNT

    # Is movement done?
    if isMotionCompleat and self._shutdownCount == 0:

      # If we were seeking and stopped pre-maturely, note where.
      if self._noteSeekStop:
        x = self._io.xAxis.getPosition()
        y = self._io.yAxis.getPosition()
        z = self._io.zAxis.getPosition()
        self._log.add(
            self.__class__.__name__,
            "CALIBRATION_STOP_LOCATION",
            f"Seek stopped at ({str(x)},{str(y)},{str(z)})",
            [x, y, z],
        )

      self._io.camera.endScan()
      self.changeState( self.stateMachine.States.STOP )

#end class