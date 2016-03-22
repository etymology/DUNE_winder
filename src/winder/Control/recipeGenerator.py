###############################################################################
# Name: recipeGenerator.py
# Uses: G-Code generator.
# Date: 2016-02-18
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import sys
import math
import random

#==============================================================================
class Location :
  """
  Location in 2d or 3d space.
  """

  #---------------------------------------------------------------------
  def __init__( self, x = 0, y = 0, z = 0 ) :
    """
    Constructor.

    Args:
      x: Position on the x-axis.
      y: Position on the y-axis.
      z: Position on the z-axis.
    """
    self.x = float( x )
    self.y = float( y )
    self.z = float( z )

  #---------------------------------------------------------------------
  def center( self, location ) :
    """
    Return the center point between this and an other location.

    Args:
      location: The second location to center between.

    Returns:
      Instance of Location with the center point.
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

    Args:
      location: Location to add to this instance.

    Returns:
      Instance of Location with results of add.

    Note:
      Does not modify self.
    """
    return Location( self.x + location.x, self.y + location.y, self.z + location.z )

  #---------------------------------------------------------------------
  def asList( self ) :
    """
    Return the location as a list of three floating point values for X/Y/Z.

    Returns:
      A list with 3 elements, [ x, y, z ].
    """
    return [ self.x, self.y, self.z ]

  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Get a string representation of object.

    Returns
      String representation of object in form (x, y, z) where x/y/z are
      numbers.
    """

    return "(" + str( self.x ) + ", " + str( self.y ) + ", " + str( self.z ) + ")"

#==============================================================================
class Segment :
  """
  A segment is two points connected by a line.
  """

  #---------------------------------------------------------------------
  def __init__( self, start, finish ) :
    """
    Constructor.

    Args:
      start: Instance of Location defining the starting location.
      finish: Instance of Location defining the finishing location.
    """
    self.start = start
    self.finish = finish

  #---------------------------------------------------------------------
  def deltaX( self ) :
    """
    Get the distance between x of segment.

    Returns:
      Distance between x of segment.
    """
    return self.start.x - self.finish.x

  #---------------------------------------------------------------------
  def deltaY( self ) :
    """
    Get the distance between y of segment.

    Returns:
      Distance between y of segment.
    """
    return self.start.y - self.finish.y

  #---------------------------------------------------------------------
  def deltaZ( self ) :
    """
    Get the distance between z of segment.

    Returns:
      Distance between z of segment.
    """
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
    return math.sqrt( deltaX**2 + deltaY**2 + deltaZ**2 )

  #---------------------------------------------------------------------
  def slope( self ) :
    """
    Slope of X/Y.

    Returns:
      Slope of the X/Y part of the line.  Returns infinite if there is no
      slope (i.e. no delta X).
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

    Returns:
      Y-Intercept of X/Y.  Returns infinite if there is no
      slope (i.e. no delta X).
    """
    return self.start.y - self.slope() * self.start.x

  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Get a string representation of object.

    Returns
      String representation of object in form (x1, y1, z1)-(x2, y2, z2) where
      xn/yn/zn are numbers and n is 1 for starting location, 2 for finishing.
    """
    return str( self.start ) + "-" + str( self.finish )

#==============================================================================
class Line :
  """
  2d line in the form of "m x + b" where m is the slope and b is the Y-Intercept.
  """

  #---------------------------------------------------------------------
  @staticmethod
  def fromAngle( angle, intercept ) :
    """
    Create a line from an angle and intercept, or vector.

    Args:
      angle: Angle in radians.
      intercept: Y-intercept.

    Returns:
      Instance of Line.
    """
    slope = math.tan( angle )

    return Line( slope, intercept )

  #---------------------------------------------------------------------
  @staticmethod
  def fromSegment( segment ) :
    """
    Create a line from a line segment.  Useful for extending line segments.

    Args:
      segment: Instance of Segment to create line from.

    Returns:
      Instance of Line.
    """
    return Line( segment.slope(), segment.intercept() )

  #---------------------------------------------------------------------
  @staticmethod
  def fromLocationAndSlope( location, slope ) :
    """
    Create a line from a single location and a slope.

    Args:
      location: Instance of Location as a known point along the line.
      slope: The slope of the line.

    Returns:
      Instance of Line.
    """
    intercept = location.y - slope * location.x
    return Line( slope, intercept )

  #---------------------------------------------------------------------
  @staticmethod
  def fromLocations( start, finish ) :
    """
    Create a line from two locations.

    Args:
      start: Instance of Location for the starting position.
      finish: Instance of Location for the finishing position.

    Returns:
      Instance of Line.
    """
    # $$$OLD deltaX = start.x - finish.x
    # $$$OLD deltaY = start.y - finish.y
    # $$$OLD slope = float( "inf" )
    # $$$OLD if 0 != deltaX :
    # $$$OLD   slope = deltaY / deltaX
    # $$$OLD
    # $$$OLD intercept = start.y - slope * start.x
    # $$$OLD
    # $$$OLD return Line( slope, intercept )
    segment = Segment( start, finish )
    return Line.fromSegment( segment )

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

    Args:
      line: Instance of Line to check for intersection.

    Returns:
      Instance of Location with the point of the intersection.  The location
      will have infinite values for x and y if there is no intersection (i.e.
      the lines are parallel).
    """

    interceptDelta = self.intercept - line.intercept

    x = float( "inf" )
    y = float( "inf" )

    if float( "inf" ) == line.slope or float( "inf" ) == self.slope :
      if line.slope != self.slope :
        if float( "inf" ) == line.slope :
          x = line.intercept
        else :
          x = self.intercept

        y = self.getY( x )
    else :
      slopeDelta = line.slope - self.slope

      # If we have a slope and it is a number.
      if 0 != slopeDelta and slopeDelta == slopeDelta :
        x = interceptDelta / slopeDelta

      y = self.getY( x )

    return Location( x, y )

  #---------------------------------------------------------------------
  def getY( self, x ) :
    """
    From a given X, get Y.

    Args:
      x: X position along line.

    Returns:
      The y position corresponding to this x position.  Returns infinite if
      the line is horizontal.
    """
    return x * self.slope + self.intercept

  #---------------------------------------------------------------------
  def getX( self, y ) :
    """
    From a given Y, get X.

    Args:
      y: Y position along line.

    Returns:
      The x position corresponding to this y position.  Returns infinite if
      the line is horizontal.
    """
    return ( y - self.intercept ) / self.slope

  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Get a string representation of object.

    Returns
      String representation of object in form y = m x + b where m is the
      slope, and b is the intercept.
    """
    return "y = " + str( self.slope ) + "x + " + str( self.intercept )

#==============================================================================
class Recipe :
  """
  Base recipe class.
  """

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

#==============================================================================
class Path :
  """
  A list of Location objects that define a path.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """
    self.path = []
    self.last = None

  #---------------------------------------------------------------------
  def pushOffset( self, location, z, radius=0, angle=0 ) :
    """
    Add an offset position to path.  Offset specified as a radius and angle.

    Args:
      location: Instance of Location specifying 2d location (z is ignored).
      z: The z-coordinate.
      radius: Radius to offset by.
      angle: Angle of offset.

    Returns:
      The length between this new position and the previous position.
    """
    offsetX = radius * math.sin( angle )
    offsetY = radius * math.cos( angle )

    return self.push( location.x + offsetX, location.y + offsetY, z )

  #---------------------------------------------------------------------
  def push( self, x, y, z ) :
    """
    Add an offset position to path.  Offset specified as a radius and angle.

    Args:
      x: The x-coordinate.
      y: The y-coordinate.
      z: The z-coordinate.

    Returns:
      The length between this new position and the previous position.
    """
    location = Location( x, y, z )
    self.path.append( location )

    segment = Segment( self.last, location )

    length = 0
    if None != self.last :
      length = segment.length()

    self.last = location

    return length

  #---------------------------------------------------------------------
  def toSketchUpRuby( self, output ) :
    """
    Turn path into Ruby code for use in SketchUp.  Useful for visualizing
    paths.

    Args:
      output: Open file for output.
    """

    output.write( "Sketchup.active_model.entities.add_line " )

    isFirst = True
    for point in self.path :

      # Convert millimeters to inches.  Sketch-up always works in inches.
      x = point.x / 25.4
      y = point.y / 25.4
      z = point.z / 25.4

      # Add a comma if not the first item in list.
      if not isFirst :
        output.write( "," )
      else :
        isFirst = False

      output.write( "[" + str( x ) + "," + str( z ) + "," + str( y ) + "]" )

    output.write( "\r\n" )

#==============================================================================
class G_Code :
  """
  Base object for a G-Code instruction.
  """

  #---------------------------------------------------------------------
  def __init__( self, gCode, parameters ) :
    """
    Constructor.

    Args:
      gCode: The G-Code function number (integer).
      parameters: A list of parameters for the function.
    """
    self._gCode = gCode
    self._parameters = parameters

  #---------------------------------------------------------------------
  def toG_Code( self ) :
    """
    Translate object into G-Code text.

    Returns:
      String of G-Code text.
    """
    result = "G" + str( self._gCode )

    for parameter in self._parameters :
      result += " P" + str( parameter )

    return result

#==============================================================================
class LatchG_Code( G_Code ) :
  """
  G-Code to set the Z latch position.
  """

  # Sides of the machine.
  FRONT = 0
  BACK  = 1

  #---------------------------------------------------------------------
  def __init__( self, side ) :
    """
    Constructor.

    Args:
      side: Which side (FRONT/BACK) to latch to.
    """
    G_Code.__init__( self, 100, [ side ] )

#==============================================================================
class WireLengthG_Code( G_Code ) :
  """
  G-Code to specify the amount of wire consumed by a move.
  """

  #---------------------------------------------------------------------
  def __init__( self, length ) :
    """
    Constructor.

    Args:
      length: How much wire was consumed by this motion.
    """
    G_Code.__init__( self, 101, [ length ] )

#==============================================================================
class SeekTransferG_Code( G_Code ) :
  """
  A seek transfer will instruct the target to follow the slope of the line
  until it reaches a Z transfer area.
  """

  # Various seek locations.  Bitmap.
  TOP          = 1
  BOTTOM       = 2
  LEFT         = 4
  RIGHT        = 8
  TOP_LEFT     = 1 + 4
  TOP_RIGHT    = 1 + 8
  BOTTOM_LEFT  = 2 + 4
  BOTTOM_RIGHT = 2 + 8

  #---------------------------------------------------------------------
  def __init__( self, seekLocation ) :
    """
    Constructor.

    Args:
      seekLocation: One (or more) of the seek seek locations.
    """
    G_Code.__init__( self, 102, [ seekLocation ] )
    self._seekLocation = seekLocation

  def seekLocationName( self ) :
    """
    Return the seek location name for this object.

    Returns:
      String of seek location.
    """
    location = ""

    if self._seekLocation & SeekTransferG_Code.TOP :
      location += "top "

    if self._seekLocation & SeekTransferG_Code.BOTTOM :
      location += "bottom "

    if self._seekLocation & SeekTransferG_Code.LEFT :
      location += "left "

    if self._seekLocation & SeekTransferG_Code.RIGHT :
      location += "right "

    return location.strip()


#==============================================================================
class GCodePath( Path ) :
  """
  A specific path that includes G-Code instructions.
  """

  # Dictionary of what G-Code functions are mapped to what path locations.
  # The dictionary key is the index into self.path at which the G-Code functions
  # occur.  Each dictionary entry contains a list of GCode objects.
  _gCode = {}

  #---------------------------------------------------------------------
  def pushG_Code( self, gCode ) :
    """
    Add a G-Code function to the next path entry.  Call before calling any
    'push' functions.  Can be called more than once per path point.

    Args:
      gCode: Instance of G_Code to insert.
    """
    index = len( self.path )
    if index in self._gCode :
      self._gCode[ index ].append( gCode )
    else :
      self._gCode[ index ] = [ gCode ]

  #---------------------------------------------------------------------
  def toG_Code( self, output, name, isCommentOut=False ) :
    """
    Turn path into G-Code text.

    Args:
      output: Open file to place output.
      name: Name to put in header of G-Code file.
      isCommendOut: Deprecated.  Leave False.
    """
    if isCommentOut :
      output.write( "# " )

    output.write( "( " + name + " )\r\n" )
    lineNumber = 1

    lastX = None
    lastY = None
    lastZ = None

    for index, point in enumerate( self.path ) :
      if isCommentOut :
        output.write( "# " )

      output.write( "N" + str( lineNumber ) )

      if lastX != point.x :
        output.write( " X" + str( point.x ) )
        lastX = point.x

      if lastY != point.y :
        output.write( " Y" + str( point.y ) )
        lastY = point.y

      if lastZ != point.z :
        output.write( " Z" + str( point.z ) )
        lastZ = point.z

      if index in self._gCode :
        for gCode in self._gCode[ index ] :
          output.write( " " + gCode.toG_Code() )

      output.write( "\r\n" )
      lineNumber += 1

  #---------------------------------------------------------------------
  def _pointLabel( self, output, location, text ) :
    """
    Make a SketchUp label at specified location.

    Args:
      output: Open file for output.
      location: The location to label.
      text: The text to place on this label.
    """
    x = location.x / 25.4
    y = location.y / 25.4
    z = location.z / 25.4

    output.write(
      'point = Geom::Point3d.new [ '
        + str( x ) + ','
        + str( z ) + ','
        + str( y ) + ' ]'
        + "\r\n" )

    x = random.uniform( -3, 3 )
    y = random.uniform( -3, 3 )

    output.write( 'vector = Geom::Vector3d.new ' + str( x ) + ',0,' + str( y ) + "\r\n" )
    output.write( 'Sketchup.active_model.entities.add_text "'
      + text + '", point, vector' + "\r\n" )

  #---------------------------------------------------------------------
  def toSketchUpRuby( self, output, enableLables=True ) :
    """
    Turn path into Ruby code for use in SketchUp.  Labels G-Code functions.
    Useful for visualizing paths.

    Args:
      output: Open file for output.
    """
    Path.toSketchUpRuby( self, output )

    if enableLables :
      for index, gCodeList in self._gCode.iteritems() :

        location = self.path[ index ]

        for gCode in gCodeList :
          if isinstance( gCode, LatchG_Code ) :
            side = "front"
            if LatchG_Code.BACK == gCode._parameters[ 0 ] :
              side = "back"
            self._pointLabel( output, location, "Z-latch " + side )

          if isinstance( gCode, SeekTransferG_Code ) :
            self._pointLabel( output, location, "Seek transfer" )

#==============================================================================
class LayerV_Recipe( Recipe ) :
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

  #---------------------------------------------------------------------
  def __init__( self, layout ) :
    """
    Constructor.  Does all calculations.

    Args:
      layout: Instance of LayerV_Layout that specifies parameters for recipe
        generation.
    """

    self.nodesFront = []
    self.nodesBack = []

    #----------------------------------
    # Create nodes.
    # This is a list of pins starting with the bottom left corner moving in
    # a clockwise direction.
    #----------------------------------
    x = 0
    y = 0
    for parameter in layout.gridParameters :
      count = parameter[ 0 ]
      xInc  = parameter[ 1 ]
      yInc  = parameter[ 2 ]
      x += parameter[ 3 ]
      y += parameter[ 4 ]

      for position in range( 0, count ) :
        self.nodesFront.append( Location( x, y, 0 ) )
        self.nodesBack.append( Location( x, y, layout.depth ) )

        x += xInc
        y += yInc

      # Backup for last position.
      x -= xInc
      y -= yInc

    #----------------------------------
    # Create net list.
    # This is a path of node indexes specifying the order in which they are
    # connected.
    #----------------------------------

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      2 * layout.rows + layout.columns - 1,
      layout.columns - 1,
      0,
      2 * layout.rows + 2 * layout.columns - 2,
      layout.columns,
      2 * layout.rows + layout.columns - 2
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

    #----------------------------------
    # Crate motions necessary to wind the above pattern.
    #----------------------------------

    # A wire can land in one of four locations along a pin: upper/lower
    # left/right.  The angle of these locations are defined here.
    _180 = math.radians( 180 )
    ul = -layout.angle
    ll = -layout.angle + _180
    ur = layout.angle
    lr = layout.angle + _180

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = GCodePath()

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
    self.gCodePath.push( startLocation.x, startLocation.y, layout.frontZ )
    net += 1

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = layout.pins / ( 2 * 6 )
    #totalCount = 5     # $$$DEBUG

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for count in range( 1, totalCount + 1 ) :
      #
      # To upper middle moving from lower-right to upper-left starting on front side.
      #

      # Get the two pins we need to be between.
      center = self.center( net, -1 )

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Front,
          layout.pinRadius,
          lr
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ll
        )

      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destination = wireLine.intersection( layout.lineTop )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code( SeekTransferG_Code.TOP ) )
      self.gCodePath.push( destination.x, destination.y, layout.frontZ )
      self.gCodePath.push( destination.x, destination.y, layout.partialZ_Front ) # Partial Z

      center = self.center( net, +1 )
      self.gCodePath.push( center.x, destination.y, layout.partialZ_Front )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( center.x, destination.y, layout.backZ )
      self.gCodePath.push( center.x, center.y - layout.overshoot, layout.backZ )

      net += 1

      #
      # To lower left column moving from upper-right to lower-left starting on back side.
      #

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ll
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Front,
          layout.pinRadius,
          layout.angle
        )

      # Pin on lower rear left.
      center = self.center( net, -1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destinationA = wireLine.intersection( layout.lineBottom )
      destinationB = wireLine.intersection( layout.lineLeft )

      if destinationA.x > destinationB.x :
        destination = destinationA
      else :
        destination = destinationB

      self.gCodePath.pushG_Code( SeekTransferG_Code( SeekTransferG_Code.BOTTOM_LEFT ) )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( destination.x, destination.y, layout.backZ )
      self.gCodePath.push( destination.x, destination.y, layout.partialZ_Back )  # Partial Z

      # To second pin on lower front left.
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.partialZ_Back )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.frontZ )
      self.gCodePath.push(
        center.x - layout.pinRadius + layout.overshoot,
        center.y,
        layout.frontZ
      )

      self.gCodePath.push(
        center.x - layout.pinRadius + layout.overshoot,
        layout.bottom,
        layout.frontZ
      )

      net += 1

      #
      # To lower left row moving from upper-left to lower-right starting on front side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Front,
          layout.pinRadius,
          ur
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ul
        )

      center = self.center( net, -1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.frontZ )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.backZ )

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.backZ )
      self.gCodePath.push( center.x, center.y + layout.overshoot, layout.backZ )

      net += 1

      #
      # To upper middle from lower-left to upper-right starting on back side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ll
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Front,
          layout.pinRadius,
          lr
        )

      # Get the two pins we need to be between.
      center = self.center( net, +1 )

      wireLine = Line.fromLocations( self.gCodePath.last, center )

      destination = wireLine.intersection( layout.lineTop )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( destination.x, destination.y, layout.backZ )
      self.gCodePath.push( destination.x, destination.y, layout.partialZ_Back ) # Partial Z

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, destination.y, layout.partialZ_Back )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( center.x, destination.y, layout.frontZ )

      self.gCodePath.push( center.x, center.y - layout.overshoot, layout.frontZ )

      net += 1

      #
      # To lower right column from upper-left to lower-right starting on front side.
      #

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Front,
          layout.pinRadius,
          lr
        )
      location = self.location( net )
      location.x += layout.rightExtention + layout.pinRadius
      length2  = \
        self.nodePath.pushOffset(
          location,
          layout.partialZ_Front,
          layout.pinRadius,
          ll
        )

      length2 += \
        self.nodePath.pushOffset( location, layout.partialZ_Back, layout.pinRadius, lr )
      length2 += \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ul
        )

      # Lower right front side.
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destinationA = wireLine.intersection( layout.lineBottom )
      destinationB = wireLine.intersection( layout.lineRight )

      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      if destinationA.x < destinationB.x :
        destination = destinationA
        self.gCodePath.push( destination.x, destination.y, layout.frontZ )
        self.gCodePath.push( destination.x, destination.y, layout.partialZ_Front )
        self.gCodePath.push( destinationB.x, destination.y, layout.partialZ_Front )
      else :
        destination = destinationB
        self.gCodePath.push( destination.x, destination.y, layout.frontZ )
        self.gCodePath.push( destination.x, destination.y, layout.partialZ_Front )

      # Lower right backside.
      center = self.center( net, -1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.partialZ_Front )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, layout.backZ )
      self.gCodePath.push(
        center.x + layout.pinRadius - layout.overshoot,
        center.y,
        layout.backZ
      )

      self.gCodePath.push(
        center.x + layout.pinRadius - layout.overshoot,
        layout.bottom,
        layout.backZ
      )

      net += 1

      #
      # Lower right row from lower-right to lower-left starting on back side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          layout.partialZ_Back,
          layout.pinRadius,
          ul
        )

      length2 = self.nodePath.pushOffset( self.location( net ), 0, layout.pinRadius, ur )

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.backZ )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.frontZ )

      center = self.center( net, -1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, layout.frontZ )
      self.gCodePath.push( center.x, center.y + layout.overshoot, layout.frontZ )

      net += 1

  #---------------------------------------------------------------------
  def printRubyCode( self ) :
    """
    Export both the G-Code and node paths to Ruby code for import into SketchUp
    for visual verification.
    """
    self.gCodePath.toSketchUpRuby( sys.stdout, False )

    gCodeFile = open( "vLayerG_Code.txt", "w" )
    self.gCodePath.toG_Code( gCodeFile, "Layer V" )
    self.nodePath.toSketchUpRuby( sys.stdout )

class LayerLayout :
  """
  Layout parameters common to all layers.
  """

  def __init__( self, divide = 1 ) :
    """
    Constructor.

    Args:
      divide: Scale factor to divide down layer (not functional).
    """
    self.rows        = 400 / divide
    self.columns     = 2 * self.rows
    self.pins        = 2 * self.rows + 2 * self.columns - 1

    # Data about the pins.
    self.pinDiameter = 2.43
    self.pinRadius   = self.pinDiameter / 2
    self.pinHeight   = 2

    # Location of Z-Transfer areas.
    # Top/bottom for Y, left/right for X.
    self.top    = 2500
    self.bottom = -25
    self.left   = -250
    self.right  = 6800

    # How big the Z-transfer windows are.
    # The Z-transfer windows start at top/bottom/left/right locations.
    self.zWindow = 20

    # Lines defining the where a Z hand-off can take place.  Used for intercept
    # calculations.
    self.lineTop    = Line( 0, self.top )
    self.lineBottom = Line( 0, self.bottom )
    self.lineLeft   = Line( float( "inf" ), self.left )
    self.lineRight  = Line( float( "inf" ), self.right )

#==============================================================================
class LayerV_Layout( LayerLayout ) :
  """
  Layout settings for the V-layer.
  """

  def __init__( self, divide = 1 ) :
    """
    Constructor.

    Args:
      divide: Scale factor to divide down layer (not functional).
    """

    LayerLayout.__init__( self, divide )

    # Spacing between pins and front to back.
    self.deltaX      = 8.0   * divide
    self.deltaY      = 5.75  * divide
    self.depth       = 87.7

    # Distance from the layer to the head.
    self.zClearance = 25
    self.frontZ = -self.zClearance
    self.backZ   = self.depth + self.zClearance

    # Travel for partial Z.  Should place head level with board and below pin
    # height.
    self.partialZ_Front = 0
    self.partialZ_Back  = self.depth

    # The wing on the right is extra distance the wire must wrap around.
    self.rightExtention = 304.29

    # Distance that must be traveled past a pin to ensure it will be hooked
    # by the wire when moving in an other direction.
    # Doing some manual checks, I found 18 degrees is a good number that will
    # maximize the amount of contact of wire to the pin and still clear any
    # neighboring pins.
    overshootAngle = 90 - 18
    self.overshoot = self.zClearance * math.tan( math.radians( overshootAngle ) )

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

    # Typical slope of lines.
    self.slope = self.deltaY / self.deltaX

    # Primary angle (in radians) between wires.
    self.angle = math.atan( self.deltaY / self.deltaX )

    # Distance between wires.
    self.wireSpacing = \
      self.deltaY / math.sqrt( self.deltaY**2 / self.deltaX**2 + 1 )

#------------------------------------------------------------------------------
if __name__ == "__main__":

  layout = LayerV_Layout()
  recipe = LayerV_Recipe( layout )

  recipe.printRubyCode()
