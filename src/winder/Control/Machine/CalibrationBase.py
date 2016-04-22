###############################################################################
# Name:
# Uses:
# Date: 2016-04-19
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

class CalibrationBase( Serializable ) :

  TOP_TAG = 'CalibrationFile'
  HASH_TAG = 'Calibration'

  #-------------------------------------------------------------------
  @staticmethod
  def _calculateStringHash( lines ) :
    """
    Calculate a hash over the body of the XML.

    Args:
      lines: XML lines.

    Returns:
      A list with two string.  First string is the hash from the file header,
      and the second is the calculated hash.  They should match is all is well.
    """
    lines = lines.replace( '\n', '' )
    lines = lines.replace( '\r', '' )
    lines = lines.replace( '\t', '' )
    lines = lines.replace( ' ', '' )

    # Calculate a hash over the body of the calibration.
    # This is used to prevent any modification to calibration once it has been
    # established.
    body = \
      re.search(
        '<' + CalibrationBase.HASH_TAG
          + '.*?(hash="([a-zA-Z0-9=]*)").*?>(.+?)</'
          + CalibrationBase.HASH_TAG + '>',
        lines )

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
    Compute the hash on an XML file.

    Args:
      fileName: File to compute hash on.

    Returns:
      A list with two string.  First string is the hash from the file header,
      and the second is the calculated hash.  They should match is all is well.
    """

    with open( fileName ) as inputFile :
      lines = inputFile.read()

    return CalibrationBase._calculateStringHash( lines )

  #-------------------------------------------------------------------
  @staticmethod
  def load( filePath, fileName, returnClass ) :
    """
    Load a calibration file and return instance.

    Args:
      filePath: Directory of file.
      fileName: File name to load.
      returnClass: Class to create and return instance of.
    Returns:
      Instance of 'returnClass' or None if there was a problem.
    """

    instance = None

    fullName = filePath + "/" + fileName
    if os.path.isfile( fullName ) :
      xmlDocument = xml.dom.minidom.parse( fullName )
      node = xmlDocument.getElementsByTagName( CalibrationBase.TOP_TAG )

      [ fileHash, bodyHash ] = CalibrationBase._calculateHash( fullName )

      # Does the calculated hash match the hash from the header?
      if bodyHash == fileHash :
        instance = returnClass()
        instance.unserialize( node[ 0 ] )

    return instance

  #-------------------------------------------------------------------
  def save( self, filePath, fileName ) :
    """
    Write calibration data to disk.

    Args:
      filePath: Directory of file.
      fileName: File name to save in.
    """

    # Serialize data into XML.
    xmlDocument = xml.dom.minidom.parseString( '<' + CalibrationBase.TOP_TAG + '/>' )
    node = self.serialize( xmlDocument )
    xmlDocument.childNodes[ 0 ].appendChild( node )

    # Create text from XML data.
    outputText = xmlDocument.toprettyxml()

    # Strip off extraneous line feeds.
    outputText = \
      '\n'.join( [ line for line in outputText.split( '\n' ) if line.strip() ] ) + '\n'

    _, bodyHash = CalibrationBase._calculateStringHash( outputText )
    outputText = outputText.replace( 'hash=""', 'hash="' + bodyHash + '"' )

    fullName = filePath + "/" + fileName

    # Write XML data to file.
    with open( fullName, "wb" ) as outputFile :
      outputFile.write( outputText )
