###############################################################################
# Name: Recipe.py
# Uses: Anode Plane Array (APA) management.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-03-01 - QUE - Creation.
###############################################################################

from Library.Serializable import Serializable
import xml.dom.minidom
import os.path

class AnodePlaneArray( Serializable ) :

  # File name of the APA state (this object) on disk.
  FILE_NAME = "state.xml"
  LOG_FILE  = "log.csv"

  # There can only be a single working instance of an APA, and it must be
  # saved before loading or starting a new one.
  activeAPA = None

  # #---------------------------------------------------------------------
  # @staticmethod
  # def create( name, recipeFile, log ) :
  #   """
  #   """
  #   apa = APA()

  #---------------------------------------------------------------------
  def __init__( self, rootDirectory, name, log, createNew=False ) :
    """
    Constructor.

    Args:
      name: Name/serial number of APA.
      log: Instance of system log file.
      createNew: True if this APA should be created should it not already exist.
    """

    # If there was an APA previously active, save it.
    # $$$DEBUG - Log message about changing APAs?
    if AnodePlaneArray.activeAPA :
      AnodePlaneArray.activeAPA.close()

    AnodePlaneArray.activeAPA = self

    self._rootDirectory = rootDirectory
    self._name = name
    self._log = log


    # Uninitialized data.
    self._lineNumber = None
    self._recipeFile = None

    # $$$DEBUG Error check.
    # $$$DEBUG What to do on failure?

    # Create directory if it doesn't exist.
    apaExists = os.path.exists( self._getPath() )
    if not apaExists and createNew :
      os.makedirs( self._getPath() )

    self._log.attach( self._getPath() + AnodePlaneArray.LOG_FILE )

    if not apaExists :
      self._log.add(
        self.__class__.__name__,
        "NEW",
        "Created new APA called " + self._name,
        [ self._name ]
      )
    else:
      self.load()

  #---------------------------------------------------------------------
  def _getPath( self ):
    """
    Get the path for all files related to this APA.
    """
    return self._rootDirectory + "/" + self._name + "/"

  #---------------------------------------------------------------------
  def loadRecipie( self, gCodeHandler, recipeFile=None, startingLine=None ) :
    """
    $$$DEBUG -
    """
    if recipeFile :
      self._recipeFile = recipeFile

    if startingLine :
      self._lineNumber = startingLine

    self._log.add(
      self.__class__.__name__,
      "GCODE",
      "Loaded G-Code file " + self._recipeFile + ", starting at line " + str( self._lineNumber ),
      [ self._name, self._lineNumber ]
    )

    gCodeHandler.loadG_Code( self._recipeFile )
    gCodeHandler.setLine( self._lineNumber )

  #---------------------------------------------------------------------
  def load( self ) :
    """
    Load
    """
    self._log.add(
      self.__class__.__name__,
      "LOAD",
      "Loaded APA called " + self._name,
      [ self._name ]
    )

    # $$$DEBUG - Error checking.

    fileName = self._getPath() + AnodePlaneArray.FILE_NAME
    if os.path.isfile( fileName ) :
      xmlDocument = xml.dom.minidom.parse( fileName )
      node = xmlDocument.getElementsByTagName( self._name )
      self.unserialize( node[ 0 ] )

  #---------------------------------------------------------------------
  def save( self ) :
    """
    Save state of APA to disk.
    """

    # $$$DEBUG - Error checking.

    xmlDocument = xml.dom.minidom.parseString( '<AnodePlaneArray/>' )
    node = self.serialize( xmlDocument )
    xmlDocument.childNodes[ 0 ].appendChild( node )

    outputText = xmlDocument.toprettyxml()

    # Strip off extraneous line feeds.
    outputText = \
      '\n'.join( [ line for line in outputText.split( '\n' ) if line.strip() ] ) + '\n'

    outputFile = open( self._getPath() + AnodePlaneArray.FILE_NAME, "wb" )
    outputFile.write( outputText )
    outputFile.close()

  #---------------------------------------------------------------------
  def close( self ) :
    """
    Close an APA.  Call during shutdown sequence.  Called internally when new
    APA is loaded.
    """
    self.save()
    self._log.add(
      self.__class__.__name__,
      "CLOSE",
      "Closing APA " + self._name,
      [ self._name ]
    )
    self._log.detach( self._getPath() + AnodePlaneArray.LOG_FILE )

  #---------------------------------------------------------------------
  def serialize( self, xmlDocument ) :
    """
    Turn this object into an XML node.

    Args:
      xmlDocument: Instance of xml.dom.minidom.Document.

    Returns:
      Must return an XML node with the data from this object.
    """
    node = xmlDocument.createElement( self._name )

    node.setAttribute( "recipeFile", self._recipeFile )
    node.setAttribute( "lineNumber", str( self._lineNumber ) )

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
    self._recipeFile = node.getAttribute( "recipeFile" )
    self._lineNumber = int( node.getAttribute( "lineNumber" ) )

    return False


# end class
