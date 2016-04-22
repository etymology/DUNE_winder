###############################################################################
# Name: DefaultCalibration.py
# Uses: Generate a default calibration file for layer based on nominal geometry.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from Library.Geometry.Location import Location
from Library.SerializableLocation import SerializableLocation

from Machine.LayerCalibration import LayerCalibration
from Machine.X_LayerGeometry import X_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.G_LayerGeometry import G_LayerGeometry

from RecipeGenerator.LayerX_Recipe import LayerX_Recipe
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe
from RecipeGenerator.LayerU_Recipe import LayerU_Recipe
from RecipeGenerator.LayerG_Recipe import LayerG_Recipe

class DefaultCalibration( LayerCalibration ) :

  #---------------------------------------------------------------------
  def __init__( self, outputFilePath, outputFileName, layerName ) :
    """
    Export node list to calibration file.  Debug function.

    Args:
      outputFileName: File name to create.
      layerName: Name of recipe.
    """

    if "X" == layerName :
      geometry = X_LayerGeometry()
      recipe = LayerX_Recipe( geometry )
    elif "V" == layerName :
      geometry = V_LayerGeometry()
      recipe = LayerV_Recipe( geometry )
    elif "U" == layerName :
      geometry = U_LayerGeometry()
      recipe = LayerU_Recipe( geometry )
    elif "G" == layerName :
      geometry = G_LayerGeometry()
      recipe = LayerG_Recipe( geometry )
    else :
      raise "Unknown layer: " + str( layerName )

    LayerCalibration.__init__( self, layerName )
    self.setOffset( SerializableLocation( 0, 0 ) )

    for node in recipe.nodes :
      location = recipe.nodes[ node ]
      newLocation = SerializableLocation( location.x, location.y )
      self.setPinLocation( node, newLocation )

    self.save( outputFilePath, outputFileName, "LayerCalibration" )

# end class

if __name__ == "__main__":
  DefaultCalibration( ".", "X_Calibration.xml", "X" )
  DefaultCalibration( ".", "V_Calibration.xml", "V" )
  DefaultCalibration( ".", "U_Calibration.xml", "U" )
  DefaultCalibration( ".", "G_Calibration.xml", "G" )
