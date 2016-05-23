###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import sys
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

#==============================================================================
# Settings.
# Can be overridden from the command-line.
#==============================================================================

# True to generate Ruby code for SketchUp.
isRubyCode = False

enablePath       = True
enableWire       = True
enablePathLabels = False
enablePinLabels  = False

enableX = True
enableU = True
enableV = True
enableG = True
zeroOffset = False

#==============================================================================

#------------------------------------------------------------------------------
if __name__ == "__main__":

  # Load configuration.
  configuration = Configuration( Settings.CONFIG_FILE )
  Settings.defaultConfig( configuration )

  recipeDirectory = configuration.get( "recipeDirectory" )

  # Create recipe directory if it does not exist.
  if not os.path.exists( recipeDirectory ) :
    os.makedirs( recipeDirectory )

  # Handle command line.
  for argument in sys.argv[ 1: ] :
    argument = argument.upper()
    option = argument
    value = "TRUE"
    if -1 != argument.find( "=" ) :
      option, value = argument.split( "=" )

    if "SKETCHUP" == option :
      isRubyCode = ( "TRUE" == value )
    elif "G-CODEPATHS" == option :
      enablePath = ( "TRUE" == value )
    elif "WIREPATHS" == option :
      enableWire = ( "TRUE" == value )
    elif "PINLABELS" == option :
      enablePinLabels = ( "TRUE" == value )
    elif "PATHLABELS" == option :
      enablePathLabels = ( "TRUE" == value )
    elif "X" == option :
      enableX = ( "TRUE" == value )
    elif "U" == option :
      enableU = ( "TRUE" == value )
    elif "V" == option :
      enableV = ( "TRUE" == value )
    elif "G" == option :
      enableG = ( "TRUE" == value )
    elif "0" == option :
      zeroOffset = ( "TRUE" == value )
    else :
      print "Unknown:", option

  # Generate recipes for each layer.
  if enableX :
    geometryX = X_LayerGeometry()
    recipeX = LayerX_Recipe( geometryX )

  if enableV :
    geometryV = V_LayerGeometry()
    recipeV = LayerV_Recipe( geometryV, geometryV.pins / 6 + 1 )

  if enableU :
    geometryU = U_LayerGeometry()
    if zeroOffset :
      geometryU.apaOffsetX = 0
      geometryU.apaOffsetY = 0
      geometryU.apaOffsetZ = 0

    recipeU = LayerU_Recipe( geometryU, geometryU.pins / 12 + 1 )

  if enableG :
    geometryG = G_LayerGeometry()
    recipeG = LayerG_Recipe( geometryG )

  # Save recipes for each layer to recipe directory.
  if enableX :
    recipeX.printStats()
    recipeX.writeG_Code( recipeDirectory + "/X-Layer.gc", "X Layer" )

  if enableV :
    recipeV.printStats()
    recipeV.writeG_Code( recipeDirectory + "/V-Layer.gc", "V Layer" )

  if enableU :
    recipeU.printStats()
    recipeU.writeG_Code( recipeDirectory + "/U-Layer.gc", "U Layer" )

  if enableG :
    recipeG.printStats()
    recipeG.writeG_Code( recipeDirectory + "/G-Layer.gc", "G Layer" )

  if isRubyCode :
    #
    # Export SketchUp Ruby code.
    #

    isAppend         = True

    if enableX :
      # Generate an ideal calibration file for layer.
      recipeX.writeDefaultCalibration( "./", "X-Layer_Calibration.xml", "X Layer" )
      calibrationX = LayerCalibration()
      calibrationX.load( "./", "X-Layer_Calibration.xml" )
      calibrationX.setOffset( geometryX.apaOffset )
      gCodePath = G_CodeToPath( recipeDirectory + "/X-Layer.gc", geometryX, calibrationX )
      gCodePath.writeRubyCode( "X-Layer.rb", enablePathLabels, enablePinLabels )
      recipeX.writeRubyCode(
        "X-Layer.rb",
        enablePath,
        enablePathLabels,
        enableWire,
        isAppend
      )

    if enableV :
      recipeV.writeDefaultCalibration( "./", "V-Layer_Calibration.xml", "V Layer" )
      calibrationV = LayerCalibration()
      calibrationV.load( "./", "V-Layer_Calibration.xml" )
      if not zeroOffset :
        calibrationV.setOffset( geometryV.apaOffset )
      gCodePath = G_CodeToPath( recipeDirectory + "/V-Layer.gc", geometryV, calibrationV )
      gCodePath.writeRubyCode( "V-Layer.rb", enablePathLabels, enablePinLabels )
      recipeV.writeRubyCode(
        "V-Layer.rb",
        enablePath,
        enablePathLabels,
        enableWire,
        isAppend
      )

    if enableU :
      recipeU.writeDefaultCalibration( "./", "U-Layer_Calibration.xml", "U Layer" )
      calibrationU = LayerCalibration()
      calibrationU.load( "./", "U-Layer_Calibration.xml" )
      if not zeroOffset :
        calibrationU.setOffset( geometryU.apaOffset )
      gCodePath = G_CodeToPath( recipeDirectory + "/U-Layer.gc", geometryU, calibrationU )
      gCodePath.writeRubyCode( "U-Layer.rb", enablePathLabels, enablePinLabels )
      recipeU.writeRubyCode(
        "U-Layer.rb",
        enablePath,
        enablePathLabels,
        enableWire,
        isAppend
      )

    if enableG :
      recipeG.writeDefaultCalibration( "./", "G-Layer_Calibration.xml", "G Layer" )
      calibrationG = LayerCalibration()
      calibrationG.load( "./", "G-Layer_Calibration.xml" )
      calibrationG.setOffset( geometryG.apaOffset )
      gCodePath = G_CodeToPath( recipeDirectory + "/G-Layer.gc", geometryG, calibrationG )
      gCodePath.writeRubyCode( "G-Layer.rb", enablePathLabels, enablePinLabels )
      recipeG.writeRubyCode(
        "G-Layer.rb",
        enablePath,
        enablePathLabels,
        enableWire,
        isAppend
      )

    #recipeU.writeRubyCode( "U-Layer.rb", False, False, True, False )
    #$$$recipeU.writeRubyBasePath( "U-Layer.rb", False )

    #recipe.writeRubyAnimateCode( "V-LayerAnimation.rb", 20 )

# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
