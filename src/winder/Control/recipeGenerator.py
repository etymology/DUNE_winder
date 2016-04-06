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
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.LayerCalibration import LayerCalibration
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe
from RecipeGenerator.LayerU_Recipe import LayerU_Recipe
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
  geometryV = V_LayerGeometry()
  recipeV = LayerV_Recipe( geometryV )
  geometryU = U_LayerGeometry()
  recipeU = LayerU_Recipe( geometryU )

  recipeV.printStats()
  recipeU.printStats()

  # Save recipes for each layer to recipe directory.
  # $$$FUTURE - Add remaining layers.
  #recipeV.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )
  recipeU.writeG_Code( recipeDirectory + "/U-Layer.gc", "U Layer" )


  #
  # Export SketchUp Ruby code.
  #

  # Generate an ideal calibration file for layer.
  recipeU.writeDefaultCalibration( "./", "U-Layer_Calibration.xml", "U Layer" )
  calibrationU = LayerCalibration.load( "./", "U-Layer_Calibration.xml" )

  # Convert G-Code to path.
  gCodePath = G_CodeToPath( recipeDirectory + "/U-Layer.gc", geometryU, calibrationU )
  gCodePath.writeRubyCode( "U-Layer.rb", True, True )

  # Add the resulting wire path.
  recipeU.writeRubyCode( "U-Layer.rb", False, False, True, True )

  #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )


# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
