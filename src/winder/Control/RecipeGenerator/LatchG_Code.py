###############################################################################
# Name: LatchG_Code.py
# Uses: G-Code to set the Z latch position.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from G_CodeFunction import G_CodeFunction

class LatchG_Code( G_CodeFunction ) :
  """
  G-Code to set the Z latch position.
  """

  # Sides of the machine.
  FRONT = 0
  BACK  = 1

  #---------------------------------------------------------------------
  def __init__( self, side ) :
    """
    Constructor.

    Args:
      side: Which side (FRONT/BACK) to latch to.
    """
    G_CodeFunction.__init__( self, 100, [ side ] )
