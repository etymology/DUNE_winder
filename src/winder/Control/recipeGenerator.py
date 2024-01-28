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
from Library.Geometry.Location import Location

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

# Generate Ruby code for SketchUp.
isRubyCode = False

# Enable G-Code path output for SketchUp.
enablePath = True

# Enable wire path output for SketchUp.
enableWire = True

# Enable G-Code labels.
enablePathLabels = False

# Enable pin labels.
enablePinLabels = False

# Do not use APA offsets in SketchUp output.
zeroOffset = False

# Enable base path (i.e. path without compensation for pin radius).
isRubyBasePath = False

# Overriding number of loops to complete.
overrideLaps = None

# Individual layer enables.
enableX = True
enableU = True
enableV = True
enableG = True

# True to create calibration files for the layers.
isCalibration = False

#==============================================================================

#------------------------------------------------------------------------------
def writeRubyCode( layer, recipe, geometry ) :
  """
  Generate the Ruby code for layer.

  Args:
    layer - Name of layer (X/U/V/G).
    recipe - Instance of RecipeGenerator.
    geometry - Geometry for layer.
  """

  print "Generating SketchUp Ruby code"

  # Generate an ideal calibration file for layer.
  print "  Generate an ideal calibration file for layer."
  calibration = recipe.defaultCalibration( layer, geometry, isCalibration )
  if zeroOffset :
    calibration.offset = Location()

  outputFileName = layer + "-Layer.rb"

  # Construct G-Code for first half.
  print "  Construct G-Code for first half."
  gCodePath = G_CodeToPath(
    recipeDirectory + "/" + layer + "-Layer_1.gc",
    geometry,
    calibration
  )

  # Write 1st wind G-Code path.
  print "  Write 1st wind G-Code path."
  gCodePath.writeRubyCode(
    outputFileName,
    layer,
    "1st",
    enablePathLabels,
    enablePinLabels,
    False
  )

  # Write wire path.
  print "  Write wire path."
  recipe.writeRubyCode(
    layer,
    0,
    outputFileName,
    enablePath,
    enablePathLabels,
    enableWire,
    True
  )

  if overrideLaps > 1 or None == overrideLaps :
    # Construct G-Code for second half.
    print "  Construct G-Code for second half."
    gCodePath = G_CodeToPath(
      recipeDirectory + "/" + layer + "-Layer_2.gc",
      geometry,
      calibration
    )

    # Write 2nd wind G-Code path.
    print "  Write 2nd wind G-Code path."
    gCodePath.writeRubyCode(
      outputFileName,
      layer,
      "2nd",
      enablePathLabels,
      enablePinLabels,
      True
    )

#------------------------------------------------------------------------------
def generateLayer( layer, recipeClass, geometry, enable ) :
  """
  Generate recipe data for given layer.

  Args:
    layer - Name of layer (X/U/V/G).
    recipeClass - Class to generate recipe (child of RecipeGenerator).
    geometry - Geometry for layer.
    enable - True to generate data for this layer, False to skip.
  """
  if enable :
    print "Generating " + layer + "-layer recipe"
    recipe = recipeClass( geometry, overrideLaps )
    recipe.writeG_Code( recipeDirectory + "/" + layer + "-Layer", "gc", layer + " Layer" )

    if isRubyCode :
      writeRubyCode( layer, recipe, geometry )

    if isRubyBasePath :
      recipe.writeRubyBasePath( layer + "-Layer.rb", False )

    recipe.printStats()
  else :
    print "Skipping " + layer + "-layer recipe"
  print

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
    elif "BASEPATH" == option :
      isRubyBasePath = ( "TRUE" == value )
    elif "OVERRIDE" == option :
      overrideLaps = int( value )
    elif "CALIBRATION" == option :
      isCalibration = ( "TRUE" == value )
    else :
      raise Exception( "Unknown:" + option )

  geometryX = X_LayerGeometry()
  geometryV = V_LayerGeometry()
  geometryU = U_LayerGeometry()
  geometryG = G_LayerGeometry()

  # Ignoring offsets?
  # (Typically used for SketchUp models without offsets).
  if zeroOffset :
    print "APA offsets set to zero"

    geometryX.apaOffsetX = 0
    geometryX.apaOffsetY = 0
    geometryX.apaOffsetZ = 0

    geometryV.apaOffsetX = 0
    geometryV.apaOffsetY = 0
    geometryV.apaOffsetZ = 0

    geometryU.apaOffsetX = 0
    geometryU.apaOffsetY = 0
    geometryU.apaOffsetZ = 0

    geometryG.apaOffsetX = 0
    geometryG.apaOffsetY = 0
    geometryG.apaOffsetZ = 0

  print

  generateLayer( "X", LayerX_Recipe, geometryX, enableX )
  generateLayer( "V", LayerV_Recipe, geometryV, enableV )
  generateLayer( "U", LayerU_Recipe, geometryU, enableU )
  generateLayer( "G", LayerG_Recipe, geometryG, enableG )

# "If quantum mechanics hasn't profoundly shocked you, you haven't understood
# it yet." -- Niels Bohr
