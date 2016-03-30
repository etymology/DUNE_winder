###############################################################################
# Name: Recipe.py
# Uses: Anode Plane Array (APA) management.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import xml.dom.minidom
import os.path

from Library.Serializable import Serializable
from Library.Recipe import Recipe
from Machine.Settings import Settings

from Machine.LayerCalibration import LayerCalibration
from Machine.G_LayerGeometry import G_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.X_LayerGeometry import X_LayerGeometry

class AnodePlaneArray( Serializable ) :

  # File name of the APA state (this object) on disk.
  FILE_NAME = "state.xml"
  LOG_FILE  = "log.csv"

  # There can only be a single working instance of an APA, and it must be
  # saved before loading or starting a new one.
  activeAPA = None

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
      gCodeHandler: Instance of GCodeHandler.
      apaDirectory: Directory APA data is stored.
      recipeDirectory: Directory recipes are stored.
      recipeArchiveDirectory: Directory recipes are archived.
      name: Name/serial number of APA.
      log: Instance of system log file.
      createNew: True if this APA should be created should it not already exist.
    """

    # If there was an APA previously active, save it.
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
    self._layer = None
    self._calibrationFile = None
    self._calibration = None     # $$$DEBUG - Needed here?

    # Create directory if it doesn't exist.
    apaExists = os.path.exists( self._getPath() )
    pathsCreated = False
    if not apaExists and createNew :
      os.makedirs( self._getPath() )
      pathsCreated = True

    # Attach a log file such that all future messages are logged to this APA
    # as well.
    if apaExists or pathsCreated :
      self._log.attach( self._getPath() + AnodePlaneArray.LOG_FILE )

    if not apaExists :
      if createNew :
        self._log.add(
          self.__class__.__name__,
          "NEW",
          "Created new APA called " + self._name,
          [ self._name ]
        )
      else:
        self._log.add(
          self.__class__.__name__,
          "NEW",
          "Unable to load APA called " + self._name
            + ".  Active layer " + self._layer ,
          [ self._name, self._layer ]
        )

        # $$$DEBUG - Do we want to crash when a file is not found?
        raise Exception( "APA not found" )
    else:
      self.load()

  #---------------------------------------------------------------------
  def _getPath( self ) :
    """
    Get the path for all files related to this APA.
    """
    return self._apaDirectory + "/" + self._name + "/"

  #---------------------------------------------------------------------
  def _getG_CodeLogName( self, layer ) :
    """
    Get the name of the G-Code log for this layer.

    Args:
      layer: Name of the layer.
    """
    return self._getPath() + "/Layer" + layer + Settings.G_CODE_LOG_FILE

  #---------------------------------------------------------------------
  def loadRecipe( self, layer=None, recipeFile=None, startingLine=None ) :
    """
    Load a recipe file into GCodeHandler.

    Args:
      layer: The current working layer.
      recipeFile: File name of recipe to load.
      startingLine: What line to start from in recipe.

    Returns:
      True if there was an error, False if not.
    """
    isError = False

    if None != layer :
      self._layer = layer

    if "G" == self._layer :
      geometry = G_LayerGeometry()
    elif "U" == self._layer :
      geometry = U_LayerGeometry()
    elif "V" == self._layer :
      geometry = V_LayerGeometry()
    elif "X" == self._layer :
      geometry = X_LayerGeometry()
    else:
      raise Exception( "Recipe has no layer for geometry." )

    if None != recipeFile :
      self._recipeFile = recipeFile

    if None != startingLine :
      self._lineNumber = startingLine

    self._recipe = \
      Recipe( self._recipeDirectory + "/" + self._recipeFile, self._recipeArchiveDirectory )
    self._gCodeHandler.loadG_Code( self._recipe.getLines(), geometry )

    # Assign a G-Code log.
    gCodeLogName = self._getG_CodeLogName( self._layer )
    self._gCodeHandler.setGCodeLog( gCodeLogName )

    if not isError :
      isError |= self._gCodeHandler.setLine( self._lineNumber )
      if isError :
        error = "Invalid line number."

    if not isError :
      self._log.add(
        self.__class__.__name__,
        "GCODE",
        "Loaded G-Code file " + self._recipeFile
          + ", active layer " + self._layer
          + ", starting at line " + str( self._lineNumber ),
        [
          self._recipeFile,
          self._layer,
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

  #---------------------------------------------------------------------
  def load( self ) :
    """
    Load

    Returns:
      True if there was an error, False if not.
    """

    isError = False
    fileName = self._getPath() + AnodePlaneArray.FILE_NAME
    if os.path.isfile( fileName ) :
      # Log message about AHA change.
      self._log.add(
        self.__class__.__name__,
        "LOAD",
        "Loaded APA called " + self._name,
        [ self._name ]
      )
      xmlDocument = xml.dom.minidom.parse( fileName )
      node = xmlDocument.getElementsByTagName( "APA_" + self._name )
      self.unserialize( node[ 0 ] )

      if self._recipeFile :
        self.loadRecipe( self._layer )

      if self._calibrationFile :
        self._calibration = LayerCalibration.load( self._getPath(), self._calibrationFile )

        if not self._calibration :
          isError = True
          self._log.add(
            self.__class__.__name__,
            "LOAD",
            "Unable to load calibration for " + self._calibrationFile + ".",
            [ self._calibrationFile ]
          )
        else :
          self._log.add(
            self.__class__.__name__,
            "LOAD",
            "Loaded calibration file " + self._calibrationFile + ".",
            [ self._calibrationFile, self._calibration._hash ]
          )

          self._gCodeHandler.useCalibration( self._calibration )

        # $$$DEBUG - Pass calibration data to G-Code handler.

    else :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "LOAD",
        "Unable to load APA called " + self._name + ".  File not found.",
        [ self._name ]
      )

    return isError

  #---------------------------------------------------------------------
  def save( self ) :
    """
    Save state of APA to disk.
    """

    # Get the current line in G-Code.
    self._lineNumber = self._gCodeHandler.getLine()

    # Serialize data into XML.
    xmlDocument = xml.dom.minidom.parseString( '<AnodePlaneArray/>' )
    node = self.serialize( xmlDocument )
    xmlDocument.childNodes[ 0 ].appendChild( node )

    # Create text from XML data.
    outputText = xmlDocument.toprettyxml()

    # Strip off extraneous line feeds.
    outputText = \
      '\n'.join( [ line for line in outputText.split( '\n' ) if line.strip() ] ) + '\n'

    # Write XML data to file.
    with open( self._getPath() + AnodePlaneArray.FILE_NAME, "wb" ) as outputFile :
      outputFile.write( outputText )

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
      "Closing APA " + self._name + ", "
        + str( self._recipeFile ) + ":" + str( self._lineNumber ),
      [
        self._name,
        self._recipeFile,
        self._lineNumber
      ]
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
    node = xmlDocument.createElement( "APA_" + self._name )

    node.setAttribute( "calibrationFile", self._calibrationFile )
    node.setAttribute( "recipeFile", self._recipeFile )
    node.setAttribute( "lineNumber", str( self._lineNumber ) )
    node.setAttribute( "layer", str( self._layer ) )

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

    calibrationFile = node.getAttribute( "calibrationFile" )
    if "None" != calibrationFile :
      self._calibrationFile = calibrationFile
    else :
      self._calibrationFile = None

    layer = node.getAttribute( "layer" )
    if "None" != layer :
      self._layer = layer
    else :
      self._layer = None

    lineNumberString = node.getAttribute( "lineNumber" )
    if "None" != lineNumberString :
      self._lineNumber = int( lineNumberString )
    else :
      self._lineNumber = None

    return False


# end class
