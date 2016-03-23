###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os.path

from Control.Settings import Settings
from Library.Configuration import Configuration

from RecipeGenerator.LayerV_Layout import LayerV_Layout
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
  layout = LayerV_Layout()
  recipe = LayerV_Recipe( layout )

  # Save recipes for each layer to recipe directory.
  # $$$FUTURE - Add remaining layers.
  #recipe.writeRubyCode( "V-Layer.rb" )
  recipe.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )
