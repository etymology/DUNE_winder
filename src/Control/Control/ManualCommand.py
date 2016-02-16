#==============================================================================
# Name: ManualCommand.py
# Uses: Manual commands for jogging motors.
# Date: 2016-02-16
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-16 - QUE - Creation.
# Notes:
#   Typical operation.  Set seek positions followed by a manual request.
#      manualCommand = ManualCommand()
#      ...
#      # Move to position (100,200).
#      manualCommand.setSeekX( 100 )
#      manualCommand.setSeekY( 200 )
#      manualCommand.setManualRequest( True )
#==============================================================================

class ManualCommand :

  #---------------------------------------------------------------------
  def __init__( self ) :
    self.isManualRequest = False
    self.isSeeking = False
    self.seekX = None
    self.seekY = None
    self.seekZ = None

  #---------------------------------------------------------------------
  def setSeeking( self, state ) :
    """
    Set seeking state.  Control software use only.

    Args:
      state: True for motion, False for no motion.
    """

    self.isSeeking = state

  #---------------------------------------------------------------------
  def getSeeking( self ) :
    """
    Set seeking state.  Control software use only.

    Returns:
      True if currently seeking, False if not.
    """

    return self.isSeeking

  #---------------------------------------------------------------------
  def setManualRequest( self, state ) :
    """
    Request/abort a manual motion to previously set seek positions.

    Args:
      state: True to start motion, False to stop motion.

    Returns:
      True if there was an error, false if not.
    """

    self.isManualRequest = state

    return False

  #---------------------------------------------------------------------
  def setSeekX( self, position ) :
    """
    Set the seek position for X-axis.

    Args:
      position: Position to seek.

    Returns:
      True if there was an error, false if not.
    """

    self.seekX = position

    return False

  #---------------------------------------------------------------------
  def setSeekY( self, position ) :
    """
    Set the seek position for Y-axis.

    Args:
      position: Position to seek.

    Returns:
      True if there was an error, false if not.
    """

    self.seekY = position

    return False

  #---------------------------------------------------------------------
  def setSeekZ( self, position ) :
    """
    Set the seek position for Z-axis.

    Args:
      position: Position to seek.

    Returns:
      True if there was an error, false if not.
    """

    self.seekZ = position

    return False


#end class