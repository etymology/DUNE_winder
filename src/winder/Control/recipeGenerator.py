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
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe

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

  #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )
  #recipe.writeRubyCode( "V-Layer.rb", True, True, True )
  recipe.printStats()

# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
