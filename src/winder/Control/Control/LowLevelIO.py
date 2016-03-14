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
    """
    Get a list of each I/O point name and the current value.

    Args:
      ioList: List of I/O instances to fetch.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    result = []
    for ioPoint in ioList :
      result.append( [ ioPoint.getName(), ioPoint.get() ] )

    return result

  #---------------------------------------------------------------------
  @staticmethod
  def getInputs() :
    """
    Get a list of digital input in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( DigitalInput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getInput( name ) :
    """
    Retrieve the current state of a specific digital input by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return DigitalInput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getOutputs() :
    """
    Get a list of every digital output in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( DigitalOutput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getOutput( name ) :
    """
    Retrieve the current state of a specific digital output by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return DigitalOutput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getTags() :
    """
    Get a list of every PLC tag in system.

    Returns:
      A list of two lists.  The first element of sub-list is the tag name and
      the second element is the tag value.
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
    """
    Retrieve the current state of a specific PLC tag by name.

    Args:
      name: Name of PLC tag.

    Returns:
      Current value of tag.
    """
    return PLC.Tag.map[ name ][ 0 ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAllDigitalIO() :
    """
    Get a list of all digital I/O points in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( DigitalIO.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getDigitalIO( name ) :
    """
    Retrieve the current state of a specific digital I/O by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return DigitalIO.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAllIO() :
    """
    Get a list of every I/O point in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( IO_Point.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getIO( name ) :
    """
    Retrieve the current state of a specific I/O point by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return IO_Point.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getMotors() :
    """
    Get a list of every motor in system.

    Returns:
      A list of two lists.  The first element of sub-list is the motor name and
      the second element is a representation of the motor state.
    """
    return LowLevelIO._getIO_List( Motor.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getMotor( name ) :
    """
    Retrieve the current state of a specific motor by name.

    Args:
      name: Name of motor.

    Returns:
      String representation current of motor state.
    """
    return Motor.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogInputs() :
    """
    Get a list of every analog input in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( AnalogInput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogInput( name ) :
    """
    Retrieve the current state of a specific analog input by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return AnalogInput.map[ name ].get()

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogOutputs() :
    """
    Get a list of every analog output in system.

    Returns:
      A list of two lists.  The first element of sub-list is the I/O name and
      the second element is the I/O value.
    """
    return LowLevelIO._getIO_List( AnalogOutput.list )

  #---------------------------------------------------------------------
  @staticmethod
  def getAnalogOutput( name ) :
    """
    Retrieve the current state of a specific analog output by name.

    Args:
      name: Name of I/O point.

    Returns:
      Current value of requested I/O point.
    """
    return AnalogOutput.map[ name ].get()
