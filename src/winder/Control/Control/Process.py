###############################################################################
# Name: Process.py
# Uses: High-level process control.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-03-01 - QUE - Creation.
###############################################################################

import os
from AnodePlaneArray import AnodePlaneArray
from Control.GCodeHandler import GCodeHandler
from Control.ControlStateMachine import ControlStateMachine

class Process :

  #---------------------------------------------------------------------
  def __init__( self, io, log, configuration ) :
    """
    Constructor.
    """
    self._io = io
    self._log = log
    self._configuration = configuration
    self.gCodeHandler = GCodeHandler( io )
    self.controlStateMachine = ControlStateMachine( io, log )

    self.controlStateMachine.gCodeHandler = self.gCodeHandler

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
    self.controlStateMachine.startRequest = True

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Request that the winding process stop.
    """
    self.controlStateMachine.stopRequest = True

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
            self.gCodeHandler,
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
    self.apa = \
      AnodePlaneArray(
        self.gCodeHandler,
        self._configuration.get( "APA_LogDirectory" ),
        self._configuration.get( "recipeDirectory" ),
        self._configuration.get( "recipeArchiveDirectory" ),
        apaName,
        self._log,
        False
      )
    #isError = False
    #try:
    #  self.apa = \
    #    AnodePlaneArray(
    #      self.gCodeHandler,
    #      self._configuration.get( "APA_LogDirectory" ),
    #      self._configuration.get( "recipeDirectory" ),
    #      self._configuration.get( "recipeArchiveDirectory" ),
    #      apaName,
    #      self._log,
    #      False
    #    )
    #except Exception as exception:
    #  isError = True
    #
    #return isError

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
    if ( 0 != xVelocity or 0 != yVelocity ) and self.controlStateMachine.isMovementReady() :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog X/Y at " + str( xVelocity ) + ", " + str( yVelocity ) + ".",
        [ xVelocity, yVelocity ]
      )
      self.controlStateMachine.manualRequest = True
      self.controlStateMachine.isJogging = True
      self._io.plcLogic.jogXY( xVelocity, yVelocity )
    elif 0 == xVelocity and 0 == yVelocity and self.controlStateMachine.isJogging :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog X/Y stop."
      )
      self.controlStateMachine.isJogging = False
      self._io.plcLogic.jogXY( xVelocity, yVelocity )
    else:
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog request ignored.",
        [ xVelocity, yVelocity ]
      )
  #---------------------------------------------------------------------
  def manualSeekXY( self, xPosition, yPosition, velocity=None ) :
    """
    $$$DEBUG
    """
    if self.controlStateMachine.isMovementReady() :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Manual move X/Y to (" + str( xPosition ) + ", " + str( yPosition ) + ") at " + str( velocity ) + ".",
        [ xPosition, yPosition, velocity ]
      )
      self.controlStateMachine.seekX = xPosition
      self.controlStateMachine.seekY = yPosition
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.manualRequest = True

# end class
