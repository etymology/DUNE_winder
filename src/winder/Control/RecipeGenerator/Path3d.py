###############################################################################
# Name: Path3d.py
# Uses: A list of Location objects that define a path.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment

class Path3d :
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

  #---------------------------------------------------------------------
  def totalLength( self ) :
    """
    Get the total length of path.

    Returns:
      Total length of path.
    """
    length = 0
    lastPoint = self.path[ 0 ]
    for point in self.path[ 1: ] :
      segment = Segment( lastPoint, point )
      length += segment.length()
      lastPoint = point

    return length

  #---------------------------------------------------------------------
  def __len__( self ) :
    """
    Return number of nodes in path.

    Returns:
      Number of nodes in path.
    """
    return len( self.path )
