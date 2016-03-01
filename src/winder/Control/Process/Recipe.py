###############################################################################
# Name: Recipe.py
# Uses: $$$DEBUG
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-03-01 - QUE - Creation.
###############################################################################

from Library.Serializable import Serializable
import xml.dom.minidom

class Recipe( Serializable ) :

  #---------------------------------------------------------------------
  def __init__( self, name, recipeFile, log ) :
    """
    Constructor.
    """

    self._name = name
    self._recipeFile = recipeFile
    self._log = log
    self._lineNumber = 0

  #---------------------------------------------------------------------
  def load( self, gCodeHandler ) :
    """
    Load
    """
    self._log.add(
      __class__.__name__,
      "LOAD",
      "Recipe loaded, file: " + self._recipeFile
        + " starting a line: " + str( self._lineNumber ),
      [ self._recipeFile, self._lineNumber ]
    )

    gCodeHandler.loadG_Code( self._recipeFile )
    gCodeHandler.setLine( self.lineNumber )

  #---------------------------------------------------------------------
  def serialize( self, xml ) :
    """
    Turn this object into an XML node.

    Args:
      xml: Instance of xml.dom.minidom.Document.

    Returns:
      Must return an XML node with the data from this object.
    """
    node = xml.createElement( __class__.__name__ )

    node.setAttribute( "name", self._name )
    node.setAttribute( "lineNumber", self._lineNumber )

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
    self._name = node.getAttribute( "name" )
    self._lineNumber = node.getAttribute( "lineNumber" )

    return False


# end class
