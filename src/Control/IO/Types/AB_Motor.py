#==============================================================================
# Name: AB_Motor.py
# Uses: Allen-Bradley motor.
# Date: 2016-02-07
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-07 - QUE - Creation.
#==============================================================================

from IO.Primitives.Motor import Motor
from IO.Types.AB_Tag import AB_Tag

class AB_Motor( Motor ) :

  list = []

  #---------------------------------------------------------------------
  def __init__( self, name, plc, tagBase ) :
    """
    Constructor.

    Args:
      name: Name of motor.
      plc: Instance of AB_PLC.
      tagBase: All tags will start with this prepended to the name.
    """

    Motor.__init__( self, name )
    AB_Motor.list.append( self )
    self._seekFlag = False
    self._plc = plc
    self._tagBase = tagBase

    self._setPosition = \
      AB_Tag(
        name + "_setPosition",
        plc,
        tagBase + "_POSITION",
        tagType="REAL"
      )

    self._maxVelocity = \
      AB_Tag(
        name + "_maxVelocity",
        plc,
        tagBase + "_DATA.CommandVelocity",
        tagType="REAL"
      )

    self._jogSpeed = \
      AB_Tag(
        name + "_jogSpeed",
        plc,
        tagBase + "_SPEED",
        tagType="REAL"
      )

    self._jogDirection = \
      AB_Tag(
        name + "_jogDirection",
        plc,
        tagBase + "_DIR",
        tagType="DINT"
      )

    # Read-only attributes.
    attributes = AB_Tag.Attributes()
    attributes.canWrite = False
    self._position = \
      AB_Tag(
        name + "_position",
        plc,
        tagBase + "_DATA.ActualPosition",
        attributes
      )

    self._velocity = \
      AB_Tag(
        name + "_velocity",
        plc,
        tagBase + "_DATA.ActualVelocity",
        attributes
      )

    self._acceleration = \
      AB_Tag(
        name + "_acceleration",
        plc,
        tagBase + "_DATA.ActualAcceleration",
        attributes
      )

    self._movement = \
      AB_Tag(
        name + "_movement",
        plc,
        tagBase + "_DATA.CoordinatedMotionStatus",
        attributes,
        "BOOL"
      )

    attributes.defaultValue = True
    self._faulted = \
      AB_Tag(
        name + "_fault",
        plc,
        tagBase + "_DATA.ModuleFault",
        tagType="BOOL"
      )


    #self._maxAcceleration = 200
    #self._maxVelocity     = 400

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop the motor.

    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def isFunctional( self ) :
    """
    Check to see if motor is ready to run.

    Returns:
      True if functional, False if not.
    """

    #print self._name, self._faulted.get()

    return not bool( self._faulted.get() )

  #---------------------------------------------------------------------
  def setEnable( self, isEnabled ) :
    """
    Enable/disable motor.

    Args:
      isEnabled: True if enabled, False if not.

    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def setDesiredPosition( self, position ) :
    """
    Go to a location.

    Args:
      positions: Position to seek (in motor units).
    """
    #$$$DEBUG print "Set position", position
    self._setPosition.set( position )
    #self._seekFlag = True

  #---------------------------------------------------------------------
  def getDesiredPosition( self ) :
    """
    Return the desired (seeking) position.

    Returns:
      Desired motor position.
    """
    return self._setPosition.get()

  #---------------------------------------------------------------------
  def isSeeking( self ) :
    """
    See if the motor is in motion.

    Returns:
      True if seeking desired position, False if at desired position.
    """

    result = bool( self._movement.get() )
    #if self._seekFlag and result :
    #  self._seekFlag = False

    #result |= self._seekFlag
    return result

  #---------------------------------------------------------------------
  def seekWait( self ) :
    """
    Block until seek is obtained.

    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def getPosition( self ) :
    """
    Return current motor position.

    Returns:
      Motor position (in motor units).
    """

    return self._position.get()

  #---------------------------------------------------------------------
  def setMaxVelocity( self, maxVelocity ) :
    """
    Set maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """
    self._jogSpeed.set( maxVelocity )

  #---------------------------------------------------------------------
  def getMaxVelocity( self ) :
    """
    Get maximum velocity motor may move.

    Args:
      maxVelocity: Maximum velocity.

    """

    return self._maxVelocity.get()

  #---------------------------------------------------------------------
  def getVelocity( self ) :
    """
    Get current motor velocity.

    Returns:
      Current motor velocity (in motor units/second).
    """

    return self._velocity.get()

  #---------------------------------------------------------------------
  def setVelocity( self, velocity ) :
    """
    Set motor velocity.  Useful for jogging motor.  Set to 0 to stop.

    Args:
      velocity: Desired velocity.  Negative velocity is reverse direction.
    """

    direction = 0
    if velocity < 0 :
      direction = 1
      velocity = -velocity

    self._jogSpeed.set( velocity )
    self._jogDirection.set( direction )

  #---------------------------------------------------------------------
  def setMaxAcceleration( self, maxAcceleration ) :
    """
    Set maximum acceleration motor may move.

    Args:
      maxAcceleration: Maximum acceleration motor may move.

    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def getMaxAcceleration( self ) :
    """
    Get maximum acceleration motor may move.

    Returns:
      Maximum acceleration motor may move.
    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def getAcceleration( self ) :
    """
    Get current motor acceleration.

    Returns:
      Motor acceleration (in motor units/second squared).
    """

    return self._acceleration.get()

  #---------------------------------------------------------------------
  def setMaxTorque( self, maxTorque ) :
    """
    Set maximum torque motor may exert.

    Args:
      maxTorque: Maximum torque motor may exert.

    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def getMaxTorque( self ) :
    """
    Get maximum torque motor may exert.

    Returns:
      Maximum torque.
    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def getTorque( self ) :
    """
    Get the current torque on motor shaft.

    Returns:
      Torque on motor shaft (in motor torque units).
    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def setTorque( self, torque ) :
    """
    Set the amount of torque the motor reports.

    Returns:
      Torque the motor reports.
    """

    # $$$DEBUG
    pass

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    $$$DEBUG
    """
    self._faulted.poll()
    self._position.poll()
    self._velocity.poll()
    self._acceleration.poll()
    self._movement.poll()

    pass

  #---------------------------------------------------------------------
  @staticmethod
  def pollAll() :
    """
    $$$DEBUG
    """

    for instance in AB_Motor.list :
      instance.poll() # $$$DEBUG - Do single read.

# end class
