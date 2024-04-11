###############################################################################
# Name: LayerU_Recipe.py
# Uses: Recipe generation for U-layer.
# Date: 2016-04-05
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################


from .LayerUV_Recipe import LayerUV_Recipe

class LayerU_Recipe( LayerUV_Recipe ) :
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
   \ /                  \
    *  *  *  *  *  *  *  *

  This layer begins in the bottom right corner, runs diagonally to the
  top center, then to the bottom most pin on the far left, the left most
  pin on the bottom, one pin right of center, and the second from the bottom
  """


  #---------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None ):
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
    self._createNode(
      geometry.gridFront,
      False,
      "F",
      geometry.mostlyExtend,
      self.geometry.startPinFront,
      self.geometry.directionFront
    )

    self._createNode(
      geometry.gridBack,
      False,
      "B",
      geometry.mostlyRetract,
      self.geometry.startPinBack,
      self.geometry.directionBack
    )

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = [
        f"F{str(geometry.columns + geometry.rows + 1)}",
        f"F{str(2 * geometry.columns + geometry.rows + 1)}",
        f"B{str(geometry.columns + 1)}",
        f"B{str(2 * geometry.columns + 2 * geometry.rows + 1)}",
        f"F{str(geometry.rows + 1)}",
        f"F{str(geometry.rows)}",
        'B1',
        f"B{str(geometry.columns)}",
        f"F{str(2 * geometry.columns + geometry.rows + 2)}",
        f"F{str(geometry.columns + geometry.rows)}",
        f"B{str(2 * geometry.columns + 2)}",
        f"B{str(2 * geometry.columns)}",
    ]

    # Total number of steps to do a complete wind.
    windSteps = 4 * geometry.rows + 4 * geometry.columns

    # Construct the remaining net list.
    self._createNet( windSteps, 1 )

    #
    # Crate motions necessary to wind the above pattern.
    #

    start1 = [ "F1201", "F1200" ]
    start2 = [ "F1201", "F1200" ]
    self._wind( start1, start2, 1, windsOverride )
