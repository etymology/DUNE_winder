###############################################################################
# Name: LayerGX_Recipe.py
# Uses: Common functions shared by G and X layer recipe.
# Date: 2016-04-12
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Location import Location

from .G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from .G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from .G_CodeFunctions.AnchorPointG_Code import AnchorPointG_Code

from .RecipeGenerator import RecipeGenerator
from .HeadPosition import HeadPosition
from .Path3d import Path3d
from .G_CodePath import G_CodePath

class LayerGX_Recipe( RecipeGenerator ) :

  #---------------------------------------------------------------------
  def _pinName( self, side, startingPin, offset ) :
    """
    Get the name of a pin using side, starting number, and offset.

    Args:
      side: Front or back (F/B).
      startingPin: Where numbering begins.
      offset: Number to add to starting pin.

    Returns:
      Name of pin in form "snnnn" where s is the side and n is the pin number
      (not zero padded).
    """
    pin  = startingPin + offset
    pin %= self.geometry.pins
    pin += 1

    return side + str( pin )

  #---------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None, firstPinScale=1.0/2 ) :
    """
    Constructor.

    Args:
      geometry - Instance (or child) of UV_LayerGeometry.
    """
    RecipeGenerator.__init__( self, geometry )

    #
    # Create nodes and net.
    #

    # The x position of the two columns on either side of frame.
    xColumnA = self.geometry.leftEdge
    xColumnB = self.geometry.rightEdge

    # The z position of the two sides of the frame.
    zSideA = self.geometry.mostlyRetract
    zSideB = self.geometry.mostlyExtend

    # Starting pinOffset numbers, side/column.
    # startAA = 0
    # startBA = self.geometry.pins / 2 - 1
    # startAB = self.geometry.pins - 1
    # startBB = self.geometry.pins / 2
    startAA = self.geometry.pins / 2
    startBA = self.geometry.pins - 1
    startAB = self.geometry.pins / 2 - 1
    startBB = 0

    # Pin counting direction, side/column.
    directionAA = +1
    directionBA = -1
    directionAB = -1
    directionBB = +1

    y = self.geometry.pinSpacing * firstPinScale
    for pinOffset in range( 0, self.geometry.pins / 2 ) :

      # Side A, column A.
      pinNameAA = self._pinName( "F", startAA, directionAA * pinOffset )
      self.nodes[ pinNameAA ] = Location( xColumnA, y, zSideA )

      # Side B, column A.
      pinNameBA = self._pinName( "B", startBA, directionBA * pinOffset )
      self.nodes[ pinNameBA ] = Location( xColumnA, y, zSideB )

      # Side A, column B.
      pinNameAB = self._pinName( "F", startAB, directionAB * pinOffset )
      self.nodes[ pinNameAB ] = Location( xColumnB, y, zSideA )

      # Side B, column B.
      pinNameBB = self._pinName( "B", startBB, directionBB * pinOffset )
      self.nodes[ pinNameBB ] = Location( xColumnB, y, zSideB )

      self.centering[ pinNameAA ] = 0
      self.centering[ pinNameBA ] = 0
      self.centering[ pinNameAB ] = 0
      self.centering[ pinNameBB ] = 0

      # Add pins to the net list.
      self.net.append( pinNameAA )
      self.net.append( pinNameBA )
      self.net.append( pinNameAB )
      self.net.append( pinNameBB )

      y += self.geometry.pinSpacing

    #
    # Create net list.  This is a path of node indexes specifying the order in which they are
    # connected.
    #

    self.gCodePath = G_CodePath()
    self.z = HeadPosition( self.gCodePath, self.geometry, HeadPosition.FRONT )

    # Current net.
    self.netIndex = 0

    startLocation = self.location( self.netIndex )
    self.nodePath.push( startLocation.x, startLocation.y, self.geometry.mostlyRetract )
    self.basePath.push( startLocation.x, startLocation.y, self.geometry.mostlyRetract )
    lastLocation = startLocation
    lastNet = self.net[ 0 ]

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = self.geometry.pins * 2
    halfCount = totalCount / 2

    if windsOverride :
      totalCount = windsOverride
      halfCount = totalCount / 2

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for self.netIndex in xrange( 1, totalCount + 1, 2 ) :

      if self.netIndex < len( self.net ) :

        # Push the anchor point of the last placed wire.
        self.gCodePath.pushG_Code( AnchorPointG_Code( lastNet, "0" ) )

        # Location of the the next pinOffset.
        location = self.location( self.netIndex )

        # Add the pinOffset location to the base path and node path (they are
        # identical for these layers).
        self.basePath.push( location.x, location.y, location.z )
        length = self.nodePath.push( location.x, location.y, location.z )

        # Push a G-Code length function to the next G-Code command to specify the
        # amount of wire consumed by this move.
        self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
        self.gCodePath.pushG_Code( self.pinCenterTarget( "XY" ) )
        self.gCodePath.pushG_Code( SeekTransferG_Code() )
        self.gCodePath.push()

        self.z.set( HeadPosition.OTHER_SIDE )

        if lastLocation.y != location.y :
          self.gCodePath.pushG_Code( self.pinCenterTarget( "Y" ) )
          self.gCodePath.push()

        if halfCount == self.netIndex :
          self.firstHalf = self.gCodePath
          self.gCodePath = G_CodePath()
          self.gCodePath.last = lastLocation
          self.gCodePath.push(
            location.x,
            location.y,
            self.geometry.retracted
          )
          self.z = HeadPosition( self.gCodePath, self.geometry, HeadPosition.FRONT )

        lastLocation = location
        lastNet = self.net[ self.netIndex ]

    self.secondHalf = self.gCodePath
    self.gCodePath = None
