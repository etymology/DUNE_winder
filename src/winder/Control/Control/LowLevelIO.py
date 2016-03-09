###############################################################################
# Name: LowLevelIO.py
# Uses: Low-level I/O functions for use by GUI.
# Date: 2016-03-09
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   Designed to provide access to all the low-level primitive I/O lists.
###############################################################################

from IO.Primitives.IO_Point import IO_Point
from IO.Primitives.DigitalIO import DigitalIO
from IO.Primitives.DigitalInput import DigitalInput
from IO.Primitives.DigitalOutput import DigitalOutput
from IO.Primitives.Motor import Motor
from IO.Primitives.AnalogInput import AnalogInput
from IO.Primitives.AnalogOutput import AnalogOutput
from IO.Devices.PLC import PLC

class LowLevelIO :
  #---------------------------------------------------------------------
  @staticmethod
  def _getIO_List( ioList ) :
    result = []
    for ioPoint in ioList :
      result.append( [ ioPoint.getName(), ioPoint.get() ] )

    return result

  #---------------------------------------------------------------------
  @staticmethod
  def getInputs() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( DigitalInput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getInput( name ) :
    return DigitalInput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getOutputs() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( DigitalOutput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getOutput( name ) :
    return DigitalOutput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getTags() :
    """
    $$$DEBUG
    """
    tags = []
    result = []
    for tag in PLC.Tag.list :
      name = tag.getName()
      if not name in tags :
        tags.append( name )
        result.append( [ name, tag.get() ] )

    return result

  #---------------------------------------------------------------------
  @staticmethod
  def getTag( name ) :
    return PLC.Tag.map[ name ][ 0 ].get()


  #---------------------------------------------------------------------
  @staticmethod
  def getAllDigitalIO() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( DigitalIO.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getDigitalIO( name ) :
    return DigitalIO.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAllIO() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( IO_Point.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getIO( name ) :
    return IO_Point.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getMotors() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( Motor.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getMotor( name ) :
    return Motor.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogInputs() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( AnalogInput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogInput( name ) :
    return AnalogInput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogOutputs() :
    """
    $$$DEBUG
    """
    return LowLevelIO._getIO_List( AnalogOutput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogOutput( name ) :
    return AnalogOutput.map[ name ].get()
