###############################################################################
# Name: OffsetG_Code.py
# Uses: G-Code to offset current position.
# Date: 2016-04-01
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from .G_CodeFunction import G_CodeFunction
from Machine.G_Codes import G_Codes

class OffsetG_Code( G_CodeFunction ) :
  """
  G-Code to offset current position.
  """

  #---------------------------------------------------------------------
  def __init__( self, x=None, y=None, z=None ):
    """
    Constructor.

    Args:
      pins: List of two pins.
    """
    parameters = []
    if x != None:
      parameters.append(f"X{str(x)}")

    if y != None:
      parameters.append(f"Y{str(y)}")

    if z != None:
      parameters.append(f"Z{str(z)}")

    G_CodeFunction.__init__( self, G_Codes.OFFSET, parameters )
