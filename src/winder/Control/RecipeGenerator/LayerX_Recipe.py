###############################################################################
# Name: LayerX_Recipe.py
# Uses: Functions specific to wind the X layer.
# Date: 2016-04-13
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from LayerGX_Recipe import LayerGX_Recipe

class LayerX_Recipe( LayerGX_Recipe ) :

  #-------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None ) :
    """
    Constructor.
    """

    LayerGX_Recipe.__init__( self, geometry, windsOverride, 0.5 )
