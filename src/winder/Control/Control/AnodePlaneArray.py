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
from Library.Recipe import Recipe
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
  def __init__(
    self,
    gCodeHandler,
    apaDirectory,
    recipeDirectory,
    recipeArchiveDirectory,
    name,
    log,
    createNew=False
  ) :
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

    self._apaDirectory = apaDirectory
    self._recipeDirectory = recipeDirectory
    self._recipeArchiveDirectory = recipeArchiveDirectory
    self._name = name
    self._log = log
    self._gCodeHandler = gCodeHandler

    # Uninitialized data.
    self._lineNumber = None
    self._recipeFile = None
    self._recipe = None

    # $$$DEBUG Error check.
    # $$$DEBUG What to do on failure?

    # Create directory if it doesn't exist.
    apaExists = os.path.exists( self._getPath() )
    if not apaExists and createNew :
      os.makedirs( self._getPath() )

    self._log.attach( self._getPath() + AnodePlaneArray.LOG_FILE )

    if not apaExists and createNew :
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
    return self._apaDirectory + "/" + self._name + "/"

  #---------------------------------------------------------------------
  def loadRecipe( self, recipeFile=None, startingLine=None ) :
    """
    Load a recipe file into GCodeHandler.

    Args:
      gCodeHandler: An instance of GCodeHandler that will execute the code.
      recipeFile: File name of recipe to load.
      startingLine: What line to start from in recipe.

    Returns:
      True if there was an error, False if not.
    """
    isError = False

    if None != recipeFile :
      self._recipeFile = recipeFile

    if None != startingLine :
      self._lineNumber = startingLine

    self._recipe = Recipe( self._recipeDirectory + "/" + self._recipeFile, self._recipeArchiveDirectory )
    self._gCodeHandler.loadG_Code( self._recipe.getLines() )
    #self._gCodeHandler.loadG_Code( self._recipeDirectory + "/" + self._recipeFile )
    #try:
    #  recipe = Recipe( self._recipeDirectory + "/" + self._recipeFile, self._recipeArchiveDirectory )
    #  self._gCodeHandler.loadG_Code( self._recipeDirectory + "/" + self._recipeFile )
    #except:
    #  isError = True
    #  error = "Unable to load file."

    if not isError :
      isError |= self._gCodeHandler.gCode.setLine( self._lineNumber )
      if isError :
        error = "Invalid line number."

    if not isError :
      self._log.add(
        self.__class__.__name__,
        "GCODE",
        "Loaded G-Code file " + self._recipeFile + ", starting at line " + str( self._lineNumber ),
        [
          self._recipeFile,
          self._lineNumber,
          self._recipe.getDescription(),
          self._recipe.getID()
        ]
      )
    else:
      self._log.add(
        self.__class__.__name__,
        "GCODE",
        "Failed to loaded G-Code file " + self._recipeFile + ", starting at line " + str( self._lineNumber ),
        [
          error,
          self._recipeFile,
          self._lineNumber
        ]
      )

    return isError

  # MOVED #---------------------------------------------------------------------
  # MOVED def start( self ) :
  # MOVED   """
  # MOVED   Begin executing recipe.
  # MOVED
  # MOVED   Returns:
  # MOVED     True if recipe execution began, False if not.
  # MOVED   """

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

      if self._recipeFile :
        self.loadRecipe()

  #---------------------------------------------------------------------
  def save( self ) :
    """
    Save state of APA to disk.
    """

    # $$$DEBUG - Error checking.

    if self._gCodeHandler.gCode :
      self._lineNumber = self._gCodeHandler.gCode.getLine()

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

    lineNumberString = node.getAttribute( "lineNumber" )
    if "None" != lineNumberString :
      self._lineNumber = int( lineNumberString )
    else :
      self._lineNumber = None

    return False


# end class
