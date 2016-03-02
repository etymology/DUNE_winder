###############################################################################
# Name: Process.py
# Uses: $$$DEBUG
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-03-01 - QUE - Creation.
###############################################################################

import os
from AnodePlaneArray import AnodePlaneArray

class Process :

  #---------------------------------------------------------------------
  def __init__( self, io, log, configuration, gCodeHandler, controlStateMachine ) :
    """
    Constructor.
    """
    self._io = io
    self._log = log
    self._configuration = configuration
    self._gCodeHandler = gCodeHandler
    self._controlStateMachine = controlStateMachine

    self.apa = None

  #---------------------------------------------------------------------
  def setWireLength( self, length ) :
    """
    Set the length of wire currently on the spool.

    Args:
      length: Length of wire (in millimeters).
    """
    pass

  #---------------------------------------------------------------------
  def getRemainingWire( self ) :
    """
    Get the amount of wire remaining on the spool.
    """
    pass

  #---------------------------------------------------------------------
  def setMinimumWire( self, length ) :
    """
    Set minimal amount of wire before automatic wind mode stops.

    Args:
      length: Minimal length in millimeters.
    """
    pass

  #---------------------------------------------------------------------
  def getRecipes( self ) :
    """
    Return a list of available recipes based on the files in the recipe
    directory.

    Returns:
      List of available recipes.
    """
    recipeList = os.listdir( self._configuration.get( "recipeDirectory" ) )
    return recipeList

  #---------------------------------------------------------------------
  def start( self ) :
    """
    Request that the winding process begin.
    """
    self._controlStateMachine.startRequest = True

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Request that the winding process stop.
    """
    self._controlStateMachine.stopRequest = True

  #---------------------------------------------------------------------
  def createAPA( self, apaName ) :
    """
    Create a new APA.

    Returns:
      True if there was an error (including if the APA already exists), False
      for no error.
    """
    isError = False

    apaList = self.getAPA_List()

    # Make sure APA name isn't already in list.
    if apaName in apaList :
      isError = True
    else:
      try:
        self.apa = \
          AnodePlaneArray(
            self._gCodeHandler,
            self._configuration.get( "APA_LogDirectory" ),
            self._configuration.get( "recipeDirectory" ),
            apaName,
            self._log,
            True
          )
      except:
        isError = True

    return isError

  #---------------------------------------------------------------------
  def getAPA_List( self ) :
    """
    Return a list of all the available APAs based on file in APA directory.

    Returns:
      List of all the available APAs.
    """
    apaList = os.listdir( self._configuration.get( "APA_LogDirectory" ) )
    return apaList

  #---------------------------------------------------------------------
  def switchAPA( self, apaName ) :
    """
    Load an APA from disk.

    Args:
      apaName: Name of the APA to load.  Must exist.

    Returns:
      True if there was an error, False if not.
    """
    isError = False
    try:
      self.apa = \
        AnodePlaneArray(
          self._gCodeHandler,
          self._configuration.get( "APA_LogDirectory" ),
          self._configuration.get( "recipeDirectory" ),
          apaName,
          self._log,
          False
        )
    except:
      isError = True

    return isError

  #---------------------------------------------------------------------
  def closeAPA( self ) :
    """
    Close APA and store on disk.  Call at program exit.
    """

    if self.apa :
      self.apa.close()

    pass

  #---------------------------------------------------------------------
  def jogXY( self, xVelocity, yVelocity ) :
    """
    $$$DEBUG
    """
    pass

  #---------------------------------------------------------------------
  def manualSeekXY( self, xPosition, yPosition ) :
    """
    $$$DEBUG
    """
    pass

# end class
