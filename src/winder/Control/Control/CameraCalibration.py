###############################################################################
# Name: CameraCalibration.py
# Uses: Use calibration data from vision system to generate layer calibration.
# Date: 2016-12-22
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import xml.dom.minidom

from Library.Geometry.Location import Location
from Library.ArrayToCSV import ArrayToCSV

from Machine.LayerFunctions import LayerFunctions

class CameraCalibration :

  #---------------------------------------------------------------------
  def __init__( self, io ) :
    """
    Constructor.
    """
    self._io = io
    self._pixelsPer_mm = 18
    self._calibrationData = []
    self._side      = None
    self._startPin  = None
    self._direction = None
    self._pinMax    = None

  #---------------------------------------------------------------------
  def pixelsPer_mm( self, pixelsPer_mm = None ) :
    """
    Get/set pixels/mm.

    Args:
      pixelsPer_mm: New values.  None (default) to read value.

    Returns:
      Current pixels/mm value.
    """

    if None != pixelsPer_mm :
      self._pixelsPer_mm = pixelsPer_mm

    return self._pixelsPer_mm

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Periodic update function to call while calibration is taking place.
    Used to clear the capture FIFO and convert this data to machine coordinates.
    """

    calibrationData = []
    if None != self._startPin :

      pin = self._startPin
      for entry in self._io.camera.captureFIFO :

        fullEntry = entry.copy()
        fullEntry[ "Side" ] = self._side
        fullEntry[ "Pin" ] = pin

        # Get offset from camera center of pin location.
        # (Yes, x and y are reversed)
        y = ( self._io.camera.FRAME_WIDTH  / 2 ) - entry[ "CameraX" ]
        x = ( self._io.camera.FRAME_HEIGHT / 2 ) - entry[ "CameraY" ]

        # Convert pixels to millimeters.
        x /= self._pixelsPer_mm
        y /= self._pixelsPer_mm

        # Save corrected position.
        fullEntry[ "MotorX_Corrected" ] = entry[ "MotorX" ] + x
        fullEntry[ "MotorY_Corrected" ] = entry[ "MotorY" ] - y

        calibrationData.append( fullEntry )

        pin += self._direction
        if pin > self._pinMax :
          pin = 1
        elif pin <= 0 :
          pin = self._pinMax

    # Switch to new data.
    self._calibrationData = calibrationData

  #---------------------------------------------------------------------
  def commitCalibration( self, layerCalibration, geometry, isFront, offsetX, offsetY ) :
    """
    Update the layer with the acquired calibration data.

    Args:
      layerCalibration: Calibration for current layer.
      geometry: Layer geometry.
      isFront: True is camera data is from front side of APA.
      offsetX: Offset in X from current side to other side.
      offsetY: Offset in Y from current side to other side.

    Returns:
      layerCalibration is modified.
      Function returns nothing.
    """

    sideA = "F"
    sideB = "B"
    if not isFront :
      sideA = "B"
      sideB = "F"

    for entry in self._calibrationData :
      if 1 == entry[ "Status" ] :
        pin = entry[ "Pin" ]
        pinName = sideA + str( pin )
        location = Location( entry[ "MotorX" ], entry[ "MotorY" ], geometry.mostlyExtend )
        layerCalibration.setPinLocation( pinName, location )

        pin = LayerFunctions.translateFrontBack( geometry, pin )
        pinName = sideB + str( pin )
        x = entry[ "MotorX" ] + offsetX
        y = entry[ "MotorY" ] + offsetY
        location = Location( x, y, geometry.mostlyRetract )
        layerCalibration.setPinLocation( pinName, location )

  #---------------------------------------------------------------------
  def setupCalibration( self, side, startPin, direction, pinMax ) :
    """
    Setup parameters for a calibration scan.
    Call before starting polling.

    Args:
      startPin: The first pin in the scan.
      direction: Counting direction of pin numbers (+1/-1).
      pinMax: Maximum number of pins before rolling over.
    """

    self._side      = side
    self._startPin  = startPin
    self._direction = direction
    self._pinMax    = pinMax

  #---------------------------------------------------------------------
  def getCalibrationData( self ) :
    """
    Return the acquired calibration data thus far.

    Returns:
      Array of dictionaries.  Each row has a dictionary entry with the following
      fields: Pin, Status, MatchLeve, MotorX, MotorY.
    """
    return self._calibrationData

  #---------------------------------------------------------------------
  def setCalibrationData( self, pin, x, y ) :
    """
    Update a calibration record.  Used to correct pins missed in scan.

    Args:
      pin: Pin number to correct.
      x: Updated location in X axis.
      x: Updated location in Y axis.
    """
    items = self._calibrationData

    # Find row for pin in capture FIFO.
    row = ( item for item in items if item[ "Pin" ] == pin ).next()

    # Update data.
    row[ "Status" ] = 1
    row[ "MotorX" ] = x
    row[ "MotorY" ] = y

  #---------------------------------------------------------------------
  def reset( self ) :
    """
    Flush current calibration data.
    """
    self._io.camera.reset()
    self._calibrationData = []

  #---------------------------------------------------------------------
  def save( self, filePath, fileName ) :
    """
    Write calibration data to CSV file.
    """
    return ArrayToCSV.saveDictionarySet( self._calibrationData, filePath, fileName, isHashed=True )
