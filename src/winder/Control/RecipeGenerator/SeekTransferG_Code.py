###############################################################################
# Name: SeekTransferG_Code.py
# Uses: A seek transfer will instruct the target to follow the slope of the line
#       until it reaches a Z transfer area.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from G_CodeFunction import G_CodeFunction

class SeekTransferG_Code( G_CodeFunction ) :
  """
  A seek transfer will instruct the target to follow the slope of the line
  until it reaches a Z transfer area.
  """

  # Various seek locations.  Bitmap.
  TOP          = 1
  BOTTOM       = 2
  LEFT         = 4
  RIGHT        = 8
  TOP_LEFT     = 1 + 4
  TOP_RIGHT    = 1 + 8
  BOTTOM_LEFT  = 2 + 4
  BOTTOM_RIGHT = 2 + 8

  #---------------------------------------------------------------------
  def __init__( self, seekLocation ) :
    """
    Constructor.

    Args:
      seekLocation: One (or more) of the seek seek locations.
    """
    G_CodeFunction.__init__( self, 102, [ seekLocation ] )
    self._seekLocation = seekLocation

  def seekLocationName( self ) :
    """
    Return the seek location name for this object.

    Returns:
      String of seek location.
    """
    location = ""

    if self._seekLocation & SeekTransferG_Code.TOP :
      location += "top "

    if self._seekLocation & SeekTransferG_Code.BOTTOM :
      location += "bottom "

    if self._seekLocation & SeekTransferG_Code.LEFT :
      location += "left "

    if self._seekLocation & SeekTransferG_Code.RIGHT :
      location += "right "

    return location.strip()
