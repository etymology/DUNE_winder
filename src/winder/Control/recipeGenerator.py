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
  recipeU = LayerU_Recipe( geometryU, 1 )

  recipeV.printStats()
  recipeU.printStats()

  # Save recipes for each layer to recipe directory.
  # $$$FUTURE - Add remaining layers.
  recipeV.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )
  recipeU.writeG_Code( recipeDirectory + "/U-Layer.gc", "U Layer" )


  #
  # Export SketchUp Ruby code.
  #


  # Generate an ideal calibration file for layer.
  recipeV.writeDefaultCalibration( "./", "V-Layer_Calibration.xml", "V Layer" )
  calibrationV = LayerCalibration.load( "./", "V-Layer_Calibration.xml" )
  gCodePath = G_CodeToPath( recipeDirectory + "/V-Layer.gc", geometryV, calibrationV )
  gCodePath.writeRubyCode( "V-Layer.rb", True, False )
  recipeV.writeRubyCode( "V-Layer.rb", False, False, True, True )


  recipeU.writeDefaultCalibration( "./", "U-Layer_Calibration.xml", "U Layer" )
  calibrationU = LayerCalibration.load( "./", "U-Layer_Calibration.xml" )
  gCodePath = G_CodeToPath( recipeDirectory + "/U-Layer.gc", geometryU, calibrationU )
  gCodePath.writeRubyCode( "U-Layer.rb", True, False )
  recipeU.writeRubyCode( "U-Layer.rb", False, False, True, True )

  #recipeU.writeRubyCode( "U-Layer.rb", False, False, True, False )
  #$$$recipeU.writeRubyBasePath( "U-Layer.rb", False )

  #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )


# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
