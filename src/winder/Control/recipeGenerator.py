###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os.path

from Machine.Settings import Settings
from Library.Configuration import Configuration

from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.LayerCalibration import LayerCalibration
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe
from RecipeGenerator.G_CodeToPath import G_CodeToPath

#------------------------------------------------------------------------------
if __name__ == "__main__":

  # Load configuration.
  configuration = Configuration( Settings.CONFIG_FILE )
  Settings.defaultConfig( configuration )

  recipeDirectory = configuration.get( "recipeDirectory" )

  # Create recipe directory if it does not exist.
  if not os.path.exists( recipeDirectory ) :
    os.makedirs( recipeDirectory )

  # Generate recipes for each layer.
  # $$$FUTURE - Add remaining layers.
  geometry = V_LayerGeometry()
  recipe = LayerV_Recipe( geometry )

  # Save recipes for each layer to recipe directory.
  # $$$FUTURE - Add remaining layers.
  recipe.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )


  #
  # Export SketchUp Ruby code.
  #

  # Generate an ideal calibration file for layer.
  recipe.writeDefaultCalibration( "./", "V-Layer_Calibration.xml", "V Layer" )
  calibration = LayerCalibration.load( "./", "V-Layer_Calibration.xml" )

  # Convert G-Code to path.
  gCodePath = G_CodeToPath( recipeDirectory + "/V-Layer.gc", geometry, calibration )
  gCodePath.writeRubyCode( "V-Layer.rb", True, True )

  # Add the resulting wire path.
  recipe.writeRubyCode( "V-Layer.rb", False, False, True, True )

  #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )
  recipe.printStats()


# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
