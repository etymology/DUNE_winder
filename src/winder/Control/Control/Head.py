###############################################################################
# Name: Head.py
# Uses: Handling the passing around of the head via Z-axis.
# Date: 2016-04-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

class Head :

  class States :
    # Continuous states.
    IDLE        = 0
    SEEK        = 1
    LATCH       = 2

    # Momentary states.
    #FIRST_SEEK  = 3
    START_LATCH = 4
    SECOND_SEEK = 5
  # end class

  FRONT = 0
  PARTIAL_FRONT = 1
  PARTIAL_BACK  = 2
  BACK = 3

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
      if self._io.plcLogic.isReady() :
        self._state = self._nextState

    # Start latching?
    elif self.States.START_LATCH == self._state :
      # Begin latch and setup state machine for second seek when latch finishes.
      self._io.plcLogic.latch()
      self._nextState = self.States.SECOND_SEEK
      self._state = self.States.LATCH

    # Start second seek?
    elif self.States.SECOND_SEEK == self._state :
      # Start seek to the finial position.
      self._io.plcLogic.setZ_Position( self._lastSeek, self._velocity )

      # Always idle after this motion.
      self._nextState = self.States.IDLE
      self._state = self.States.SEEK

  #---------------------------------------------------------------------
  def __init__( self, io, geometry ) :
    """
    Constructor.
    """
    self._io = io
    self._geometry = geometry
    self._position = Head.FRONT
    self._velocity = None
    self._lastSeek = None
    self._state = self.States.IDLE

  #---------------------------------------------------------------------
  def setPosition( self, position, velocity ) :
    """
    Set the head position.

    Args:
      position: FRONT/PARTIAL_FRONT/PARTIAL_BACK/BACK.
      velocity: Max travel velocity.
    """
    isError = True

    # If the head is idle and the position is actually different...
    if self.States.IDLE == self._state and position != self._position :

      self._velocity = velocity

      if self.FRONT == position :
        desiredPosition = self._geometry.frontZ
      elif self.PARTIAL_FRONT == position :
        desiredPosition = self._geometry.partialZ_Front
      elif self.PARTIAL_BACK == position :
        desiredPosition = self._geometry.partialZ_Back
      elif self.BACK == position :
        desiredPosition = self._geometry.backZ

      # Do we have to go get/leave the head?
      if self.BACK == self._position or self.BACK == position :

        # The last seek is the set to the desired position.  If the back is
        # the desired position, then the last seek will be to the front, leaving
        # the head on the back.
        if self.BACK == position :
          self._lastSeek = self._geometry.frontZ
        else :
          self._lastSeek = desiredPosition

        # First seek is all the way to the back.
        desiredPosition = self._geometry.backZ

        # After the seek is complete, begin a latch operation.
        self._nextState = self.States.START_LATCH
      else:
        # If no latching operations are required, the seek finishes the operation.
        self._nextState = self.States.IDLE

      # Begin seeking.
      self._io.plcLogic.setZ_Position( desiredPosition, self._velocity )
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
      FRONT/PARTIAL_FRONT/PARTIAL_BACK/BACK.
    """
    return self._position

# end class
