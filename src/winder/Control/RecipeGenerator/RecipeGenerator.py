###############################################################################
# Name: RecipeGenerator.py
# Uses: Base recipe generation class.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Path3d import Path3d
from Library.Geometry.Location import Location
from Library.Recipe import Recipe
from Machine.LayerCalibration import LayerCalibration
from G_CodeFunctions.LatchG_Code import LatchG_Code

# $$$DEBUG - Move
class Z_Axis :

  FRONT = 0
  PARTIAL_FRONT = 1
  PARTIAL_BACK  = 2
  BACK = 3

  #---------------------------------------------------------------------
  def __init__( self, gCodePath, geometry, initialPosition ) :
    """
    $$$DEBUG
    """
    self._gCodePath = gCodePath
    self._geometry = geometry
    self._currentPostion = initialPosition

  #---------------------------------------------------------------------
  def set( self, location ) :

    if self._currentPostion != location :

      # Latch needed?
      if Z_Axis.BACK == self._currentPostion or Z_Axis.BACK == location :
        # Latch to front or back?
        if self._currentPostion == Z_Axis.BACK :
          self._gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
        else :
          self._gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )

        # Get/set it from/to back.
        self._gCodePath.push( z=self._geometry.backZ )

      # Front and back are both in front.  This is because is the destination
      # is the back, we leave the head at the back and return to the front.
      if Z_Axis.BACK == location or Z_Axis.FRONT == location :
        self._gCodePath.push( z=self._geometry.frontZ )
      elif Z_Axis.PARTIAL_FRONT == location :
        self._gCodePath.push( z=self._geometry.partialZ_Front )
      elif Z_Axis.PARTIAL_BACK == location :
        self._gCodePath.push( z=self._geometry.partialZ_Back )

      self._currentPostion = location

class RecipeGenerator :
  """
  Base recipe class.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    $$$DEBUG
    """
    self.net = []
    self.nodes = {}
    self.totalPins = None
    self.gCodePath = None
    self.nodePath = None

    self.geometry = None
    self.headZ = 0

  #---------------------------------------------------------------------
  def offsetPin( self, pin, offset ) :
    """
    $$$DEBUG
    """
    side = pin[ 0 ]
    pinNumber  = int( pin[ 1: ] ) - 1
    pinNumber += offset
    pinNumber %= self.totalPins
    pinNumber += 1
    return side + str( pinNumber )

  #---------------------------------------------------------------------
  def pinNames( self, startPin, direction ) :
    """
    Return a pair of pin names of two pins next to one an other.

    Args:
      side: 'F' for front, 'B' for back side.
      startPin: First pin number.
      direction: Either -1 or 1 to fetch the pin on either side.

    Returns:
      List of two pin name strings.
    """
    pinA = self.net[ startPin ]
    pinB = self.offsetPin( pinA, direction )
    return [ pinA, pinB ]

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
    pinA = self.nodes[ pin ]

    pin = self.offsetPin( pin, direction )
    pinB = self.nodes[ pin ]

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
    return self.nodes[ pin ]

  #---------------------------------------------------------------------
  def writeRubyBasePath(
    self,
    outputFileName,
    isAppend=True
  ) :
    """
    Make the basic wire path.  This is pin-center to pin-center without
    considering diameter of pin.

    Args:
      outputFileName: File name to create.
      enableWire: Show the wire wound on the layer.
    """
    attributes = "w"
    if isAppend :
      attributes = "a"

    rubyFile = open( outputFileName, attributes )

    path3d = Path3d()
    for net in self.net :
      node = self.nodes[ net ]
      print node
      path3d.push( node.x, node.y, node.z )

    path3d.toSketchUpRuby( rubyFile )

    rubyFile.close()

  #---------------------------------------------------------------------
  def writeRubyCode(
    self,
    outputFileName,
    enablePath=True,
    enablePathLabels=False,
    enableWire=True,
    isAppend=True
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

    attributes = "w"
    if isAppend :
      attributes = "a"

    rubyFile = open( outputFileName, attributes )

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
    with open( outputFileName, "w" ) as gCodeFile :
      self.gCodePath.toG_Code( gCodeFile, layerName )

    # Create an instance of Recipe to update the header with the correct hash.
    Recipe( outputFileName, None )

  #---------------------------------------------------------------------
  def writeDefaultCalibration( self, outputFilePath, outputFileName, layerName ) :
    """
    Export node list to calibration file.

    Args:
      outputFileName: File name to create.
      layerName: Name of recipe.
    """

    calibration = LayerCalibration( layerName )
    calibration.setOffset( Location( 0, 0 ) )

    for node in self.nodes :
      calibration.setPinLocation( node, self.nodes[ node ] )

    calibration.save( outputFilePath, outputFileName )

  #---------------------------------------------------------------------
  def printStats( self ) :
    """
    Print some statistics about the layer.
    """

    print "Wire consumed:", "{:,.2f}mm".format( self.nodePath.totalLength() )
    print "G-Code lines:", len( self.gCodePath )

