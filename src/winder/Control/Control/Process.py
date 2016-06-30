###############################################################################
# Name: Process.py
# Uses: High-level process control.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os
import re
from Control.AnodePlaneArray import AnodePlaneArray
from Control.APA_Base import APA_Base
from Library.Spool import Spool
from Control.G_CodeHandler import G_CodeHandler
from Control.ControlStateMachine import ControlStateMachine

class Process :

  #---------------------------------------------------------------------
  def __init__( self, io, log, configuration, systemTime, machineCalibration ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      log: Log file to write state changes.
      configuration: Instance of Configuration.
      systemTime: Instance of TimeSource.
    """
    self._io = io
    self._log = log
    self._configuration = configuration
    self._systemTime = systemTime

    # $$$FUTURE - Change these settings.
    self.spool = Spool( 27000000, 5000 )

    self.controlStateMachine = ControlStateMachine( io, log, systemTime )

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

    self.gCodeHandler = G_CodeHandler( io, self.spool, machineCalibration )
    self.controlStateMachine.gCodeHandler = self.gCodeHandler

    maxVelocity = float( configuration.get( "maxVelocity" ) )

    # Setup initial limits on velocity and acceleration.
    io.plcLogic.setupLimits(
      maxVelocity,
      float( configuration.get( "maxAcceleration" ) ),
      float( configuration.get( "maxDeceleration" ) )
    )

    # Setup extended/retracted positions for head.
    io.head.setExtendedAndRetracted( machineCalibration.zFront, machineCalibration.zBack )

    # By default, the G-Code handler will use maximum velocity.
    self.gCodeHandler.setLimitVelocity( maxVelocity )
    self.gCodeHandler.setVelocity( maxVelocity )

    self._machineCalibration = machineCalibration

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

    # Fetch all files in recipe directory.
    recipeList = os.listdir( self._configuration.get( "recipeDirectory" ) )

    # Filter just the G-Code file extension.
    expression = re.compile( r'\.gc$' )
    recipeList = filter( lambda index: expression.search( index ), recipeList )

    return recipeList

  #---------------------------------------------------------------------
  def start( self ) :
    """
    Request that the winding process begin.
    """
    if self.controlStateMachine.isMovementReady() :

      self.controlStateMachine.startRequest = True
      self.controlStateMachine.stopRequest = False

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Request that the winding process stop.
    """
    if self.controlStateMachine.isInMotion() :
      self.controlStateMachine.startRequest = False
      self.controlStateMachine.stopRequest = True

  #---------------------------------------------------------------------
  def acknowledgeError( self ) :
    """
    Request that the winding process stop.
    """
    if self._io.plcLogic.isError() :
      self._log.add(
        self.__class__.__name__,
        "ERROR_RESET",
        "PLC error acknowledgment and clear."
      )

    self._io.plcLogic.reset()

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
      self.controlStateMachine.windTime = 0
      self.apa = \
        AnodePlaneArray(
          self.gCodeHandler,
          self._configuration.get( "APA_LogDirectory" ),
          self._configuration.get( "recipeDirectory" ),
          self._configuration.get( "recipeArchiveDirectory" ),
          apaName,
          self._log,
          self._systemTime,
          True
        )

    return isError

  #---------------------------------------------------------------------
  def getG_CodeList( self, center, delta ) :
    """
    Fetch a sub-set of the loaded G-Code self.lines.  Useful for showing what
    has recently executed, and what is to come.

    Args:
      center: Where to center the list.
      delta: Number of entries to read +/- center.

    Returns:
      List of G-Code lines, or empty list of no G-Code is loaded.
    """
    result = []
    if self.gCodeHandler.isG_CodeLoaded() :
      if None == center :
        center = self.gCodeHandler.getLine()

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
  def getG_CodeDirection( self ) :
    """
    Get the direction of G-Code execution.

    Returns:
      True for normal direction, False to run in reverse.  True if no G-Code
      is loaded.
    """
    result = True
    if self.gCodeHandler.isG_CodeLoaded() :
      result = self.gCodeHandler.getDirection()

    return result

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
  def getG_CodeLoop( self ) :
    """
    See if G-Code should loop continuously.

    Returns:
      True if G-Code should loop.
    """
    return self.controlStateMachine.loopMode

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
  def setG_CodeVelocityScale( self, scaleFactor=1.0 ) :
    """
    Set the velocity scale factor that limits the speed of all motions.

    Args:
      scaleFactor: New scale factor (typically between 0.0-1.0, although > 1 is
                   allowed).
    """
    self._log.add(
      self.__class__.__name__,
      "VELOCITY_SCALE",
      "G-Code velocity scale change from "
        + str( self.gCodeHandler.getVelocityScale() )
        + " to "
        + str( scaleFactor ),
      [ self.gCodeHandler.getVelocityScale(), scaleFactor ]
    )

    self.gCodeHandler.setVelocityScale( scaleFactor )

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
  def getAPA_DetailedList( self ) :
    """
    Return a detailed list of all the available APAs.

    Returns:
      Detailed list of all the available APAs.
    """

    directory = self._configuration.get( "APA_LogDirectory" )

    apaList = []
    for apaName in self.getAPA_List() :
      apaList.append( self.getAPA_Details( apaName ) )

    return apaList

  #---------------------------------------------------------------------
  def getAPA_Details( self, name ) :
    """
    Return details of about specified APA.

    Args:
      name: APA to retrieve details about.

    Returns:
      Dictionary with all APA details.
    """

    apa = APA_Base( self._configuration.get( "APA_LogDirectory" ), name )
    apa.load( "AnodePlaneArray" )

    return apa.toDictionary()

  #---------------------------------------------------------------------
  def getLoadedAPA_Name( self ) :
    """
    Get the name of the loaded APA.

    Returns:
      Name of the loaded APA or an empty string if no APA is loaded.
    """
    result = ""
    if self.apa :
      result = self.apa.getName()

    return result

  #---------------------------------------------------------------------
  def getRecipeName( self ) :
    """
    Return the name of the loaded recipe.

    Returns:
      String name of the loaded recipe.  Empty string if no recipe loaded.
    """
    result = ""
    if self.apa :
      result = self.apa.getRecipe()

    return result

  #---------------------------------------------------------------------
  def getRecipeLayer( self ) :
    """
    Return the current layer of the APA.

    Returns:
      String name of the current layer of the APA.  Empty string if no recipe
      loaded.
    """
    result = ""
    if self.apa :
      result = self.apa.getLayer()

    return result

  #---------------------------------------------------------------------
  def getStage( self ) :
    """
    Return the current stage of APA progress.

    Returns:
      Integer number (table in APA.Stages) of APA progress.
    """
    result = ""
    if self.apa :
      result = self.apa.getStage()

    return result

  #---------------------------------------------------------------------
  def switchAPA( self, apaName ) :
    """
    Load an APA from disk.

    Args:
      apaName: Name of the APA to load.  Must exist.
    """
    self.controlStateMachine.windTime = 0
    self.apa = \
      AnodePlaneArray(
        self.gCodeHandler,
        self._configuration.get( "APA_LogDirectory" ),
        self._configuration.get( "recipeDirectory" ),
        self._configuration.get( "recipeArchiveDirectory" ),
        apaName,
        self._log,
        self._systemTime,
        False
      )

  #---------------------------------------------------------------------
  def closeAPA( self ) :
    """
    Close APA and store on disk.  Call at program exit.  No additional uses.
    """

    if self.apa :
      self.apa.addWindTime( self.controlStateMachine.windTime )
      self.apa.close()
      self.apa = None

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
  def manualSeekXY( self, xPosition=None, yPosition=None, velocity=None ) :
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
  def manualHeadPosition( self, position, velocity ) :
    """
    Manually position the head.

    Args:
      position: One of the Head positions (RETRACTED/FRONT/BACK/EXTENDED).
      velocity: Maximum speed at which to move.

    Returns:
      True if there was an error, False if not.
    """
    isError = True

    if self.controlStateMachine.isMovementReady() and self._io.head.getPosition() != position :
      isError = False

      self._log.add(
        self.__class__.__name__,
        "HEAD",
        "Manual head position to " + str( position ) + " at " + str( velocity ) + ".",
        [ position, velocity ]
      )
      self.controlStateMachine.setHeadPosition = position
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.manualRequest = True

    else :
      self._log.add(
        self.__class__.__name__,
        "HEAD",
        "Manual head position ignored.",
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

  #---------------------------------------------------------------------
  def seekPin( self, pin, velocity ) :
    """
    Manually seek out a pin location.

    Args:
      pin - Name of pin to seek.
      velocity: Speed of z axis in m/s.

    Returns:
      True if there was an error, False if not.
    """
    calibration = self.gCodeHandler.getLayerCalibration()

    isError = True

    # Do we have a calibration file?
    if calibration :
      # Does request pin exist?
      if calibration.getPinExists( pin ) :
        self._log.add(
          self.__class__.__name__,
          "SEEK_PIN",
          "Manual pin seek " + pin + " at " + str( velocity ) +".",
          [ pin, velocity ]
        )
        position = calibration.getPinLocation( pin )
        position = position.add( calibration.offset )
        self.manualSeekXY( position.x, position.y, velocity )
        isError = False
      else:
        self._log.add(
          self.__class__.__name__,
          "SEEK_PIN",
          "Manual pin seek request ignored--pin does not exist.",
          [ pin, velocity ]
        )
    else:
      self._log.add(
        self.__class__.__name__,
        "SEEK_PIN",
        "Manual pin seek request ignored--no calibration loaded.",
        [ pin, velocity ]
      )


    return isError

# end class
