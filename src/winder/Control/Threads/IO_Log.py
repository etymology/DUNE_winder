###############################################################################
# Name: IO_LogThread.py
# Uses: System to log I/O.
# Date: 2016-03-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-03-03 - QUE - Creation.
###############################################################################

from IO.Primitives.IO_Point import IO_Point
from IO.Devices.PLC import PLC
import os.path

class IO_Log :

  #---------------------------------------------------------------------
  def __init__( self, outputFileName ) :
    """
    Constructor.

    $$$DEBUG
    """

    # Create the path if it does not exist.
    path = os.path.dirname( outputFileName )
    if path and not os.path.exists( path ) :
      os.makedirs( path )

    needsHeader = not os.path.isfile( outputFileName )
    self._outputFile = open( outputFileName, 'a' )

    if needsHeader :
      names = "Time\tDelta\t"
      for ioPoint in IO_Point.list :
        names += ioPoint.getName() + "\t"

      for tag in PLC.Tag.list :
        names += tag.getName() + "\t"

      self._outputFile.write( names + "\n" )

  #---------------------------------------------------------------------
  def log( self, timeStamp, delta ) :
    """
    $$$DEBUG
    """
    result = str( timeStamp ) + "\t" + str( delta ) + "\t"
    for ioPoint in IO_Point.list :
      result += str( ioPoint.get() ) + "\t"

    for tag in PLC.Tag.list :
      result += str( tag.get() ) + "\t"

    self._outputFile.write( result + "\n" )

# end class
