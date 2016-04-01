###############################################################################
# Name: G_CodeToPath.py
# Uses: Convert G-Code to a 3d G-Code path.
# Date: 2016-03-30
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import random

from Library.G_Code import G_Code
from G_CodePath import G_CodePath

from G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from G_CodeFunctions.LatchG_Code import LatchG_Code
from G_CodeFunctions.ClipG_Code import ClipG_Code
from G_CodeFunctions.PinCenterG_Code import PinCenterG_Code
from G_CodeFunctions.G_CodeFunction import G_CodeFunction

from Machine.G_Codes import G_Codes
from Machine.G_CodeHandlerBase import G_CodeHandlerBase
from Machine.LayerCalibration import LayerCalibration


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
      header = inputFile.readline()

      # Get the rest of the lines.
      lines = inputFile.readlines()

    self._gCode = G_Code( lines, self._callbacks )
    self._calibration = calibration
    self._geometry = geometry

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
    for line in range( 0, totalLines ) :

      # Reset all values so we know what has changed.
      self._lastX = self._x
      self._lastY = self._y
      self._lastZ = self._z
      self._functions = []

      # Interpret the next line.
      self._gCode.executeNextLine( line )

      for function in self._functions :
        path.pushG_Code( G_CodeFunction( function[ 0 ], function[ 1: ] ) )

      path.push( self._x, self._y, self._z )

    return path

  #---------------------------------------------------------------------
  def _pointLabel( self, output, location, text, layer=None, vary=False ) :
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

    if vary :
      random.uniform( -3, 3 )
      random.uniform( -3, 3 )
    else :
      x = 0.1
      y = 0.1

    output.write( 'vector = Geom::Vector3d.new ' + str( x ) + ',0,' + str( y ) + "\r\n" )
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
    rubyFile = open( outputFileName, "w" )

    gCodePath = self.toPath()

    rubyFile.write( 'layer = Sketchup.active_model.layers.add "Pin labels"' + "\r\n" )
    if enablePinLabels :
      for pinName in self._calibration._locations :
        location = self._calibration.getPinLocation( pinName )
        if "B" == pinName[ 0 ] :
          location.z = self._geometry.depth

        self._pointLabel( rubyFile, location, pinName, 'layer' )

    gCodePath.toSketchUpRuby( rubyFile, enablePathLabels )

    rubyFile.close()
