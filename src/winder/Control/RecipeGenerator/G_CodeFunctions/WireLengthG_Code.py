###############################################################################
# Name: WireLengthG_Code.py
# Uses: G-Code to specify the amount of wire consumed by a move.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from .G_CodeFunction import G_CodeFunction
from Machine.G_Codes import G_Codes

class WireLengthG_Code( G_CodeFunction ) :
  """
  G-Code to specify the amount of wire consumed by a move.
  """

  #---------------------------------------------------------------------
  def __init__( self, length ) :
    """
    Constructor.

    Args:
      length: How much wire was consumed by this motion.
    """
    G_CodeFunction.__init__( self, G_Codes.WIRE_LENGTH, [ length ] )
