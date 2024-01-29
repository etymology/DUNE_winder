###############################################################################
# Name: LayerG_Recipe.py
# Uses: Functions specific to wind the G layer.
# Date: 2016-04-14
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from .LayerGX_Recipe import LayerGX_Recipe

class LayerG_Recipe( LayerGX_Recipe ) :

  #-------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None ) :
    """
    Constructor.
    """

    LayerGX_Recipe.__init__( self, geometry, windsOverride, 0 )
