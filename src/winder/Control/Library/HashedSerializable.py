###############################################################################
# Name: HashedSerializable.py
# Uses: A serialized class checked for validity using a hash.
# Date: 2016-04-19
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import pathlib
import re

from .Hash import Hash
from .Serializable import Serializable

class HashedSerializable( Serializable ) :

  #===================================================================
  class Error( ValueError ) :
    """
    Exception on hash match failure.
    """

    #-----------------------------------------------------------------
    def __init__(self, message, data=None):
      """
      Constructor.

      Args:
        message: Error message.
        data: An array of data related to the exception.
      """
      if data is None:
        data = []
      ValueError.__init__( self, message )
      self.data = data

  #-------------------------------------------------------------------
  def __init__( self, includeOnly=None, exclude=None, ignoreMissing=False ) :
    """
    Constructor.

    Args:
      includeOnly: List of class variables to include in serialization.  None to
        include all, or use exclude list.
      exclude: List of class variables to exclude in serialization.  includeOnly
        must be None for this to have effect.  None to include all class
        variables.
    """
    Serializable.__init__( self, includeOnly, exclude, ignoreMissing )

    self._filePath = None
    self._fileName = None

    # Hash of XML data used for modification detection.
    self.hashValue = ""

  #-------------------------------------------------------------------
  def _calculateStringHash( self, lines ):
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
    lines = re.sub(f'(<strname="hashValue">{Hash.HASH_PATTERN}?</str>)', '', lines)

    return Hash.singleLine( lines )

  #-------------------------------------------------------------------
  def load( self, filePath, fileName, nameOverride=None, exceptionForMismatch=True ):
    """
    Load an XML file and return instance.

    Args:
      filePath: Directory of file.
      fileName: File name to load.
      nameOverride: Top-level XML name.
      exceptionForMismatch: True to raise an exception if the hash does not
        match.  Default is True.

    Returns:
      True if there was an error, False if not.

    Throws:
      HashedSerializable.Error if hashes do not match (only when
      exceptionForMismatch is True).
    """

    self._filePath = filePath
    self._fileName = fileName

    # Load the serialized XML data as usual.
    Serializable.load( self, filePath, fileName, nameOverride )

    # Get all XML lines.
    lines = pathlib.Path(f"{filePath}/{fileName}").read_text()
    # Extract the hash from the raw XML.
    body = re.search( '<str[\s]*?name="hashValue"[\s]*?>' + Hash.HASH_PATTERN + '?</str>', lines )
    self.hashValue = body[1]

    hashValue = self._calculateStringHash( lines )

    isError = hashValue != self.hashValue
    if isError and exceptionForMismatch:
      raise HashedSerializable.Error(
          f"{str(hashValue)} does not match {str(self.hashValue)}",
          [str(hashValue), str(self.hashValue)],
      )

    return isError

  #-------------------------------------------------------------------
  def getFullFileName( self ):
    """
    Get the full path to file.
    File must have been saved/loaded prior to calling.

    Returns:
      Full path to file.
    """

    return f"{self._filePath}/{self._fileName}"

  #-------------------------------------------------------------------
  def getFileName( self ) :
    """
    Get the file name.
    File must have been saved/loaded prior to calling.

    Returns:
      File name.
    """

    return self._fileName

  #-------------------------------------------------------------------
  def getFilePath( self ) :
    """
    Get the file path.
    File must have been saved/loaded prior to calling.

    Returns:
      File path.
    """

    return self._filePath

  #-------------------------------------------------------------------
  def save( self, filePath=None, fileName=None, nameOverride=None ):
    """
    Write XML data to disk.

    Args:
      filePath: Directory of file.  Omit to use the path specified loading.
      fileName: File name to save in.  Omit to use the name specified loading.
      nameOverride: Top-level XML name.
    """

    # File name/path omitted?
    if filePath is None == fileName:
      filePath = self._filePath
      fileName = self._fileName

    self._filePath = filePath
    self._fileName = fileName

    # Start with the XML.
    outputText = self.toXML_String( nameOverride )

    # Calculate hash of XML.
    self.hashValue = self._calculateStringHash( outputText )

    # Replace hash value with updated value.
    outputText = re.sub(
        '<str[\s]*?name="hashValue"[\s]*?>' + Hash.HASH_PATTERN + '?</str>',
        f'<str name="hashValue">{self.hashValue}</str>',
        outputText,
    )

    # Write XML data to file.
    with open(f"{filePath}/{fileName}", "wb") as outputFile:
      outputFile.write( outputText )

# end class

# Unit test.
if __name__ == "__main__":

  class TestClass2( Serializable ) :

    #-------------------------------------------------------------------
    def __init__( self ) :
      self.aa = None
      self.bb = None
      self.cc = None
      self.dd = None

    def __str__( self ):
      return f"{str(self.aa)},{str(self.bb)},{str(self.cc)},{str(self.dd)}"

    def bar() :
      pass

  class Unserializable :
    pass

  class TestClass( HashedSerializable ) :

    #-------------------------------------------------------------------
    def __init__( self ) :


      self.a = None
      self.b = None
      self.c = None
      self.d = None
      self.testClass2 = TestClass2()
      self.e = []
      self.f = {}
      self.g = Unserializable()
      self.h = lambda: 5

      HashedSerializable.__init__( self, exclude=[ 'g', 'h' ] )

    def foo() :
      pass


  testClass = TestClass()
  testClass.a = 11.0
  testClass.b = 12
  testClass.c = 13
  testClass.d = "14"
  testClass.e = [ 100, 200.0, 300, "400", 3.14e9 ]
  testClass.f = { 'apple': 1, "orange": 2 }
  testClass.testClass2.aa = 11
  testClass.testClass2.bb = 22
  testClass.testClass2.cc = 33
  testClass.testClass2.dd = 44
  testClass.save( ".", "test.xml" )

  testClassCopy = TestClass()
  testClassCopy.load( ".", "test.xml" )

  assert( testClassCopy.a == testClass.a )
  assert( testClassCopy.b == testClass.b )
  assert( testClassCopy.c == testClass.c )
  assert( testClassCopy.d == testClass.d )
  assert( testClassCopy.e == testClass.e )
  assert( testClassCopy.f == testClass.f )
  assert( testClassCopy.testClass2.aa == testClass.testClass2.aa )
  assert( testClassCopy.testClass2.bb == testClass.testClass2.bb )
  assert( testClassCopy.testClass2.cc == testClass.testClass2.cc )
  assert( testClassCopy.testClass2.dd == testClass.testClass2.dd )
