###############################################################################
# Name: G_CodePath.py
# Uses: A specific path that includes G-Code instructions.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import random

from Path3d import Path3d
from G_CodeFunctions.LatchG_Code import LatchG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code

class G_CodePath( Path3d ) :
  """
  A specific path that includes G-Code instructions.
  """

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """
    Path3d.__init__( self )

    # Dictionary of what G-Code functions are mapped to what path locations.
    # The dictionary key is the index into self.path at which the G-Code functions
    # occur.  Each dictionary entry contains a list of G_Code objects.
    self._gCode = {}
    self._seekForceX = []
    self._seekForceY = []
    self._seekForceZ = []

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
  def pushSeekForce( self, forceX=False, forceY=False, forceZ=False ) :
    """
    Force one or more of the axises to print their position.  Needed when an
    edge seek has been done.

    Args:
      forceX - Cause X position is output.
      forceY - Cause Y position is output.
      forceZ - Cause Z position is output.
    """
    index = len( self.path )
    if forceX :
      self._seekForceX.append( index )

    if forceY :
      self._seekForceY.append( index )

    if forceZ :
      self._seekForceZ.append( index )

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

      if index in self._seekForceX :
        lastX = None

      if index in self._seekForceY :
        lastY = None

      if index in self._seekForceZ :
        lastZ = None

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
    Path3d.toSketchUpRuby( self, output )

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
