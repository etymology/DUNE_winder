###############################################################################
# Name: G_CodeToPath.py
# Uses: Convert G-Code to a 3d G-Code path.
# Date: 2016-03-30
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from __future__ import print_function
import random

from Library.G_Code import G_Code

from Library.Geometry.Location import Location

from Machine.G_Codes import G_Codes
from Machine.G_CodeHandlerBase import G_CodeHandlerBase
from Machine.DefaultCalibration import DefaultMachineCalibration
from Machine.HeadCompensation import HeadCompensation

from .G_CodePath import G_CodePath
from .G_CodeFunctions.G_CodeFunction import G_CodeFunction
from six.moves import range

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
    machineCalibration = DefaultMachineCalibration()
    machineCalibration.headArmLength    = 0
    machineCalibration.headRollerRadius = 0
    machineCalibration.headRollerGap    = 0

    headCompensation = HeadCompensation( machineCalibration )
    G_CodeHandlerBase.__init__( self, machineCalibration, headCompensation )

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

    self.useLayerCalibration( calibration )

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

    # Set initial location.
    self._x = 0
    self._y = 0
    self._z = 0

    self._headZ = self._geometry.retracted
    latchSide = FRONT
    for line in range( 0, totalLines ) :

      # Reset all values so we know what has changed.
      self._lastX = self._x
      self._lastY = self._y
      self._lastZ = self._z
      self._functions = []

      try :
        self._gCode.executeNextLine( line )
      except Exception as exception:
        print("Unable to execute line", line)
        print("  " + self._gCode.lines[ line ])
        print("  " + str( exception ))
        raise Exception( "Problems executing G-Code: " + str( exception ) )

      for function in self._functions :
        path.pushG_Code( G_CodeFunction( function[ 0 ], function[ 1: ] ) )

      if FRONT == self._headPosition :
        self._headZ = self._geometry.retracted
      elif PARTIAL_FRONT == self._headPosition :
        self._headZ = self._geometry.mostlyRetract
      elif PARTIAL_BACK == self._headPosition :
        self._headZ = self._geometry.mostlyExtend
      elif BACK == self._headPosition :
        self._headZ = self._geometry.extended

      path.push( self._x, self._y, self._headZ )

    return path

  #---------------------------------------------------------------------
  def _pointLabel( self, output, location, text, layer=None, offsetX=None, offsetY=None ) :
    """
    Make a SketchUp label at specified location.

    Args:
      output: Open file for output.
      location: The location to label.
      text: The text to place on this label.
      layer: Layer to add text.  None for default layer.
      offsetX: X-offset to label.
      offsetY: Y-offset to label.
    """
    x = location.x / 25.4
    y = location.y / 25.4
    z = location.z / 25.4

    output.write(
      'point = Geom::Point3d.new [ '
        + str( x ) + ','
        + str( z ) + ','
        + str( y ) + ' ]'
        + "\n" )

    if None == offsetX :
      offsetX = random.uniform( -3, 3 )

    if None == offsetY :
      offsetY = random.uniform( -3, 3 )

    output.write( 'vector = Geom::Vector3d.new ' + str( offsetX ) + ',0,' + str( offsetY ) + "\n" )
    output.write( 'label = Sketchup.active_model.entities.add_text "'
      + text + '", point, vector' + "\n" )

    if layer :
      output.write( 'label.layer = ' + layer + "\n" )

  #---------------------------------------------------------------------
  def writeRubyCode(
    self,
    outputFileName,
    layerName,
    layerHalf,
    enablePathLabels=False,
    enablePinLabels=False,
    isAppend=False
  ) :
    """
    Export node paths to Ruby code for import into SketchUp for visual
    verification.

    Args:
      outputFileName: File name to create.
      layerHalf: 0=first half, 1=second half.
      enablePathLabels: Label additional G-Code points.
      enablePinLabels: True to enable pin labels.
      isAppend: True to append, False to overwrite output file.
    """

    attributes = "w"
    if isAppend :
      attributes = "a"

    with open( outputFileName, attributes ) as rubyFile :

      gCodePath = self.toPath()

      if enablePinLabels :
        rubyFile.write(
          'layer = Sketchup.active_model.layers.add "Pin labels ' + layerName + '"' + "\n" )

        for pinName in self._calibration.getPinNames() :
          location = self._calibration.getPinLocation( pinName )
          location = location.add( self._calibration.offset )

          # $$$FUTURE - The offset for Z is added twice.  Figure out how to fix this.
          location.z -= self._calibration.offset.z

          y = 0.1
          x = 0.1
          if "B" == pinName[ 0 ] :
            y = -y
            x = -x

          self._pointLabel( rubyFile, location, pinName, 'layer', x, y )

      gCodePath.toSketchUpRuby( rubyFile, layerName, layerHalf, enablePathLabels )
