###############################################################################
# Name: Y_TestGenerator.py
# Uses: Generate G-Code for Y-Stage testing.
# Date: 2016-06-01
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   This will produce G-Code to move the Y stage to various random positions
# and then do a complete Z-motion.
#   Invoke from winder/Control like this:
#     python -m Debug.Y_TestGenerator
#   To reproduce a test one needs the seed specified on the command line:
#     python -m Debug.Y_TestGenerator seed=1234
#   Total cycles can be generated as well (seed optional):
#     python -m Debug.Y_TestGenerator seed=5678 cycles=1000
###############################################################################

import sys
import random
from Library.Recipe import Recipe

outputFileName = "../Recipes/Y_Test.gc"
cycles      = 1000
Y_BOTTOM    = 0
Y_TOP       = 2750
Z_RETRACTED = 0
Z_EXTENDED  = 434

# Generate an initial random seed.
# (We need to be able to reproduce the same pseudo-random numbers, so the
# seed is initially random but can be changed via the command line arguments.)
seed = random.randint( 0, sys.maxint )

# Handle command line.
for argument in sys.argv:
  #argument = argument.upper()
  option = argument
  value = "TRUE"
  if -1 != argument.find( "=" ) :
    option, value = argument.split( "=" )

  option = option.upper()

  if "CYCLES" == option :
    cycles = int( value )
  elif "SEED" == option :
    seed = int( value )
  elif "OUTPUT" == option :
    outputFileName = value

# Seed random number generator.
random.seed( seed )

with open( outputFileName, "w" ) as gCodeFile :
  # Header.
  gCodeFile.write( "( Y/Z cycle test using " + str( cycles ) + " cycles.  Random seed: " + str( seed ) + " )\n" )

  for cycle in range( 0, cycles ) :
    y = random.random() * ( Y_TOP - Y_BOTTOM ) + Y_BOTTOM
    gCodeFile.write( "N" + str( cycle + 1 ) + " Y" + str( y ) + "\n" )

    # Go and get head.
    gCodeFile.write( "Z" + str( Z_EXTENDED ) + "\n" )
    gCodeFile.write( "G100" )
    gCodeFile.write( "Z" + str( Z_RETRACTED ) + "\n" )

    # Return head.
    gCodeFile.write( "Z" + str( Z_EXTENDED ) + "\n" )
    gCodeFile.write( "G100" )
    gCodeFile.write( "G100" )
    gCodeFile.write( "Z" + str( Z_RETRACTED ) + "\n" )

# Use the recipe to create hash.
Recipe( outputFileName, None )
