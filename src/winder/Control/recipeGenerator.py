###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import sys
import math

#==============================================================================
class Location :
  """
  Location in 2d or 3d space.
  """

  #---------------------------------------------------------------------
  def __init__( self, x = 0, y = 0, z = 0 ) :
    self.x = float( x )
    self.y = float( y )
    self.z = float( z )

  #---------------------------------------------------------------------
  def center( self, location ) :
    """
    Return the center point between this and an other location.
    """
    deltaX = abs( self.x - location.x )
    deltaY = abs( self.y - location.y )
    deltaZ = abs( self.z - location.z )

    x = deltaX / 2 + min( self.x, location.x )
    y = deltaY / 2 + min( self.y, location.y )
    z = deltaY / 2 + min( self.z, location.z )

    return Location( x, y, z )

  #---------------------------------------------------------------------
  def add( self, location ) :
    """
    Add/offset this location by an other location.
    """
    return Location( self.x + location.x, self.y + location.y, self.z + location.z )

  #---------------------------------------------------------------------
  def asList( self ) :
    """
    Return the location as a list of three floating point values for X/Y/Z.
    """
    return [ self.x, self.y, self.z ]

  #---------------------------------------------------------------------
  def __str__( self ) :
    return "(" + str( self.x ) + ", " + str( self.y ) + ", " + str( self.z ) + ")"

#==============================================================================
class Segment :
  """
  A segment is two points connected by a line.
  """

  #---------------------------------------------------------------------
  def __init__( self, start, finish ) :
    self.start = start
    self.finish = finish

  #---------------------------------------------------------------------
  def deltaX( self ) :
    return self.start.x - self.finish.x

  #---------------------------------------------------------------------
  def deltaY( self ) :
    return self.start.y - self.finish.y

  #---------------------------------------------------------------------
  def deltaZ( self ) :
    return self.start.z - self.finish.z

  #---------------------------------------------------------------------
  def length( self ) :
    """
    Return the length of segment.

    Returns:
      Length of segment.
    """
    deltaX = self.deltaX()
    deltaY = self.deltaY()
    deltaZ = self.deltaZ()

    # Thank you Pythagoras.
    return sqrt( deltaX**2 + deltaY**2 + deltaZ**2 )

  #---------------------------------------------------------------------
  def slope( self ) :
    """
    Slope of X/Y.
    """
    deltaX = self.deltaX()
    deltaY = self.deltaY()

    slope = float( "inf" )
    if 0 != deltaX :
      slope = deltaY / deltaX

    return slope

  #---------------------------------------------------------------------
  def intercept( self ) :
    """
    Y-Intercept of X/Y.
    """
    return self.start.y - self.slope() * self.start.x

#==============================================================================
class Line :
  """
  2d line in the form of "m x + b" where m is the slope and b is the Y-Intercept.
  """

  #---------------------------------------------------------------------
  @staticmethod
  def fromAngle( angle, intercept ) :
    """
    Create a line from an angle and intercept.
    """
    slope = math.tan( angle )

    return Line( slope, intercept )

  #---------------------------------------------------------------------
  @staticmethod
  def fromSegment( segment ) :
    """
    Create a line from a line segment.
    """
    return Line( segment.slope(), segment.intercept() )

  #---------------------------------------------------------------------
  @staticmethod
  def fromLocationAndSlope( location, slope ) :
    """
    Create a line from a single location and a slope.
    """
    intercept = location.y - slope * location.x
    return Line( slope, intercept )

  #---------------------------------------------------------------------
  @staticmethod
  def fromLocations( start, finish ) :
    """
    Create a line from two locations.
    """
    deltaX = start.x - finish.x
    deltaY = start.y - finish.y
    slope = float( "inf" )
    if 0 != deltaX :
      slope = deltaY / deltaX

    intercept = start.y - slope * start.x

    return Line( slope, intercept )

  #---------------------------------------------------------------------
  def __init__( self, slope, intercept ) :
    """
    Constructor.

    Lines are represented in the form y = m x + b where m is the slope
    and b is the y-intercept.

    Args:
      slope - Slope of line (rise over run).
      intercept - Y-intercept of line (m x + b = 0).
    """
    self.slope = slope
    self.intercept = intercept

  #---------------------------------------------------------------------
  def intersection( self, line ) :
    """
    Return the point at which this line and an other intersect one an other.
    """
    interceptDelta = self.intercept - line.intercept
    slopeDelta = line.slope - self.slope

    x = float( "inf" )
    if 0 != slopeDelta :
      x = interceptDelta / slopeDelta

    y = self.getY( x )

    return Location( x, y )

  #---------------------------------------------------------------------
  def getY( self, x ) :
    """
    From a given X, get Y.
    """
    return x * self.slope + self.intercept

  #---------------------------------------------------------------------
  def getX( self, y ) :
    """
    From a given Y, get X.
    """
    return ( y - self.intercept ) / self.slope

  #---------------------------------------------------------------------
  def __str__( self ) :
    return "y = " + str( self.slope ) + "x + " + str( self.intercept )

#==============================================================================
class Recipe :
  net = []
  nodesA = []
  nodesB = []

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
    pin = self.net[ startPin ] - 1
    x = self.nodesA[ pin ][ 0 ]
    y = self.nodesA[ pin ][ 1 ]
    pinA = Location( x, y )

    x = self.nodesA[ pin + direction ][ 0 ]
    y = self.nodesA[ pin + direction ][ 1 ]
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
    pin = self.net[ net ] - 1
    x = self.nodesA[ pin ][ 0 ]
    y = self.nodesA[ pin ][ 1 ]
    return Location( x, y )

#==============================================================================
class Path :
  """
  A list of Location objects that define a path.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    self.path = []
    self.last = None

  #---------------------------------------------------------------------
  def pushOffset( self, location, z, radius=0, angle=0 ) :

    offsetX = radius * math.sin( angle )
    offsetY = radius * math.cos( angle )

    self.push( location.x + offsetX, location.y + offsetY, z )

  #---------------------------------------------------------------------
  def push( self, x, y, z ) :
    self.last = Location( x, y, z )
    self.path.append( self.last )

  #---------------------------------------------------------------------
  def toRuby( self ) :
    sys.stdout.write( "Sketchup.active_model.entities.add_line " )

    isFirst = True
    for point in self.path :

      # Convert millimeters to inches.  Sketch-up always works in inches.
      x = point.x / 25.4
      y = point.y / 25.4
      z = point.z / 25.4

      # Add a comma if not the first item in list.
      if not isFirst :
        sys.stdout.write( "," )
      else :
        isFirst = False

      sys.stdout.write( "[" + str( x ) + "," + str( z ) + "," + str( y ) + "]" )

    sys.stdout.write( "\r\n" )


#==============================================================================
class Layer2Recipe( Recipe ) :

  #---------------------------------------------------------------------
  def __init__( self, layout ) :
    """

      *  *  *  *  *  *  *  *
              / \/ \
    *        /  /\  \       *
           /   /  \  \
    *     /  /      \ \
        /   /        \  \   *
    *  /   /          \  \
     /   /              \ \
    *   /                \  *
     \ /                  \
      *  *  *  *  *  *  *  *

    This layer begins in the bottom right corner, runs diagonally to the
    top center, then to the bottom most pin on the far left, the left most
    pin on the bottom, one pin right of center, and the second from the bottom
    """

    #
    # Create nodes.
    # This is a list of pins starting with the bottom left corner moving in
    # a clockwise direction.
    #
    self.nodesA = []
    self.nodesB = []
    x = 0
    y = 0
    for parameter in layout.gridParameters :
      count = parameter[ 0 ]
      xInc  = parameter[ 1 ]
      yInc  = parameter[ 2 ]
      x += parameter[ 3 ]
      y += parameter[ 4 ]

      for position in range( 0, count ) :
        self.nodesA.append( [ x, y, 0 ] )
        self.nodesB.append( [ x, y, layout.depth ] )

        x += xInc
        y += yInc

      # Backup for last position.
      x -= xInc
      y -= yInc

    #
    # Create net list.
    # This is a path of node indexes specifying the order in which they are
    # connected.
    #

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      2 * layout.rows + layout.columns,
      layout.columns,
      1,
      2 * layout.rows + 2 * layout.columns - 1,
      layout.columns + 1,
      2 * layout.rows + layout.columns - 1
    ]

    # Number of items in above list.
    repeat = len( self.net )

    # Total number of pins.
    pins = 2 * layout.rows + 2 * layout.columns + 1

    # Initial direction.
    direction = 1

    # All remaining net locations are based off a simple the previous locations.
    for netNumber in range( repeat, pins ) :
      self.net.append( self.net[ netNumber - repeat ] + direction )
      direction = -direction

    #
    # Crate motions necessary to wind the above pattern.
    #

    # A wire can land in one of four locations along a pin: upper/lower
    # left/right.  The angle of these locations are defined here.
    _180 = math.radians( 180 )
    ul = -layout.angle
    ll = -layout.angle + _180
    ur = layout.angle
    lr = layout.angle + _180

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = Path()

    # The node path is a path of points that are connect together.  Used to calculate
    # the amount of wire actually dispensed.
    self.nodePath = Path()

    #
    # Initial seek position.
    #
    startLocation = Location( layout.deltaX * layout.columns, layout.wireSpacing / 2 )

    # Current net.
    net = 0
    self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, layout.angle )
    self.gCodePath.push( startLocation.x, startLocation.y, layout.startZ )
    net += 1

    for count in range( 1, 1200 / 6 ) :
      #
      # Pin 800
      # To middle pin
      #

      # Get the two pins we need to be between.
      center = self.center( net, -1 )

      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destination = wireLine.intersection( layout.lineTop )
      self.gCodePath.push( destination.x, destination.y, layout.startZ )
      self.gCodePath.push( destination.x, destination.y, layout.endZ )

      center = self.center( net, +1 )
      self.gCodePath.push( center.x, destination.y, layout.endZ )
      self.gCodePath.push( center.x, center.y - layout.overshoot, layout.endZ )

      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, lr )
      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ll )

      net += 1

      #
      # Pin 1
      # To corner pin back side
      #
      center = self.center( net, -1 )

      wireLine = Line.fromLocations( self.gCodePath.last, center )

      destination = wireLine.intersection( layout.lineBottom )
      self.gCodePath.push( destination.x, destination.y, layout.endZ )
      self.gCodePath.push( destination.x, destination.y, layout.startZ )

      #
      # Pin 1
      # To corner pin front side
      #
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.startZ )

      # Snug pin 1 but missing pin 2399
      self.gCodePath.push( center.x - layout.pinRadius + layout.overshoot, center.y, layout.startZ )

      # Hook pin 1
      self.gCodePath.push( center.x - layout.pinRadius + layout.overshoot, layout.bottom, layout.startZ )

      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ll )
      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, lr )
      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, layout.angle ) # $$$DEBUG
      net += 1

      #
      # Pin 2399
      #
      center = self.center( net, -1 )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.startZ )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.endZ )

      self.gCodePath.push( center.x, center.y + layout.overshoot, layout.endZ )

      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, ur )
      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ul )
      net += 1



      #
      # Pin 801
      #

      # Get the two pins we need to be between.
      center = self.center( net, +1 )
      #self.gCodePath.push( center.x, center.y, layout.endZ )

      wireLine = Line.fromLocations( self.gCodePath.last, center )

      destination = wireLine.intersection( layout.lineTop )
      self.gCodePath.push( destination.x, destination.y, layout.endZ )
      self.gCodePath.push( destination.x, destination.y, layout.startZ )

      center = self.center( net, +1 )
      self.gCodePath.push( center.x, destination.y, layout.startZ )
      self.gCodePath.push( center.x, center.y - layout.overshoot, layout.startZ )

      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ll )
      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, lr )
      net += 1

      #
      # Pin 1599
      # To corner pin front side
      #
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )

      destination = wireLine.intersection( layout.lineBottom )
      self.gCodePath.push( destination.x, destination.y, layout.startZ )
      self.gCodePath.push( destination.x, destination.y, layout.endZ )

      #
      #
      # Pin 1599
      # To corner pin back side
      #
      center = self.center( net, -1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.endZ )

      # Snug pin 1 but missing pin 2399
      self.gCodePath.push( center.x + layout.pinRadius - layout.overshoot, center.y, layout.endZ )

      # Hook pin 1
      self.gCodePath.push( center.x + layout.pinRadius - layout.overshoot, layout.bottom, layout.endZ )

      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, lr )
      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ul )
      net += 1

      #
      # Pin 1601
      #
      center = self.center( net, +1 )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.endZ )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.startZ )

      self.gCodePath.push( center.x, center.y + layout.overshoot, layout.startZ )

      self.nodePath.pushOffset( self.location( net ), layout.depth, layout.pinRadius, ul )
      self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, ur )
      net += 1

  #---------------------------------------------------------------------
  def printRubyCode( self ) :
    """
    Export both the G-Code and node paths to Ruby code for import into SketchUp
    for visual verification.
    """
    self.gCodePath.toRuby()
    self.nodePath.toRuby()


#==============================================================================
class LayerV_Layout :
  """
  Layout settings for the V layer.
  """

  def __init__( self ) :

    self.rows        = 400
    self.columns     = 2 * self.rows

    self.deltaX      = 8.0
    self.deltaY      = 5.75
    self.depth       = 87.7
    self.pinDiameter = 2.43
    self.pinRadius   = self.pinDiameter / 2
    self.pinHeight   = 2

    self.zClearance = 25
    self.startZ = -self.zClearance
    self.endZ   = self.depth + self.zClearance

    self.overshootAngle = 90 - 18
    self.overshoot = self.zClearance * math.tan( math.radians( self.overshootAngle ) )

    # The grid parameters are a list of parameters for how the grid is constructed.
    # Columns:
    #   Count - Number of pins this row in the table represents.
    #   dx - Change in x each iteration.
    #   dy - Change in y each iteration.
    #   off.x - Starting x offset for initial position of first pin in this set.
    #   off.y - Starting y offset for initial position of first pin in this set.
    self.gridParameters = \
    [
      # Count                    dx            dy   off.x   off.y
      [ self.rows,                0,  self.deltaY,      0,  4.463 ],
      [ self.columns,   self.deltaX,            0,  6.209,  4.462 ],
      [ self.rows - 1,            0, -self.deltaY,  2.209, -7.336 ],
      [ self.columns,  -self.deltaX,            0, -2.209, -7.339 ]
    ]

    # Location of Z-Transfer areas.
    self.top    = 2500
    self.bottom = -25
    self.left   = 0
    self.right  = 0

    # Lines defining the where a Z hand-off can take place.  Used for intercept
    # calculations.
    self.lineTop    = Line( 0, self.top )
    self.lineBottom = Line( 0, self.bottom )
    self.lineLeft   = Line( self.left, 0 )
    self.lineRight  = Line( self.right, 0 )

    # Typical slope of lines.
    self.slope = self.deltaY / self.deltaX

    # Primary angle.
    self.angle = math.atan( self.deltaY / self.deltaX )

    # Distance between wires.
    self.wireSpacing = \
      self.deltaY / math.sqrt( self.deltaY**2 / self.deltaX**2 + 1 )

#------------------------------------------------------------------------------
if __name__ == "__main__":

  layout = LayerV_Layout()
  recipe = Layer2Recipe( layout )

  recipe.printRubyCode()
