###############################################################################
# Name: G_CodeToPath.py
# Uses: Convert G-Code to a 3d G-Code path.
# Date: 2016-03-30
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import random

from Library.G_Code import G_Code

from Library.Geometry.Location import Location

from Machine.G_Codes import G_Codes
from Machine.G_CodeHandlerBase import G_CodeHandlerBase

from .G_CodePath import G_CodePath
from .G_CodeFunctions.G_CodeFunction import G_CodeFunction

class G_CodeToPath( G_CodeHandlerBase ) :

  #---------------------------------------------------------------------
  def __init__( self, fileName, geometry, calibration ) :
    """
    Constructor.

    Args:
      fileName: G-Code file to use.
      geometry: Layer/machine geometry.
      calibration: Layer calibration.
    """

    G_CodeHandlerBase.__init__( self )

    # Read input file.
    with open( fileName ) as inputFile :
      # Read file header.
      inputFile.readline()

      # Get the rest of the lines.
      lines = inputFile.readlines()

    self._gCode = G_Code( lines, self._callbacks )
    self._calibration = calibration
    self._geometry = geometry
    self._headZ = 0

  #---------------------------------------------------------------------
  def toPath( self ) :
    """
    Convert the G-Code into a 3d path.

    Returns:
      Instance of G_CodePath that contains the motions of the head as specified
      by G-Code.
    """
    path = G_CodePath()
    totalLines = self._gCode.getLineCount()

    FRONT = 0
    PARTIAL_FRONT = 1
    PARTIAL_BACK  = 2
    BACK = 3

    offset = self._calibration.getOffset()

    self._headZ = self._geometry.frontZ
    latchSide = FRONT
    for line in range( 0, totalLines ) :

      # Reset all values so we know what has changed.
      self._lastX = self._x
      self._lastY = self._y
      self._lastZ = self._z
      self._functions = []

      # Interpret the next line.
      try :
        self._gCode.executeNextLine( line )
      except Exception as exception :
        print "Error on line ", line
        raise exception

      for function in self._functions :
        path.pushG_Code( G_CodeFunction( function[ 0 ], function[ 1: ] ) )

        if G_Codes.HEAD_LOCATION == int( function[ 0 ] ) :
          latchSide = int( function[ 1 ] )
          if FRONT == latchSide :
            self._headZ = self._geometry.frontZ
          elif PARTIAL_FRONT == latchSide :
            self._headZ = self._geometry.partialZ_Front
          elif PARTIAL_BACK == latchSide :
            self._headZ = self._geometry.partialZ_Back
          elif BACK == latchSide :
            self._headZ = self._geometry.backZ

      path.push( self._x + offset.x, self._y + offset.y, self._headZ + offset.z )

    return path

  #---------------------------------------------------------------------
  def _pointLabel( self, output, location, text, layer=None, offsetX=None, offsetY=None ) :
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

    if None == offsetX :
      offsetX = random.uniform( -3, 3 )

    if None == offsetY :
      offsetY = random.uniform( -3, 3 )

    output.write( 'vector = Geom::Vector3d.new ' + str( offsetX ) + ',0,' + str( offsetY ) + "\r\n" )
    output.write( 'label = Sketchup.active_model.entities.add_text "'
      + text + '", point, vector' + "\r\n" )

    if layer :
      output.write( 'label.layer = ' + layer + "\r\n" )

  #---------------------------------------------------------------------
  def writeRubyCode(
    self,
    outputFileName,
    enablePathLabels=False,
    enablePinLabels=False
  ) :
    """
    Export node paths to Ruby code for import into SketchUp for visual
    verification.

    Args:
      outputFileName: File name to create.
      enablePathLabels: Label additional G-Code points.
    """
    with open( outputFileName, "w" ) as rubyFile :

      gCodePath = self.toPath()

      layerOffset = \
        Location( self._geometry.apaOffsetX, self._geometry.apaOffsetY, self._geometry.apaOffsetZ )

      rubyFile.write( 'layer = Sketchup.active_model.layers.add "Pin labels"' + "\r\n" )
      if enablePinLabels :
        for pinName in self._calibration.getPinNames() :
          location = self._calibration.getPinLocation( pinName )
          location = location.add( layerOffset )

          y = 0.1
          x = 0.1
          if "B" == pinName[ 0 ] :
            location.z = self._geometry.depth + self._geometry.apaOffsetZ
            y = -y
            x = -x

          self._pointLabel( rubyFile, location, pinName, 'layer', x, y )

      gCodePath.toSketchUpRuby( rubyFile, enablePathLabels )
