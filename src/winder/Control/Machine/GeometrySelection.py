###############################################################################
# Name: GeometrySelection.py
# Uses: Create layer geometry based on layer name.
# Date: 2016-11-01
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from .LayerGeometry import LayerGeometry
from .X_LayerGeometry import X_LayerGeometry
from .V_LayerGeometry import V_LayerGeometry
from .U_LayerGeometry import U_LayerGeometry
from .G_LayerGeometry import G_LayerGeometry

class GeometrySelection( LayerGeometry ) :

  #-------------------------------------------------------------------
  def __new__( _, layerName ):
    """
    The new operator will actually not create an instance of this class, but
    rather an instance of the requested layer's geometry class.

    Args:
      layerName: Name of layer geometry to create (X/V/U/G).

    Returns:
      Instance of the requested layer geometry.
    """

    # Lookup table of layer geometries.
    LAYERS = {
      'X' : X_LayerGeometry,
      'V' : V_LayerGeometry,
      'U' : U_LayerGeometry,
      'G' : G_LayerGeometry,
    }

    # Select requested geometry.
    specificLayer = LAYERS[ layerName ]

    # Return instance of specified layer.
    return specificLayer()

# Unit test.
if __name__ == "__main__":
  xGeometry = GeometrySelection( 'X' )
  vGeometry = GeometrySelection( 'V' )
  uGeometry = GeometrySelection( 'U' )
  gGeometry = GeometrySelection( 'G' )

  assert( type( xGeometry ) == X_LayerGeometry )
  assert( type( vGeometry ) == V_LayerGeometry )
  assert( type( uGeometry ) == U_LayerGeometry )
  assert( type( gGeometry ) == G_LayerGeometry )
