###############################################################################
# Name: G_CodeToPath.py
# Uses: Convert G-Code to a 3d G-Code path.
# Date: 2016-03-30
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################


from Library.G_Code import G_Code
from G_CodePath import G_CodePath
from G_CodeFunctions.LatchG_Code import LatchG_Code

from Machine.G_CodeHandlerBase import G_CodeHandlerBase
from Machine.LayerCalibration import LayerCalibration


class G_CodeToPath( G_CodeHandlerBase ) :

  def __init__( self, fileName, geometry ) :

    G_CodeHandlerBase.__init__( self )

    # Read input file.
    with open( fileName ) as inputFile :
      # Read file header.
      header = inputFile.readline()

      # Get the rest of the lines.
      lines = inputFile.readlines()

    self._gCode = G_Code( lines, self._callbacks )
    self._calibration = LayerCalibration( "" )
    self._geometry = geometry

  def toPath( self ) :

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
        #print function[ 0 ]
        number = int( function[ 0 ] )
        if 100 == number :
          #print "Latch", function[ 1 ]
          path.pushG_Code( LatchG_Code( int( function[ 1 ] ) ) )

      path.push( self._x, self._y, self._z )

    return path

  #---------------------------------------------------------------------
  def writeRubyCode(
    self,
    outputFileName,
    enablePathLabels=False
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

    gCodePath.toSketchUpRuby( rubyFile, enablePathLabels )

    rubyFile.close()
