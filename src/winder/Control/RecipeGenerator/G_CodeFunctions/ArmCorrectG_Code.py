###############################################################################
# Name: ArmCorrectG_Code.py
# Uses: G-Code to correct current position for arm on head.
# Date: 2016-08-22
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from .G_CodeFunction import G_CodeFunction
from Machine.G_Codes import G_Codes

class ArmCorrectG_Code( G_CodeFunction ) :
  """
  G-Code to correct current position for arm on head.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """
    G_CodeFunction.__init__( self, G_Codes.ARM_CORRECT )
