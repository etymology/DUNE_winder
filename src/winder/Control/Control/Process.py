###############################################################################
# Name: Process.py
# Uses: High-level process control.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os
from Control.AnodePlaneArray import AnodePlaneArray
from Library.Spool import Spool
from Control.G_CodeHandler import G_CodeHandler
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
    self.spool = Spool( 27000000, 50 )
    self.gCodeHandler = G_CodeHandler( io, self.spool )
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
    if self.gCodeHandler.isG_CodeLoaded() :
      result = self.gCodeHandler.fetchLines( center, delta )

    return result

  #---------------------------------------------------------------------
  def setG_CodeLine( self, line ) :
    """
    Set a new line number from loaded recipe to seek.

    Args:
      line: Line number.

    Returns:
      True if there was an error, False if not.
    """
    isError = True
    if self.gCodeHandler.isG_CodeLoaded() :
      initialLine = self.gCodeHandler.getLine()
      isError = self.gCodeHandler.setLine( line )

      if not isError :
        self._log.add(
          self.__class__.__name__,
          "LINE",
          "G-Code line changed from " + str( initialLine ) + " to " + str( line ),
          [ initialLine, line ]
        )

    if isError :
      self._log.add(
        self.__class__.__name__,
        "LINE",
        "Unable to change G-Code line changed to " + str( line ),
        [ line ]
      )

    return isError

  #---------------------------------------------------------------------
  def setG_CodeDirection( self, isForward ) :
    """
    Set the direction of G-Code execution.

    Args:
      isForward: True for normal direction, False to run in reverse.
    """
    isError = True
    if self.gCodeHandler.isG_CodeLoaded() :
      initialDirection = self.gCodeHandler.getDirection()
      isError = self.gCodeHandler.setDirection( isForward )

      if not isError :
        self._log.add(
          self.__class__.__name__,
          "DIRECTION",
          "G-Code direction changed from " + str( initialDirection ) + " to " + str( isForward ),
          [ initialDirection, isForward ]
        )

    if isError :
      self._log.add(
        self.__class__.__name__,
        "LINE",
        "Unable to change G-Code direction changed to " + str( isForward ),
        [ isForward ]
      )


    return isError

  #---------------------------------------------------------------------
  def setG_CodeRunToLine( self, line ) :
    """
    Set the line number to run G-Code and then stop.
    """
    isError = True
    if self.gCodeHandler.isG_CodeLoaded() :
      initialRunTo = self.gCodeHandler.runToLine
      #isError = self.gCodeHandler.setDirection( isForward )
      self.gCodeHandler.runToLine = line
      isError = False

      if not isError :
        self._log.add(
          self.__class__.__name__,
          "RUN_TO",
          "G-Code finial line changed from " + str( initialRunTo ) + " to " + str( line ),
          [ initialRunTo, line ]
        )

    if isError :
      self._log.add(
        self.__class__.__name__,
        "LINE",
        "Unable to change G-Code run to line to " + str( line ),
        [ line ]
      )


    return isError

  #---------------------------------------------------------------------
  def setG_CodeLoop( self, isLoopMode ) :
    """
    Specify if the G-Code should loop continuously.  Useful for testing
    but not production.

    Args:
      isLoopMode: True if G-Code should loop.
    """
    self._log.add(
      self.__class__.__name__,
      "LOOP",
      "G-Code loop mode set from "
        + str( self.controlStateMachine.loopMode )
        + " to "
        + str( isLoopMode ),
      [ self.controlStateMachine.loopMode, isLoopMode ]
    )

    self.controlStateMachine.loopMode = isLoopMode

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
        "Jog X/Y request ignored.",
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
    else :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Manual move X/Y ignored.",
        [ xPosition, yPosition, velocity ]
      )

    return isError

  #---------------------------------------------------------------------
  def manualSeekZ( self, position, velocity=None ) :
    """
    Seek an Z location.

    Args:
      position: New position in meters of z.
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
        "Manual move Z to " + str( position ) + " at " + str( velocity ) + ".",
        [ position, velocity ]
      )
      self.controlStateMachine.seekZ = position
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.manualRequest = True
    else :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Manual move Z ignored.",
        [ position, velocity ]
      )

    return isError

  #---------------------------------------------------------------------
  def jogZ( self, velocity ) :
    """
    Jog the Z axis at a given velocity.

    Args:
      velocity: Speed of z axis in m/s.  Allows negative for reverse, 0 to stop.

    Returns:
      True if there was an error, False if not.
    """

    isError = False
    if 0 != velocity and self.controlStateMachine.isMovementReady() :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog Z at " + str( velocity ) + ".",
        [ velocity ]
      )
      self.controlStateMachine.manualRequest = True
      self.controlStateMachine.isJogging = True
      self._io.plcLogic.jogZ( velocity )
    elif 0 == velocity and self.controlStateMachine.isJogging :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog Z stop."
      )
      self.controlStateMachine.isJogging = False
      self._io.plcLogic.jogZ( velocity )
    else:
      isError = True
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog Z request ignored.",
        [ velocity ]
      )

    return isError

# end class
