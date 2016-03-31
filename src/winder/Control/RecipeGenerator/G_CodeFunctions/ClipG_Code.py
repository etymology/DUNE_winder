###############################################################################
# Name: ClipG_Code.py
# Uses: G-Code to clip the position based on Z-transfer location.
# Date: 2016-03-31
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from G_CodeFunction import G_CodeFunction

class ClipG_Code( G_CodeFunction ) :
  """
  G-Code to clip the position based on Z-transfer location.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """
    G_CodeFunction.__init__( self, 104, [] )

