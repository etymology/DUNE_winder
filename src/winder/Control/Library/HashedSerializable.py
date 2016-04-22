###############################################################################
# Name: HashedSerializable.py
# Uses: A serialized class checked for validity using a hash.
# Date: 2016-04-19
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import xml.dom.minidom
import os.path
import re
import hashlib
import base64

from Serializable import Serializable

class HashedSerializable( Serializable ) :

  #-------------------------------------------------------------------
  def __init__( self, includeOnly=None, exclude=None ) :
    """
    Constructor.

    Args:
      includeOnly: List of class variables to include in serialization.  None to
        include all, or use exclude list.
      exclude: List of class variables to exclude in serialization.  includeOnly
        must be None for this to have effect.  None to include all class
        variables.
    """
    Serializable.__init__( self, includeOnly, exclude )

    # Hash of XML data used for modification detection.
    self.hashValue = ""

  #-------------------------------------------------------------------
  def _calculateStringHash( self, lines ) :
    """
    Calculate a hash of a string of XML lines.

    Args:
      lines: A string containing one or more XML lines.

    Returns:
      Base-32 encoded hash value for data.

    Notes:
      Must contain an XML hash value entry.
    """

    # Remove all white-space.
    # This is done because white-space will not alter the content of the data
    # but can legitimately be different for two identical sets of data.
    lines = re.sub( '[\s]+', '', lines )

    # Ignore the hash entry completely.
    lines = re.sub( '(<strname="hashValue">[a-zA-Z0-9=]*</str>)', '', lines )

    # Create hash of G-Code, including description.
    hashValue = hashlib.sha256()
    hashValue.update( lines )

    # Turn hash into base 32 encoding.
    hashValue = base64.b32encode( hashValue.digest() )

    return hashValue

  #-------------------------------------------------------------------
  def load( self, filePath, fileName, exceptionForMismatch=True ) :
    """
    Load an XML file and return instance.

    Args:
      filePath: Directory of file.
      fileName: File name to load.
      exceptionForMismatch: True to raise an exception if the hash does not
        match.  Default is True.

    Returns:
      True if there was an error, False if not.
    """

    # Load the serialized XML data as usual.
    Serializable.load( self, filePath, fileName )

    # Get all XML lines.
    with open( filePath + "/" + fileName ) as inputFile :
      lines = inputFile.read()

    # Extract the hash from the raw XML.
    body = re.search( '<str[\s]*?name="hashValue"[\s]*?>([a-zA-Z0-9=]*)</str>', lines )
    self.hashValue = body.group( 1 )

    hashValue = self._calculateStringHash( lines )

    isError = hashValue != self.hashValue
    if isError and exceptionForMismatch :
      raise ValueError( str( hashValue ) + " does not match " + str( self.hashValue ) )

    return isError

  #-------------------------------------------------------------------
  def save( self, filePath, fileName, nameOverride=None ) :
    """
    Write XML data to disk.

    Args:
      filePath: Directory of file.
      fileName: File name to save in.
      nameOverride: Top-level XML name.
    """

    # Start with the XML.
    outputText = self.toXML_String( nameOverride )

    # Calculate hash of XML.
    bodyHash = self._calculateStringHash( outputText )

    # Replace hash value with updated value.
    outputText = \
      re.sub(
        '<str[\s]*?name="hashValue"[\s]*?>([a-zA-Z0-9=]*)</str>',
        '<str name="hashValue">' + bodyHash + '</str>' ,
        outputText
      )

    # Write XML data to file.
    with open( filePath + "/" + fileName, "wb" ) as outputFile :
      outputFile.write( outputText )

# end class

# Unit test.
if __name__ == "__main__":

  class SomeClass2( Serializable ) :

    #-------------------------------------------------------------------
    def __init__( self ) :
      self.aa = None
      self.bb = None
      self.cc = None
      self.dd = None

    def __str__( self ) :
      return str( self.aa ) + "," + str( self.bb ) + "," + str( self.cc ) + "," + str( self.dd )

    def bar() :
      pass

  class Unserializable :
    pass

  class SomeClass( HashedSerializable ) :

    #-------------------------------------------------------------------
    def __init__( self ) :


      self.a = None
      self.b = None
      self.c = None
      self.d = None
      self.someClass2 = SomeClass2()
      self.e = []
      self.f = {}
      self.g = Unserializable()
      self.h = lambda: 5

      HashedSerializable.__init__( self, exclude=[ 'g', 'h' ] )

    def foo() :
      pass


  someClass = SomeClass()
  someClass.a = 11.0
  someClass.b = 12
  someClass.c = 13L
  someClass.d = "14"
  someClass.e = [ 100, 200.0, 300L, "400", 3.14e9 ]
  someClass.f = { 'apple': 1, "orange": 2 }
  someClass.someClass2.aa = 11
  someClass.someClass2.bb = 22
  someClass.someClass2.cc = 33
  someClass.someClass2.dd = 44
  someClass.save( ".", "test.xml" )

  someClassCopy = SomeClass()
  someClassCopy.load( ".", "test.xml" )

  assert( someClassCopy.a == someClass.a )
  assert( someClassCopy.b == someClass.b )
  assert( someClassCopy.c == someClass.c )
  assert( someClassCopy.d == someClass.d )
  assert( someClassCopy.e == someClass.e )
  assert( someClassCopy.f == someClass.f )
  assert( someClassCopy.someClass2.aa == someClass.someClass2.aa )
  assert( someClassCopy.someClass2.bb == someClass.someClass2.bb )
  assert( someClassCopy.someClass2.cc == someClass.someClass2.cc )
  assert( someClassCopy.someClass2.dd == someClass.someClass2.dd )

  print "Good"
