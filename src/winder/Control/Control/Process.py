###############################################################################
# Name: Process.py
# Uses: High-level process control.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import os
import re
import math

from Library.Geometry.Location import Location
from Library.G_Code import G_Code

from Control.AnodePlaneArray import AnodePlaneArray
from Control.APA_Base import APA_Base
from Control.G_CodeHandler import G_CodeHandler
from Control.ControlStateMachine import ControlStateMachine
from Control.CameraCalibration import CameraCalibration

from Machine.Spool import Spool
from Machine.HeadCompensation import HeadCompensation
from Machine.GeometrySelection import GeometrySelection
from Machine.LayerFunctions import LayerFunctions
from Machine.DefaultCalibration import DefaultLayerCalibration

class Process :

  STAGE_TABLE = {
    0  : None,                                         # Uninitialized.
    1  : { "layer" : "X", "recipe" : "X-Layer_1.gc" }, # X-first.
    2  : { "layer" : "X", "recipe" : "X-Layer_2.gc" }, # X-second.
    3  : { "layer" : "V", "recipe" : "V-Layer_1.gc" }, # V-first.
    4  : { "layer" : "V", "recipe" : "V-Layer_2.gc" }, # V-second.
    5  : { "layer" : "U", "recipe" : "U-Layer_1.gc" }, # U-first.
    6  : { "layer" : "U", "recipe" : "U-Layer_2.gc" }, # U-second.
    7  : { "layer" : "G", "recipe" : "G-Layer_1.gc" }, # G-first.
    8  : { "layer" : "G", "recipe" : "G-Layer_2.gc" }, # G-second.
    9  : None,                                         # Sign-off.
    10 : None                                          # Complete.
  }

  #---------------------------------------------------------------------
  def __init__( self, io, log, configuration, systemTime, machineCalibration ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      log: Log file to write state changes.
      configuration: Instance of Configuration.
      systemTime: Instance of TimeSource.
      machineCalibration: Machine calibration instance.
    """
    self._io = io
    self._log = log
    self._configuration = configuration
    self._systemTime = systemTime

    # $$$FUTURE - Change these settings.
    self.spool = Spool( 27000000, 5000 )

    self.controlStateMachine = ControlStateMachine( io, log, systemTime )
    self.headCompensation = HeadCompensation( machineCalibration )

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

    self.gCodeHandler = G_CodeHandler( io, self.spool, machineCalibration, self.headCompensation )
    self.controlStateMachine.gCodeHandler = self.gCodeHandler

    self._maxVelocity = float( configuration.get( "maxVelocity" ) )
    self._maxSlowVelocity = float( configuration.get( "maxSlowVelocity" ) )

    # Setup initial limits on velocity and acceleration.
    io.plcLogic.setupLimits(
      self._maxVelocity,
      float( configuration.get( "maxAcceleration" ) ),
      float( configuration.get( "maxDeceleration" ) )
    )

    self._cameraURL = configuration.get( "cameraURL" )

    # Setup extended/retracted positions for head.
    io.head.setExtendedAndRetracted( machineCalibration.zFront, machineCalibration.zBack )

    # By default, the G-Code handler will use maximum velocity.
    self.gCodeHandler.setLimitVelocity( self._maxVelocity )

    # Set the limits to prevent manually inputting wrong coordinate values
    self._machineCalibration = machineCalibration
    self._transferLeft = float( self._machineCalibration.get( "transferLeft" ) )
    self._transferRight = float( self._machineCalibration.get( "transferRight" ) )
    self._limitLeft = float( self._machineCalibration.get( "limitLeft" ) )
    self._limitRight = float( self._machineCalibration.get( "limitRight" ) )
    self._limitTop = float( self._machineCalibration.get( "limitTop" ) )
    self._limitBottom = float( self._machineCalibration.get( "limitBottom" ) )
    self._zlimitFront = float( self._machineCalibration.get( "zLimitFront" ) )
    self._zlimitRear = float( self._machineCalibration.get( "zLimitRear" ) )

    self.cameraCalibration = CameraCalibration( io )
    self.cameraCalibration.pixelsPer_mm( configuration.get( "pixelsPer_mm" ) )

    self.controlStateMachine.cameraCalibration = self.cameraCalibration
    self.controlStateMachine.machineCalibration= self._machineCalibration

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
  def stopNextLine( self ) :
    """
    Stop winding process after completing the next line.
    """
    if self.controlStateMachine.isInMotion() \
      and self.gCodeHandler.isG_CodeLoaded() :
        self.gCodeHandler.stopNext()

  #---------------------------------------------------------------------
  def step( self ) :
    """
    Run just one line of G-Code, then stop.
    """
    if self.controlStateMachine.isMovementReady() \
      and self.gCodeHandler.isG_CodeLoaded() :
        self.gCodeHandler.singleStep = True
        self.controlStateMachine.startRequest = True
        self.controlStateMachine.stopRequest = False

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
  # Phil Heath (PWH)
  # Added 19/08/2021 for the PLC_Init button
  #
  #---------------------------------------------------------------------
  def acknowledgePLC_Init( self ) :
  #  """
  #  Request that the winding process init.
  #  """
  
    print("Hello World!")
    self._io.plcLogic.PLC_init()
  
  #---------------------------------------------------------------------
  def servoDisable( self ) :
    """
    Disable motor servo control, thus idling the axises.
    """
    if self.controlStateMachine.isInMotion() :
      self._log.add(
        self.__class__.__name__,
        "SERVO",
        "Idling servo control."
      )
      self.controlStateMachine.manualRequest = True
      self.controlStateMachine.idleServos    = True

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
  def setStage( self, stage, message="<unspecified>" ) :
    """
    Set the APA progress stage.

    Args:
      stage: Integer number (table in APA_Base.Stages) of APA progress.
      message: Message/reason for changing to new stage.
    """
    isError = False

    if not self.apa :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "STATE_SET",
        "Unable to set state--no APA loaded.",
        [ stage, message ]
      )

    if not isError :
      if stage in Process.STAGE_TABLE :
        settings = Process.STAGE_TABLE[ stage ]
        self.apa.setStage( stage, message )
        self.apa.closeLoadedRecipe()
        if settings :
          layer = settings[ "layer" ]
          recipe = settings[ "recipe" ]
          geometry = GeometrySelection( layer )

          self.apa.setupBlankCalibration( layer, geometry )
          self.apa.loadRecipe( layer, recipe )
      else :
        isError = True

        self._log.add(
          self.__class__.__name__,
          "STATE_SET",
          "Unable to set state--unknown state " + str( stage ),
          [ stage, message ]
        )

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
  def getPositionLogging( self ) :
    """
    Check to see if position logging is enabled.

    Returns:
      True if position logging is enabled.
    """

    return self.gCodeHandler.isPositionLogging()

  #---------------------------------------------------------------------
  def setPositionLogging( self, isEnabled ) :
    """
    Enable/disable position logging.  Test function.

    Args:
      isEnabled: True to enable logging, False to disable/stop.

    Returns:
      True if logging was enabled, False if not.
    """
    fileName = None
    if isEnabled :
      if self.apa :
        fileName = self.apa.getPath() + "positionLog.csv"
        self._log.add(
          self.__class__.__name__,
          "POSITION_LOGGING",
          "Position logging begins",
          [ 1, fileName ]
        )
      else:
        self._log.add(
          self.__class__.__name__,
          "POSITION_LOGGING",
          "Position logging request ignored.  No APA loaded.",
          [ -1 ]
        )
    else:
      self._log.add(
        self.__class__.__name__,
        "POSITION_LOGGING",
        "Position logging ends",
        [ 0 ]
      )

    self.gCodeHandler.startPositionLogging( fileName )

    return self.getPositionLogging()

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
      String name of the current layer of the APA.  None if no recipe
      loaded.
    """
    result = None
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
  def maxVelocity( self, maxVelocity=None ) :
    """
    Set/get the maximum velocity used by PLC logic and G-Code handler.

    Args:
      maxVelocity: New maximum velocity (optional).

    Returns:
      Maximum velocity.
    """

    if None != maxVelocity :
      self._maxVelocity = maxVelocity
      self._io.plcLogic.maxVelocity( maxVelocity )
      self.gCodeHandler.setLimitVelocity( maxVelocity )

    return self._maxVelocity

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
      self.controlStateMachine.windTime = 0
      self.apa.close()
      self.apa = None

  #---------------------------------------------------------------------
  def jogXY( self, xVelocity, yVelocity, acceleration=None, deceleration=None ) :
    """
    Jog the X/Y axis at a given velocity.

    Args:
      xVelocity: Speed of x axis in m/s.  Allows negative for reverse, 0 to stop.
      yVelocity: Speed of y axis in m/s.  Allows negative for reverse, 0 to stop.
      acceleration: Maximum positive acceleration.  None for default.
      deceleration: Maximum negative acceleration.  None for default.
      Safe Zone: If JogXY is working outside the _transferRight and _transferLeft regions
                 then the velocity of the Jog will be reduced to maxSlowVelocity in X and Y.
    Returns:
      True if there was an error, False if not.
    """

    isError = False
    if ( 0 != xVelocity or 0 != yVelocity ) and self.controlStateMachine.isMovementReady() :
      #Current coordinates to find out if we are in Safety Zone
      x = self._io.xAxis.getPosition()
      y = self._io.yAxis.getPosition()
      z = self._io.zAxis.getPosition()
      if x < self._transferLeft  or x > self._transferRight : # reduce the Job velocity to maxSlowVelocity
        if ( xVelocity != 0 ) :
          xVelocity = math.copysign(self._maxSlowVelocity,xVelocity)
        if ( yVelocity != 0 ) :
          yVelocity = math.copysign(self._maxSlowVelocity,yVelocity)

      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Jog X/Y at " + str( xVelocity ) + ", " + str( yVelocity ) + " m/s, "
          + str( acceleration ) + ", " + str( deceleration ) + " m/s^2.",
        [ xVelocity, yVelocity, acceleration, deceleration ]
      )

      self.controlStateMachine.manualRequest = True
      self.controlStateMachine.isJogging = True
      self._io.plcLogic.jogXY( xVelocity, yVelocity, acceleration, deceleration )
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
        [ xVelocity, yVelocity, acceleration, deceleration ]
      )

    return isError

  #---------------------------------------------------------------------
  def manualSeekXY( self, xPosition=None, yPosition=None, velocity=None, acceleration=None, deceleration=None ) :
    """
    Seek an X/Y location.

    Args:
      xPosition: New position in meters of x.
      yPosition: New position in meters of y.
      velocity: Maximum velocity.  None for last velocity used.
      acceleration: Maximum positive acceleration.  None for default.
      deceleration: Maximum negative acceleration.  None for default.
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
          + ", " + str( yPosition ) + ") at " + str( velocity ) + ", "
          + str( acceleration ) + ", " + str( deceleration ) + " m/s^2.",
        [ xPosition, yPosition, velocity, acceleration, deceleration ]
      )
      self.controlStateMachine.seekX = xPosition
      self.controlStateMachine.seekY = yPosition
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.seekAcceleration = acceleration
      self.controlStateMachine.seekDeceleration = deceleration
      self.controlStateMachine.manualRequest = True
    else :
      self._log.add(
        self.__class__.__name__,
        "JOG",
        "Manual move X/Y ignored.",
        [ xPosition, yPosition, velocity, acceleration, deceleration ]
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

      # Two pins may be specified.  If they are, get both names.  If not, set
      # both names to the single name given.
      pinNameA = pin
      pinNameB = pin
      if " " in pin :
        [ pinNameA, pinNameB ] = pin.split( ' ' )

      # Does request pin exist?
      if calibration.getPinExists( pinNameA ) \
        and calibration.getPinExists( pinNameB ) :
          self._log.add(
            self.__class__.__name__,
            "SEEK_PIN",
            "Manual pin seek " + pin + " at " + str( velocity ) +".",
            [ pin, velocity ]
          )

          # Get the center of the pins.
          pinA = calibration.getPinLocation( pinNameA )
          pinB = calibration.getPinLocation( pinNameB )
          position = pinA.center( pinB )
          position = position.add( calibration.offset )

          # Run a manual seek to pin/center position.
          self.manualSeekXY( position.x, position.y, velocity )
          isError = False
      else:
        self._log.add(
          self.__class__.__name__,
          "SEEK_PIN",
          "Manual pin seek request ignored--pin(s) does not exist.",
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

  #---------------------------------------------------------------------
  def seekPinNominal( self, pin, velocity ) :
    """
    Seek out the nominal pin location.
    Useful for calibration scan setup.

    Args:
      pin - Name of pin to seek.
      velocity: Speed of z axis in m/s.

    Returns:
      True if there was an error, False if not.
    """
    isError = True
    if self.apa :
      # Get the name of this layer.
      layer = self.apa.getLayer()

      # Get the default calibration for this layer.
      calibration = DefaultLayerCalibration( None, None, layer )

      # Does request pin exist?
      if calibration.getPinExists( pin ) :
        self._log.add(
          self.__class__.__name__,
          "SEEK_PIN_NOMINAL",
          "Nominal pin seek " + pin + " at " + str( velocity ) +".",
          [ pin, velocity ]
        )

        # Get the center of the pins.
        position = calibration.getPinLocation( pin )
        position = position.add( calibration.offset )

        # Run a manual seek to pin position.
        self.manualSeekXY( position.x, position.y, velocity )
        isError = False
      else:
        self._log.add(
          self.__class__.__name__,
          "SEEK_PIN_NOMINAL",
          "Nominal pin seek request ignored--pin(s) does not exist.",
          [ pin, velocity ]
        )
    else:
      self._log.add(
        self.__class__.__name__,
        "SEEK_PIN_NOMINAL",
        "Nominal pin seek request ignored--no APA loaded.",
        [ pin, velocity ]
      )

    return isError

  #---------------------------------------------------------------------
  def setAnchorPoint( self, pinA, pinB = None ) :
    """
    Specify the anchor point--location where the wire is assume to be fixed.

    Args:
      pinA - Pin name.  First name when using pin centering.
      pinB - Pin name.  Second name for pin centering, omit to use just one pin.
    """
    calibration = self.gCodeHandler.getLayerCalibration()

    isError = True

    # Do we have a calibration file?
    if calibration :

      # Get first pin location.
      pinA = calibration.getPinLocation( pinA )

      if pinA :
        # Do we have a second pin?
        if pinB :
          # Center between two pins.
          pinB = calibration.getPinLocation( pinB )

          if pinB :
            location = pinA.center( pinB )
        else :
          # Use the specified location.
          location = pinA

        location = location.add( calibration.offset )

        self.headCompensation.anchorPoint( location )
        isError = False

    return isError

  #---------------------------------------------------------------------
  def getHeadAngle( self ) :
    """
    Get the current angle of the arm based on machine position and the last
    anchor point.

    Args:
      location: Location of actual machine position.

    Returns:
      Angle of the arm (-pi to +pi).
    """

    result = 0
    if self._io.isFunctional() :
      x = self._io.xAxis.getPosition()
      y = self._io.yAxis.getPosition()
      z = self._io.zAxis.getPosition()

      # $$$FUTURE - This doesn't work.  Not too important.  Fix it one day.
      # if self._io.head.BACK == self._io.head.getSide() :
      #   print "Back"
      #   z = self._io.head.getTargetAxisPosition()

      location = Location( x, y, z )

      result = self.headCompensation.getHeadAngle( location )

    return result

  #---------------------------------------------------------------------
  def executeG_CodeLine( self, line ) :
    """
    Run a line of G-code.

    Args:
      line: G-Code to execute.

    Returns:
      Failure data.  None if there was no failure.
    """
    error = None
    if not self.controlStateMachine.isMovementReady() :
      error = "Machine not ready."
      self._log.add(
        self.__class__.__name__,
        "MANUAL_GCODE",
        "Failed to execute manual G-Code line as machine was not ready.",
        [ line ]
      )
      
    else :
      #Check the format of the string matches a VALID PATTERN
      xy = '(\ *[X]\d{1,4}(\.\d{1,2})?\ *[Y]\d{1,4}(\.\d{1,2})?\ *$)'   # 'X1234 Y1234','X0 Y1234'
      gxy = '(\ *[G]105\ *[P][XY]-?\d{1,3}(\.\d{1,2})?\ *$)'  # 'G105 PX123','G105  PY123',G105  PY-12', 'G105  PX-123'
      gx_y = '(\ *[G]105\ *[P][X]-?\d{1,3}(\.\d{1,2})?\ *[P][Y]-?\d{1,3}(\.\d{1,2})?\ *$)' # 'G105  PX123 PY123'
      xyf = '(\ *[X]\d{1,4}(\.\d{1,2})?\ *[Y]\d{1,4}(\.\d{1,2})?\ *[F]\d{1,3}\ *$)'    # 'X1234 Y1234 F123'
      fxy = '(\ *[F]\d{1,3}\ *[X]\d{1,4}(\.\d{1,2})?\ *[Y]\d{1,4}(\.\d{1,2})?\ *$)'    # 'X1234 Y1234 F123' 
      gxyf = '(\ *[G]105\ *[P][XY]-?\d{1,3}(\.\d{1,2})?\ *[F]\d{1,3}\ *$)'   # 'G105 PX123 F12','G105 PY123 F123'
      gx_yf = '(\ *[G]105\ *[P][X]-?\d{1,3}(\.\d{1,2})?\ *[P][Y]-?\d{1,3}(\.\d{1,2})?\ *[F]\d{1,3}\ *$)' # 'G105  PX123 PY123 F123'
      gp = '(\ *[G]106\ *P[0123]\ *$)' # 'G106 P0', ..., 'G106 P4'
      z = '(\ *[Z]-?\d{1,3}\ *$)'  # 'Z123' , 'Z-123'
      if not re.match(xy+'|'+gxy+'|'+xyf+'|'+fxy+'|'+gxyf+'|'+gx_y+'|'+gx_yf+'|'+gp+'|'+z, line) :
        error = "Invalid G-code format or coordinates exceeding the maximun digits allowed [X1234] : "+line

      #Check that X and Y input coordinate are within limits
      #Get the current positions 
      xPosition = self._io.xAxis.getPosition()
      yPosition  = self._io.yAxis.getPosition()
      zPosition = self._io.zAxis.getPosition()
      codeLineSplit = line.split()
      for cmd in codeLineSplit :
        if "X" in cmd and re.match(xy+'|'+gxy+'|'+xyf+'|'+fxy+'|'+gxyf+'|'+gx_y+'|'+gx_yf, line) :
          xCmd = cmd.split("X")
          x = float(xCmd[1])
          if re.match( gxy+'|'+gxyf+'|'+gx_y+'|'+gx_yf, line):   # if G105 is used then add relative coordinate
            x = x + xPosition 
          if x < self._limitLeft or x > self._limitRight :
            error = "Invalid X-axis Coordinates, exceeding limit ["+str(self._limitLeft)+" , "+str(self._limitRight)+"]"
        if "Y" in cmd and re.match(xy+'|'+gxy+'|'+xyf+'|'+fxy+'|'+gxyf+'|'+gx_y+'|'+gx_yf, line) :
          yCmd = cmd.split("Y")
          y = float(yCmd[1])
          if re.match( gxy+'|'+gxyf+'|'+gx_y+'|'+gx_yf, line):
            y = y + yPosition
          if y < self._limitBottom or y > self._limitTop :
            error = "Invalid Y-axis Coordinates, exceeding limit ["+str(self._limitBottom)+" , "+str(self._limitTop)+"]"
        if "Z" in cmd and re.match(z, line) :
          zCmd = cmd.split("Z")
          z = float(zCmd[1])
          #if z < self._zlimitFront or z > self._zlimitRear :
          if z > self._zlimitRear :  
            error = "Invalid Z-axis Coordinates, exceeding limit ["+str(z)+" > "+str(self._zlimitRear)+"]"            

      if error != None :
        self._log.add(
          self.__class__.__name__,
          "MANUAL_GCODE",
          "Failed to execute manual G-Code line. Coordinates exceeding limit.",
          [ line ]
        )
      else :
        #Excute G_CodeLine
        errorData = self.gCodeHandler.executeG_CodeLine( line )

        if errorData :
          error = errorData[ "message" ]
          self._log.add(
            self.__class__.__name__,
            "MANUAL_GCODE",
            "Failed to execute manual G-Code line.",
            [ line, error ]
          )
        else:
          self.controlStateMachine.manualRequest = True
          self.controlStateMachine.executeGCode = True

          self._log.add(
            self.__class__.__name__,
            "MANUAL_GCODE",
            "Execute manual G-Code line.",
            [ line ]
          )

    return error

  #---------------------------------------------------------------------
  def setCameraImageURL( self, url ) :
    """
    Set the URL for the camera image.  Override function for simulator.
    """
    self._cameraURL = url

  #---------------------------------------------------------------------
  def getCameraImageURL( self ) :
    """
    Get the URL for the camera image.
    """
    return self._cameraURL

  #---------------------------------------------------------------------
  def startCalibrate(
    self,
    side,
    startPin,
    endPin,
    maxPins,
    deltaX,
    deltaY,
    velocity=None,
    acceleration=None,
    deceleration=None
  ) :
    """
    Begin the calibration sequence.

    Args:
      side: Front/back (F/B).
      startPin: First pin in scan.
      endPin: Last pin in scan.
      maxPin: The number of pin before wrap occurs.
      deltaX: Nominal change in X for next pin.  (Can be 0 for Y traverse.)
      deltaY: Nominal change in Y for next pin.  (Can be 0 for X traverse.)
      velocity: Maximum velocity.  None for last velocity used.
      acceleration: Maximum positive acceleration.  None for default.
      deceleration: Maximum negative acceleration.  None for default.
    """

    if not self.controlStateMachine.isMovementReady() :
      self._log.add(
        self.__class__.__name__,
        "CALIBRATION_ERROR",
        "Calibration scan error--machine not idle.",
        [ startPin, endPin, deltaX, deltaY, velocity, acceleration, deceleration ]
      )
      isError = True
    else :

      # Determine direction of travel.
      pinDelta = endPin - startPin
      if pinDelta < 0 :
        direction = -1
      else :
        direction = 1

      # Get the scan parameters setup.
      self.cameraCalibration.setupCalibration( side, startPin, direction, maxPins )
      self._io.camera.startScan( deltaX, deltaY )

      # Setup seek location.
      # The seek distance is the distance for the number of pins expected, plus
      # 1/2 to be sure the last pin is found.
      pinCount = abs( pinDelta )
      xPosition = self._io.xAxis.getPosition() + deltaX * ( pinCount + 0.5 )
      yPosition = self._io.yAxis.getPosition() + deltaY * ( pinCount + 0.5 )

      # Begin the seek by switching into calibration mode.
      self.controlStateMachine.seekX = xPosition
      self.controlStateMachine.seekY = yPosition
      self.controlStateMachine.seekVelocity = velocity
      self.controlStateMachine.seekAcceleration = acceleration
      self.controlStateMachine.seekDeceleration = deceleration
      self.controlStateMachine.calibrationRequest = True

      self._log.add(
        self.__class__.__name__,
        "CALIBRATION",
        "Calibration scan from pin " + str( startPin ) + " to " + str( endPin )
          + ".  X/Y to (" + str( xPosition )
          + ", " + str( yPosition ) + ") at " + str( velocity ) + ", "
          + str( acceleration ) + ", " + str( deceleration ) + " m/s^2.",
        [ startPin, endPin, xPosition, yPosition, velocity, acceleration, deceleration ]
      )

      isError = False

    return isError

  #---------------------------------------------------------------------
  def getAPA_Side( self ) :
    """
    Get the front-facing side of the APA.

    Returns:
      0 for front side of APA facing front side of machine.
      1 for back side of APA facing front side of machine.
      None for either no loaded APA, or APA in an invalid state for such a query.
    """
    result = None
    if None != self.apa :
      stage = self.apa.getStage()
      result = self.apa.STAGE_SIDE[ stage ]

    return result

  #---------------------------------------------------------------------
  def getLayerPinGeometry( self ) :
    """
    Get the pin geometry for current layer.

    Returns:
      A array of two sides.  Each side is a dictionary of of what pin number is
      on each edge corner.  There are eight edge corners (4 edges, 2 sides to
      each edge).  Returns None if no APA is loaded.
    """
    result = None
    if None != self.apa :
      stage = self.apa.getStage()
      side = self.apa.STAGE_SIDE[ stage ]
      layer = self.apa.getLayer()
      geometry = GeometrySelection( layer )

      pinFront = geometry.startPinFront
      pinBack  = geometry.startPinBack

      # Edges starting on bottom right and moving counter-clockwise.
      edges = [ "RB", "RT", "TR", "TL", "LT", "LB", "BL", "BR" ]

      front = {}
      back  = {}
      frontSumX = 0
      frontSumY = 0
      backSumX = 0
      backSumY = 0
      for edgeIndex in xrange( 0, 4 ) :

        frontCount  = geometry.gridFront[ edgeIndex ][ 0 ]
        frontDeltaX = geometry.gridFront[ edgeIndex ][ 1 ]
        frontDeltaY = geometry.gridFront[ edgeIndex ][ 2 ]
        backCount   = geometry.gridBack[ edgeIndex ][ 0 ]
        backDeltaX  = geometry.gridBack[ edgeIndex ][ 1 ]
        backDeltaY  = geometry.gridBack[ edgeIndex ][ 2 ]

        frontSumX += geometry.gridFront[ edgeIndex ][ 3 ]
        frontSumY += geometry.gridFront[ edgeIndex ][ 4 ]
        backSumX += geometry.gridBack[ edgeIndex ][ 3 ]
        backSumY += geometry.gridBack[ edgeIndex ][ 4 ]

        # Offset between front/back side pins.
        # This is either an offset in X or Y, and really just for the U-layer.
        offsetX = backSumX - frontSumX
        offsetY = backSumY - frontSumY

        # Forward.
        edge = edges[ edgeIndex * 2 + 0 ]
        front[ edge ] = [ pinFront, frontDeltaX, frontDeltaY, offsetX, offsetY ]
        back[ edge ]  = [ pinBack, backDeltaX, backDeltaY, -offsetX, -offsetY ]

        frontCount -= 1
        frontCount *= geometry.directionFront
        backCount -= 1
        backCount *= geometry.directionBack

        pinFront = LayerFunctions.offsetPin( geometry, pinFront, frontCount )
        pinBack  = LayerFunctions.offsetPin( geometry, pinBack,  backCount )

        # Reverse.
        edge = edges[ edgeIndex * 2 + 1 ]
        front[ edge ] = [ pinFront, -frontDeltaX, -frontDeltaY, offsetX, offsetY ]
        back[ edge ]  = [ pinBack, -backDeltaX, -backDeltaY, -offsetX, -offsetY ]

        pinFront = LayerFunctions.offsetPin( geometry, pinFront, geometry.directionFront )
        pinBack  = LayerFunctions.offsetPin( geometry, pinBack,  geometry.directionBack )

      result = [ front, back, geometry.pins ]

    return result

  #---------------------------------------------------------------------
  def commitCalibration( self, side, offsetX, offsetY ) :
    """
    Commit the scan data to the calibration file.

    Args:
      side: Front facing side of APA (0=front, 1=back).
      offsetX: Offset in X from current side to other side.
      offsetY: Offset in Y from current side to other side.

    Returns:
      True if there was an error, False if not.
    """
    isError = True
    if None != self.apa :
      isError = False
      layer = self.apa.getLayer()
      geometry = GeometrySelection( layer )
      calibration = self.gCodeHandler.getLayerCalibration()
      calibrationFileName = calibration.getFileName()
      cameraDataPath = self.apa.getPath() + "Scans"

      # Create directory if it doesn't exist.
      if not os.path.exists( cameraDataPath ) :
        os.makedirs( cameraDataPath )

      cameraDataFile = str( self._systemTime.get() )
      cameraDataFile = cameraDataFile.replace( " ", "_" ).replace( ":", "_" ).replace( ".", "_" )
      cameraDataFile += ".csv"

      if self.apa.Side.FRONT == side :
        isFrontSide = True
      else :
        isFrontSide = False

      self.cameraCalibration.commitCalibration(
        calibration,
        geometry,
        isFrontSide,
        offsetX,
        offsetY
      )

      cameraDataHash = self.cameraCalibration.save( cameraDataPath, cameraDataFile )
      calibration.save()

      self._log.add(
        self.__class__.__name__,
        "CALIBRATION_SAVED",
        "Updated calibration information from scan for layer " + layer + " to " \
          + calibrationFileName + ".",
        [ layer, calibrationFileName, calibration.hashValue, cameraDataFile, cameraDataHash ]
      )

    return isError

  #---------------------------------------------------------------------
  def cameraSeekCenter( self, velocity=None ) :
    """
    Seek to the center of the pin currently in view.
    Only useful if camera has a pin location to work with.

    Args:
      velocity: Seek velocity.

    Returns:
      True if there was an error, False if not.
    """
    isError = False
    [ x, y ] = self.cameraCalibration.centerCurrentLocation()
    if None != x and None != y :

      self.manualSeekXY( x, y, velocity )

      self._log.add(
        self.__class__.__name__,
        "PIN_CENTER",
        "Seeking pin center: " + str( x ) + " " + str( y ) + ".",
        [ x, y ]
      )
    else :
      isError = True
      self._log.add(
        self.__class__.__name__,
        "PIN_CENTER",
        "Failed to find a pin center to seek."
      )

    return isError

# end class
