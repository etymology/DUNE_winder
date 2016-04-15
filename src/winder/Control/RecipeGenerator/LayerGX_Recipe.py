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

from .RecipeGenerator import RecipeGenerator
from .HeadPosition import HeadPosition
from .Path3d import Path3d
from .G_CodePath import G_CodePath

class LayerGX_Recipe( RecipeGenerator ) :

  #---------------------------------------------------------------------
  def __init__( self, geometry, windsOverride=None, firstPinScale=1.0/2 ) :
    """
    Constructor.

    Args:
      geometry - Instance (or child) of UV_LayerGeometry.
    """
    RecipeGenerator.__init__( self, geometry )

    self.basePath = Path3d()

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = G_CodePath()

    # The node path is a path of points that are connect together.  Used to calculate
    # the amount of wire actually dispensed.
    frameOffset = \
      Location( geometry.apaOffsetX, geometry.apaOffsetY, geometry.apaOffsetZ )

    self.nodePath = Path3d( frameOffset )

    self.centering = {}

    #
    # Create nodes and net.
    # Nodes are a list of pins starting with the bottom left corner moving in
    # a clockwise direction.  The net is a path of node indexes specifying the
    # order in which they are connected.
    #

    xLeft  = self.geometry.leftEdge
    xRight = self.geometry.rightEdge
    y = self.geometry.pinSpacing * firstPinScale

    for pin in range( 1, self.geometry.pins / 2 + 1 ) :

      # Front left.
      location = Location( xLeft, y, self.geometry.partialZ_Front )
      pinNameA = "F" + str( pin )
      self.nodes[ pinNameA ] = location

      # Rear left.
      location = Location( xLeft, y, self.geometry.partialZ_Back )
      pinNumber = ( self.geometry.pins / 2 - pin + 1 ) % self.geometry.pins
      pinNameB = "B" + str( pinNumber )
      self.nodes[ pinNameB ] = location

      # Front right.
      location = Location( xRight, y, self.geometry.partialZ_Front )
      pinNumber = self.geometry.pins - pin + 1
      pinNameC = "F" + str( pinNumber )
      self.nodes[ pinNameC ] = location

      # Rear right.
      location = Location( xRight, y, self.geometry.partialZ_Back )
      pinNumber = pin + self.geometry.pins / 2 #( self.geometry.pins / 2 + pinNumber + 1 )
      pinNameD = "B" + str( pinNumber )
      self.nodes[ pinNameD ] = location

      self.centering[ pinNameA ] = 0
      self.centering[ pinNameB ] = 0
      self.centering[ pinNameC ] = 0
      self.centering[ pinNameD ] = 0

      # Add pins to the net list.
      self.net.append( pinNameA )
      self.net.append( pinNameC )
      self.net.append( pinNameD )
      self.net.append( pinNameB )

      y += self.geometry.pinSpacing

    #
    # Create net list.  This is a path of node indexes specifying the order in which they are
    # connected.
    #


    #self.printNodes()
    #self.printNet()

    self.z = HeadPosition( self.gCodePath, self.geometry, HeadPosition.FRONT )

    # Current net.
    self.netIndex = 0

    #net = self.net[ self.netIndex ]
    #orientation = self.orientations[ net ]
    #
    #self.nodePath.pushOffset(
    #  self.location( self.netIndex ),
    #  self.geometry.pinRadius,
    #  self.orientations[ net ]
    #)
    startLocation = self.location( self.netIndex )
    self.gCodePath.push( startLocation.x, startLocation.y, self.geometry.frontZ )
    self.nodePath.push( startLocation.x, startLocation.y, 0 )
    self.basePath.push( startLocation.x, startLocation.y, 0 )
    lastLocation = startLocation

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = self.geometry.pins * 2

    if windsOverride :
      totalCount = windsOverride

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for _ in range( 1, totalCount + 1 ) :

      self.netIndex += 1
      if self.netIndex < len( self.net ) :

        # Location of the the next pin.
        location = self.location( self.netIndex )

        # Add the pin location to the base path and node path (they are
        # identical for these layers).
        self.basePath.push( location.x, location.y, location.z )
        length = self.nodePath.push( location.x, location.y, location.z )

        # Push a G-Code length function to the next G-Code command to specify the
        # amount of wire consumed by this move.
        self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
        self.gCodePath.pushG_Code( self.pinCenterTarget( "X" ) )
        self.gCodePath.pushG_Code( SeekTransferG_Code() )
        self.gCodePath.push()

        self.z.set( HeadPosition.OTHER_SIDE )

        if lastLocation.y != location.y :
          self.gCodePath.pushG_Code( self.pinCenterTarget( "Y" ) )
          self.gCodePath.push()

        lastLocation = location


    #self.gCodePath.push( startLocation.x, startLocation.y, self.geometry.frontZ )
    #self.basePath.push( startLocation.x, startLocation.y, self.geometry.frontZ )


