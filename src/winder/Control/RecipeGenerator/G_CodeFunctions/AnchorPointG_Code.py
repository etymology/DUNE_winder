###############################################################################
# Name: AnchorPointG_Code.py
# Uses: G-Code to specify anchor point of wire during move.
# Date: 2016-08-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from G_CodeFunction import G_CodeFunction
from Machine.G_Codes import G_Codes

class AnchorPointG_Code( G_CodeFunction ) :
  """
  G-Code to specify anchor point of wire during move.
  """

  #---------------------------------------------------------------------
  def __init__( self, pinA, pinB=None, offset=None ) :
    """
    Constructor.

    Args:
      pinA: First pin for centering.
      pinB: Center pin for centering.
      offset: 0=None, U/D=Up or down, L/R=Left/right.
    """

    if None == pinB :
      pinB = pinA

    if None == offset :
      offset = "0"

    G_CodeFunction.__init__( self, G_Codes.ANCHOR_POINT, [ pinA, pinB, offset ] )
