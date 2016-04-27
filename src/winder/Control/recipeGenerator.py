###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os.path

from Library.Configuration import Configuration

from Machine.Settings import Settings
from Machine.LayerCalibration import LayerCalibration
from Machine.X_LayerGeometry import X_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.G_LayerGeometry import G_LayerGeometry

from RecipeGenerator.LayerX_Recipe import LayerX_Recipe
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe
from RecipeGenerator.LayerU_Recipe import LayerU_Recipe
from RecipeGenerator.LayerG_Recipe import LayerG_Recipe

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
  geometryX = X_LayerGeometry()
  recipeX = LayerX_Recipe( geometryX )

  geometryV = V_LayerGeometry()
  recipeV = LayerV_Recipe( geometryV, geometryV.pins / 6 )

  geometryU = U_LayerGeometry()
  recipeU = LayerU_Recipe( geometryU, geometryU.pins / 6 )

  geometryG = G_LayerGeometry()
  recipeG = LayerG_Recipe( geometryG )

  recipeX.printStats()
  recipeV.printStats()
  recipeU.printStats()
  recipeG.printStats()

  # Save recipes for each layer to recipe directory.
  recipeX.writeG_Code( recipeDirectory + "/X-Layer.gc", "X Layer" )
  recipeV.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )
  recipeU.writeG_Code( recipeDirectory + "/U-Layer.gc", "U Layer" )
  recipeG.writeG_Code( recipeDirectory + "/G-Layer.gc", "G Layer" )


  #  #
  #  # Export SketchUp Ruby code.
  #  #
  #
  #  # Generate an ideal calibration file for layer.
  #  recipeX.writeDefaultCalibration( "./", "X-Layer_Calibration.xml", "X Layer" )
  #  calibrationX = LayerCalibration()
  #  calibrationX.load( "./", "X-Layer_Calibration.xml" )
  #  calibrationX.setOffset( geometryX.apaOffset )
  #  gCodePath = G_CodeToPath( recipeDirectory + "/X-Layer.gc", geometryX, calibrationX )
  #  gCodePath.writeRubyCode( "X-Layer.rb", enablePathLabels=False, enablePinLabels=True )
  #  recipeX.writeRubyCode(
  #    "X-Layer.rb",
  #    enablePath=False,
  #    enablePathLabels=False,
  #    enableWire=True,
  #    isAppend=False
  #  )
  #
  #
  #  recipeV.writeDefaultCalibration( "./", "V-Layer_Calibration.xml", "V Layer" )
  #  calibrationV = LayerCalibration()
  #  calibrationV.load( "./", "V-Layer_Calibration.xml" )
  #  calibrationV.setOffset( geometryV.apaOffset )
  #  gCodePath = G_CodeToPath( recipeDirectory + "/V-Layer.gc", geometryV, calibrationV )
  #  gCodePath.writeRubyCode( "V-Layer.rb", enablePathLabels=False, enablePinLabels=False )
  #  recipeV.writeRubyCode(
  #    "V-Layer.rb",
  #    enablePath=False,
  #    enablePathLabels=False,
  #    enableWire=True,
  #    isAppend=False
  #  )
  #
  #  recipeU.writeDefaultCalibration( "./", "U-Layer_Calibration.xml", "U Layer" )
  #  calibrationU = LayerCalibration()
  #  calibrationU.load( "./", "U-Layer_Calibration.xml" )
  #  calibrationU.setOffset( geometryU.apaOffset )
  #  gCodePath = G_CodeToPath( recipeDirectory + "/U-Layer.gc", geometryU, calibrationU )
  #  gCodePath.writeRubyCode( "U-Layer.rb", enablePathLabels=False, enablePinLabels=True )
  #  recipeU.writeRubyCode(
  #    "U-Layer.rb",
  #    enablePath=True,
  #    enablePathLabels=False,
  #    enableWire=True,
  #    isAppend=False
  #  )
  #
  #
  #  recipeG.writeDefaultCalibration( "./", "G-Layer_Calibration.xml", "G Layer" )
  #  calibrationG = LayerCalibration()
  #  calibrationG.load( "./", "G-Layer_Calibration.xml" )
  #  calibrationG.setOffset( geometryG.apaOffset )
  #  gCodePath = G_CodeToPath( recipeDirectory + "/G-Layer.gc", geometryG, calibrationG )
  #  gCodePath.writeRubyCode( "G-Layer.rb", enablePathLabels=False, enablePinLabels=True )
  #  recipeG.writeRubyCode(
  #    "G-Layer.rb",
  #    enablePath=False,
  #    enablePathLabels=False,
  #    enableWire=True,
  #    isAppend=False
  #  )


  #recipeU.writeRubyCode( "U-Layer.rb", False, False, True, False )
  #$$$recipeU.writeRubyBasePath( "U-Layer.rb", False )

  #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )





# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
