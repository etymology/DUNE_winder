###############################################################################
# Name: RecipeGenerator.py
# Uses: Base recipe generation class.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Location import Location
from Library.Recipe import Recipe

class RecipeGenerator :
  """
  Base recipe class.
  """

  net = []
  nodesFront = []
  nodesBack = []
  gCodePath = None
  nodePath = None

  #---------------------------------------------------------------------
  def center( self, startPin, direction ) :
    """
    Get the center location between two pins.

    Args:
      startPin: Net index of the first pin.
      direction: +1 or -1 to select neighbor for centering.

    Returns:
      Location instance with the center point between these two pins.
    """
    pin = self.net[ startPin ]
    x = self.nodesFront[ pin ].x
    y = self.nodesFront[ pin ].y
    pinA = Location( x, y )

    netOffset = ( pin + direction ) % len( self.nodesFront )
    x = self.nodesFront[ netOffset ].x
    y = self.nodesFront[ netOffset ].y
    pinB = Location( x, y )

    return pinA.center( pinB )

  #---------------------------------------------------------------------
  def location( self, net ) :
    """
    Get the location of a pin by net index.

    Args:
      net: Net index of the pin.

    Returns:
      Location instance of the net.
    """
    pin = self.net[ net ]
    location = self.nodesFront[ pin ]
    result = Location( location.x, location.y, location.z )
    return result

  #---------------------------------------------------------------------
  def writeRubyCode( self, outputFileName ) :
    """
    Export node paths to Ruby code for import into SketchUp for visual
    verification.

    Args:
      outputFileName: File name to create.
    """
    rubyFile = open( outputFileName, "w" )
    self.gCodePath.toSketchUpRuby( rubyFile, False )
    self.nodePath.toSketchUpRuby( rubyFile )
    rubyFile.close()

  #---------------------------------------------------------------------
  def writeG_Code( self, outputFileName, layerName ) :
    """
    Export G-Code to file.

    Args:
      outputFileName: File name to create.
      layerName: Name of recipe.
    """

    # Safe G-Code instructions.
    gCodeFile = open( outputFileName, "w" )
    self.gCodePath.toG_Code( gCodeFile, layerName )
    gCodeFile.close()

    # Create an instance of Recipe to update the header with the correct hash.
    Recipe( outputFileName, None )
