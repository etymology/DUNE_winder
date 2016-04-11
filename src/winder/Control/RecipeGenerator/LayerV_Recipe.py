###############################################################################
# Name: LayerV_Recipe.py
# Uses: Recipe generation for V-layer.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Location import Location

from LayerUV_Recipe import LayerUV_Recipe

class LayerV_Recipe( LayerUV_Recipe ) :
  """

    *  *  *  *  *  *  *  *
            / \/ \
  *        /  /\  \       *
         /   /  \  \
  *     /  /      \ \
      /   /        \  \   *
  *  /   /          \  \
   /   /              \ \
  *   /                \  *
     /                  \ /
    *  *  *  *  *  *  *  *

  This layer begins in the bottom right corner, runs diagonally to the
  top center, then to the bottom most pin on the far left, the left most
  pin on the bottom, one pin right of center, and the second from the bottom
  """


  #---------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None ) :
    """
    Constructor.  Does all calculations.

    Args:
      geometry: Instance of LayerV_Layout that specifies parameters for recipe
        generation.
      windsOverride: Set to specify the number to winds to make before stopping.
        Normally left to None.
    """

    LayerUV_Recipe.__init__( self, geometry )

    # Setup node list.
    self._createNode( geometry.gridFront, True, "F", geometry.partialZ_Front, 1, 1 )
    self._createNode(
      geometry.gridBack, True, "B", geometry.partialZ_Back, self.geometry.rows, -1 )

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      "F" + str( 2 * geometry.rows + geometry.columns ),
      "F" + str( geometry.columns ),
      "B" + str( geometry.rows + 2 * geometry.columns ),
      "B" + str( geometry.rows ),
      "F" + str( 1 ),
      "F" + str( 2 * geometry.rows + 2 * geometry.columns - 1 ),
      "B" + str( geometry.rows + 1 ),
      "B" + str( geometry.rows + 2 * geometry.columns - 1 ),
      "F" + str( geometry.columns + 1 ),
      "F" + str( 2 * geometry.rows + geometry.columns - 1 ),
      "B" + str( geometry.rows + geometry.columns + 1 ),
      "B" + str( geometry.rows + geometry.columns - 1 ),
    ]

    # Total number of steps to do a complete wind.
    windSteps = 4 * geometry.rows + 4 * geometry.columns - 3

    # Construct the remaining net list.
    self._createNet( windSteps )

    #
    # Crate motions necessary to wind the above pattern.
    #

    startLocation = \
      Location( geometry.deltaX * geometry.columns, geometry.wireSpacing / 2 )

    self._wind( startLocation, -1, windsOverride )
