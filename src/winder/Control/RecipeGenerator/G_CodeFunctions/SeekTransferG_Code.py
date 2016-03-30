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

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.

    Args:
      seekLocation: One (or more) of the seek seek locations.
    """
    G_CodeFunction.__init__( self, 102, [] )

  def seekLocationName( self ) :
    """
    Return the seek location name for this object.

    Returns:
      String of seek location.

      $$$DEBUG - Remove function.
    """
    location = ""
    return location.strip()
