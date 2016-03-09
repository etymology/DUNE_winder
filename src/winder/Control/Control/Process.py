###############################################################################
# Name: Process.py
# Uses: High-level process control.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os
from AnodePlaneArray import AnodePlaneArray
from Library.Spool import Spool
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
    self.spool = Spool( 100, 50 )
    self.gCodeHandler = GCodeHandler( io, self.spool )
    self.controlStateMachine = ControlStateMachine( io, log )

    self.controlStateMachine.gCodeHandler = self.gCodeHandler

    self.apa = None

    path = self._configuration.get( "APA_LogDirectory" )
    if not os.path.exists( path ) :
      os.makedirs( path )

    path = self._configuration.get( "recipeArchiveDirectory" )
    if not os.path.exists( path ) :
      os.makedirs( path )

    path = self._configuration.get( "recipeDirectory" )
    if not os.path.exists( path ) :
      raise Exception( "Recipe directory (" + path + ") does not exist." )

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
  def start( self, isLoopMode=False ) :
    """
    Request that the winding process begin.

    Args:
      isLoopMode: True to continuously loop this G-Code (debug only).
    """
    self.controlStateMachine.startRequest = True
    self.controlStateMachine.loopMode = isLoopMode

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

    assert( "" != apaName )

    apaList = self.getAPA_List()

    # Make sure APA name isn't already in list.
    if apaName in apaList :
      isError = True
    else:
      self.apa = \
        AnodePlaneArray(
          self.gCodeHandler,
          self._configuration.get( "APA_LogDirectory" ),
          self._configuration.get( "recipeDirectory" ),
          self._configuration.get( "recipeArchiveDirectory" ),
          apaName,
          self._log,
          True
        )

    return isError

  #---------------------------------------------------------------------
  def getG_CodeList( self, center, delta ) :
    result = []
    if self.gCodeHandler.gCode :
      result = self.gCodeHandler.gCode.fetchLines( center, delta )

    return result

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

  #---------------------------------------------------------------------
  def closeAPA( self ) :
    """
    Close APA and store on disk.  Call at program exit.  No additional uses.
    """

    if self.apa :
      self.apa.close()

  #---------------------------------------------------------------------
  def jogXY( self, xVelocity, yVelocity ) :
    """
    Jog the X/Y axis at a given velocity.

    Args:
      xVelocity: Speed of x axis in m/s.  Allows negative for reverse, 0 to stop.
      yVelocity: Speed of y axis in m/s.  Allows negative for reverse, 0 to stop.

    Returns:
      True if there was an error, False if not.
    """

    isError = False
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
      isError = True
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog request ignored.",
        [ xVelocity, yVelocity ]
      )

    return isError
  #---------------------------------------------------------------------
  def manualSeekXY( self, xPosition, yPosition, velocity=None ) :
    """
    Seek an X/Y location.

    Args:
      xPosition: New position in meters of x.
      yPosition: New position in meters of y.
      velocity: Maximum velocity.  None for last velocity used.
    Returns:
      True if there was an error, False if not.
    """

    isError = True
    if self.controlStateMachine.isMovementReady() :
      isError = False
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Manual move X/Y to (" + str( xPosition )
          + ", " + str( yPosition ) + ") at " + str( velocity ) + ".",
        [ xPosition, yPosition, velocity ]
      )
      self.controlStateMachine.seekX = xPosition
      self.controlStateMachine.seekY = yPosition
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.manualRequest = True

    return isError

# end class
