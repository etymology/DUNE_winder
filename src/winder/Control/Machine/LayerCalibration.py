###############################################################################
# Name: LayerCalibration.py
# Uses: Calibration adjustments for a layer.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import xml.dom.minidom
import os.path
import re
import hashlib
import base64

from Library.Serializable import Serializable
from Library.Geometry.Location import Location

class LayerCalibration( Serializable ) :
  """
  Layer calibration is just a map that has an adjusted location for each
  pin on a layer.  The pins are addressed by side and pin number.  Each
  have a 2d location.

  When uncalibrated, the pin locations are the nominal locations.
  """

  #-------------------------------------------------------------------
  def __init__( self, layer ) :
    """
    Constructor.
    """

    # Name of layer this calibration file applies.
    self._layer = layer

    # Hash of calibration XML data used for modification detection.
    self._hash = None

    # Offset of 0,0 on the APA to machine offset.
    self._offset = None

    # Look-up table that correlates pin names to their locations.
    self._locations = {}

  #-------------------------------------------------------------------
  def setOffset( self, offset ) :
    """
    Set the offset of pin 1 from the machine offset.  Should only be called
    from a calibration routine.

    Args:
      offset: Instance of Location with absolute machine position.
    """
    self._offset = offset

  #-------------------------------------------------------------------
  def getOffset( self ) :
    """
    Return the offset from raw machine position.  Subtract this value from
    the raw position to get the APA position.

    Returns:
      Location of pin 1 in raw machine position.
    """
    return self._offset

  #-------------------------------------------------------------------
  def setPinLocation( self, pin, location ) :
    """
    Set the calibrated location of the specified pin.

    Args:
      pin: Which pin.
      location: The location (relative to the APA) of this pin.
    """
    self._locations[ pin ] = location

  #-------------------------------------------------------------------
  def getPinLocation( self, pin ) :
    """
    Get the calibrated location of the specified pin.

    Args:
      pin: Which pin.

    Returns:
      Instance of Location with the position of this pin.
    """

    return self._locations[ pin ]

  #---------------------------------------------------------------------
  def getPinNames( self ) :
    """
    Return a list of pin names.
    
    Returns:
      List of pin names.
    """
    return self._locations.keys()

  #---------------------------------------------------------------------
  def serialize( self, xmlDocument ) :
    """
    Turn this object into an XML node.

    Args:
      xmlDocument: Instance of xml.dom.minidom.Document.

    Returns:
      Must return an XML node with the data from this object.
    """
    node = xmlDocument.createElement( "Calibration" )
    node.setAttribute( "layer", str( self._layer ) )
    node.setAttribute( "hash", "" )

    for pin in self._locations :

      location = self._locations[ pin ]

      pinNode = xmlDocument.createElement( "Pin" )
      pinNode.setAttribute( "number", str( pin ) )
      pinNode.setAttribute( "x", str( location.x ) )
      pinNode.setAttribute( "y", str( location.y ) )
      node.appendChild( pinNode )

    return node

  #---------------------------------------------------------------------
  def unserialize( self, node ) :
    """
    Take an XML node and load values into this object.

    Args:
      node: Instance of xml.dom.minidom.Node.

    Returns:
      True if there was an error, False if not.
    """
    self._layer = node.getAttribute( "layer" )
    self._hash = node.getAttribute( "layer" )
    pinNodes = node.getElementsByTagName( "Pin" )

    for pinNode in pinNodes :
      pin = pinNode.getAttribute( "number" )
      x = pinNode.getAttribute( "x" )
      y = pinNode.getAttribute( "y" )
      self._locations[ pin ] = Location( x, y )

  #-------------------------------------------------------------------
  @staticmethod
  def _calculateStringHash( lines ) :
    """
    $$$DEBUG
    """
    lines = lines.replace( '\n', '' )
    lines = lines.replace( '\r', '' )
    lines = lines.replace( '\t', '' )
    lines = lines.replace( ' ', '' )

    # Calculate a hash over the body of the calibration.
    # This is used to prevent any modification to calibration once it has been
    # established.
    body = re.search( '<Calibration.*?(hash="([a-zA-Z0-9=]*)").*?>(.+?)</Calibration>', lines )
    fileHash = body.group( 2 )
    bodyData = body.group( 3 )

    # Create hash of G-Code, including description.
    bodyHash = hashlib.sha256()
    bodyHash.update( bodyData )

    # Turn hash into base 32 encoding.
    bodyHash = base64.b32encode( bodyHash.digest() )

    return [ fileHash, bodyHash ]

  #-------------------------------------------------------------------
  @staticmethod
  def _calculateHash( fileName ) :
    """
    $$$DEBUG
    """

    with open( fileName ) as inputFile :
      lines = inputFile.read()

    return LayerCalibration._calculateStringHash( lines )

  #-------------------------------------------------------------------
  def internalSet( self, layer, hashValue ):
    """
    $$$DEBUG
    """
    self._layer = layer
    self._hash  = hashValue
    
  #-------------------------------------------------------------------
  @staticmethod
  def load( filePath, fileName ) :
    """
    $$$DEBUG
    """

    layerCalibration = None

    fullName = filePath + "/" + fileName
    if os.path.isfile( fullName ) :
      xmlDocument = xml.dom.minidom.parse( fullName )
      node = xmlDocument.getElementsByTagName( "CalibrationFile" )
      layer = node[ 0 ].getAttribute( "layer" )

      [ fileHash, bodyHash ] = LayerCalibration._calculateHash( fullName )

      # Does the calculated hash match the hash from the header?
      if bodyHash == fileHash :
        layerCalibration = None

        layerCalibration = LayerCalibration( layer )
        layerCalibration.unserialize( node[ 0 ] )
        layerCalibration.internalSet( layer, bodyHash )
      else :
        print "Hash mismatch"
        print bodyHash
        print fileHash

      # $$$FUTURE
      ## Log message about AHA change.
      #self._log.add(
      #  self.__class__.__name__,
      #  "LOAD",
      #  "Loaded calibration file " + fileName,
      #  [ fileName ]
      #)
    else :
      # $$$FUTURE
      print "File not found", fullName
      #self._log.add(
      #  self.__class__.__name__,
      #  "LOAD",
      #  "Unable to load calibration file " + fileName + ".  File not found.",
      #  [ fileName ]
      #)
      #pass

    return layerCalibration

  #-------------------------------------------------------------------
  def save( self, filePath, fileName ) :
    """
    $$$DEBUG
    """

    # Serialize data into XML.
    xmlDocument = xml.dom.minidom.parseString( '<CalibrationFile/>' )
    node = self.serialize( xmlDocument )
    xmlDocument.childNodes[ 0 ].appendChild( node )

    # Create text from XML data.
    outputText = xmlDocument.toprettyxml()

    # Strip off extraneous line feeds.
    outputText = \
      '\n'.join( [ line for line in outputText.split( '\n' ) if line.strip() ] ) + '\n'

    _, bodyHash = LayerCalibration._calculateStringHash( outputText )
    outputText = outputText.replace( 'hash=""', 'hash="' + bodyHash + '"' )

    fullName = filePath + "/" + fileName

    # Write XML data to file.
    with open( fullName, "wb" ) as outputFile :
      outputFile.write( outputText )
