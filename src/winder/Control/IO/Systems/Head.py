###############################################################################
# Name: Head.py
# Uses: Handling the passing around of the head via Z-axis.
# Date: 2016-04-18
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


class Head :

  class States :
    # Continuous states.
    IDLE        = 0
    SEEK        = 1
    LATCH       = 2

    # Momentary states.
    START_DOUBLE_LATCH = 3
    START_LATCH = 4
    SECOND_SEEK = 5
  # end class

  RETRACTED = 0
  FRONT     = 1
  BACK      = 2
  EXTENDED  = 3

  #---------------------------------------------------------------------
  def isIdle( self ) :
    """
    See if state head is idle (i.e. not in a state of motion).  Make sure
    this is True before requesting a move.

    Returns:
      True if not in motion, False if not.
    """

    self.update()

    return self.States.IDLE == self._state

  #---------------------------------------------------------------------
  def update( self ) :
    """
    Update state machine logic.
    """

    # Seeking/latching?
    if self.States.SEEK == self._state or self.States.LATCH == self._state :
      if self._plcLogic.isReady() :
        self._state = self._nextState

    elif self.States.START_DOUBLE_LATCH == self._state :
      # Start first latch, and prepare to latch again as the next state.
      self._plcLogic.latch()
      self._nextState = self.States.START_LATCH
      self._state = self.States.LATCH

    # Start latching?
    elif self.States.START_LATCH == self._state :
      # Begin latch and setup state machine for second seek when latch finishes.
      self._plcLogic.latch()
      self._nextState = self.States.SECOND_SEEK
      self._state = self.States.LATCH

    # Start second seek?
    elif self.States.SECOND_SEEK == self._state :

      # Start seek to the finial position.
      self._desiredPosition = self._lastSeek
      # Hack to speed up arm retraction at G106 P3 movement
      if  self.EXTENDED == self._position : # Leave head latched, then retract arm with : 10 * velocity
        self._plcLogic.setZ_Position( self._lastSeek, self._velocity * 10 )
      else :  # run at normal velocity
        self._plcLogic.setZ_Position( self._lastSeek, self._velocity )

      # Always idle after this motion.
      self._nextState = self.States.IDLE
      self._state = self.States.SEEK

  #---------------------------------------------------------------------
  def __init__( self, plcLogic ) :
    """
    Constructor.

    Args:
      plcLogic: Instance of PLC_Logic.
    """
    self._plcLogic  = plcLogic
    self._extended  = None
    self._retracted = None
    self._front     = None
    self._back      = None
    self._position  = Head.RETRACTED
    self._lastPosition = Head.RETRACTED
    self._velocity  = None
    self._lastSeek  = None
    self._state = self.States.IDLE

    # Desired location of axis.
    self._desiredPosition = 0

  #---------------------------------------------------------------------
  def setFrontAndBack( self, front, back ) :
    """
    Set the front and back locations (i.e. locations to put head level with
    the current layer).

    Args:
      front: Z-location to make head level with current layer on front side.
      back: Z-location to make head level with current layer on back side.
    """
    self._front = front
    self._back  = back

  #---------------------------------------------------------------------
  def setExtendedAndRetracted( self, retracted, extended ) :
    """
    Set the extended and retracted position for the Z-axis.

    Args:
      retracted: Z-position for fully retracted.
      extended: Z-position for fully extended (i.e. ready to latch).
    """
    self._extended  = extended
    self._retracted = retracted

  #---------------------------------------------------------------------
  def setPosition( self, position, velocity ) :
    """
    Set the head position.

    Args:
      position: RETRACTED/FRONT/BACK/EXTENDED.
      velocity: Max travel velocity.
    """
    isError = True

    # If the head is idle and the position is actually different...
    if self.States.IDLE == self._state and position != self._position :

      # Note from where we started.
      self._lastPosition = self._position

      self._velocity = velocity

      if self.RETRACTED == position :
        self._desiredPosition = self._retracted
      elif self.FRONT == position :
        self._desiredPosition = self._front
      elif self.BACK == position :
        self._desiredPosition = self._back
      elif self.EXTENDED == position :
        self._desiredPosition = self._extended
      else:
        raise "Unknown head position request" + str( position )

      # No desired position likely means the locations have not been setup.
      if None != self._desiredPosition :

        # Do we have to go get/leave the head?
        if self.EXTENDED == self._position or self.EXTENDED == position :

          # The last seek is the set to the desired position.  If the back is
          # the desired position, then the last seek will be to the front, leaving
          # the head on the back.
          if self.EXTENDED == position :
            self._lastSeek = self._retracted
          else :
            self._lastSeek = self._desiredPosition

          # First seek is all the way to the back.
          self._desiredPosition = self._extended

          # After the seek is complete, begin a latch operation.
          if self.EXTENDED == position :
            self._nextState = self.States.START_DOUBLE_LATCH
          else :
            self._nextState = self.States.START_LATCH
        else:
          # If no latching operations are required, the seek finishes the operation.
          self._nextState = self.States.IDLE

        # Begin seeking.
        self._plcLogic.setZ_Position( self._desiredPosition, self._velocity )
        self._state = self.States.SEEK

        # Use the new position as the current position.
        self._position = position

        isError = False

    return isError

  #---------------------------------------------------------------------
  def getPosition( self ) :
    """
    Get the current position of the head.

    Returns:
      RETRACTED/FRONT/BACK/EXTENDED.
    """
    return self._position

  #---------------------------------------------------------------------
  def getTargetAxisPosition( self ) :
    """
    Get the target location of head axis.

    Returns:
      Target location of head axis.
    """
    return self._desiredPosition

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop/abort transfer.
    """

    # If in transition...
    if self.States.IDLE != self._state :

      # If Z axis is in motion, stop it.
      if self.States.SEEK == self._state :
        self._plcLogic.stopSeek()

      # Revert to previous position.
      self._position = self._lastPosition

      # Idle the state machine.
      self._state = self.States.IDLE

# end class
