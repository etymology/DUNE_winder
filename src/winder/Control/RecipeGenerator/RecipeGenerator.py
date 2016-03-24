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
  def writeRubyCode(
    self,
    outputFileName,
    enablePath=True,
    enablePathLabels=False,
    enableWire=True
  ) :
    """
    Export node paths to Ruby code for import into SketchUp for visual
    verification.

    Args:
      outputFileName: File name to create.
      enablePath: Show the path taken to wind the layer.
      enablePathLabels: Label additional G-Code points.
      enableWire: Show the wire wound on the layer.
    """
    rubyFile = open( outputFileName, "w" )

    if enablePath :
      self.gCodePath.toSketchUpRuby( rubyFile, enablePathLabels )

    if enableWire :
      self.nodePath.toSketchUpRuby( rubyFile )

    rubyFile.close()

  #---------------------------------------------------------------------
  def writeRubyAnimateCode(
    self,
    outputFileName,
    number
  ) :
    """
    Create SketchUp ruby code to have an animation with one new path displayed
    in each scene.

    Args:
      outputFileName: Where to write this data.
      number: Number of segments of the path to animate.
    """
    output = open( outputFileName, "w" )

    for index in range( 0, number ) :
      output.write( 'layer' + str( index )
        + ' = Sketchup.active_model.layers.add "wire' + str( index ) + '"' )

      output.write( 'layer' + str( index ) + '.visible = false' )
      output.write( 'Sketchup.active_model.active_layer = layer' + str( index ) )

      # Convert millimeters to inches.  Sketch-up always works in inches.
      point = self.nodePath.path[ index ]
      x1 = point.x / 25.4
      y1 = point.y / 25.4
      z1 = point.z / 25.4

      point = self.nodePath.path[ index + 1 ]
      x2 = point.x / 25.4
      y2 = point.y / 25.4
      z2 = point.z / 25.4

      output.write( 'Sketchup.active_model.entities.add_line '
        + "[" + str( x1 ) + "," + str( z1 ) + "," + str( y1 ) + "], "
        + "[" + str( x2 ) + "," + str( z2 ) + "," + str( y2 ) + "]"
      )

    for index in range( 0, number ) :
      output.write(
        'page' + str( index )
        + ' = Sketchup.active_model.pages.add "page' + str( index ) + '"'
      )

      for indexB in range( 0, number ) :
        visible = 'true'
        if indexB > index :
          visible = 'false'

        output.write( 'layer' + str( indexB ) + '.visible = ' + visible )

    output.close()

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

  #---------------------------------------------------------------------
  def printStats( self ) :
    """
    Print some statistics about the layer.
    """

    print "Wire consumed:", self.nodePath.totalLength()
    print "G-Code lines:", len( self.gCodePath )

