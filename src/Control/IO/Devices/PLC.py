###############################################################################
# Name: PLC.py
# Uses: Abstract PLC class.
# Date: 2016-02-26
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-26 - QUE - Creation.
###############################################################################

from IO_Device import IO_Device
from abc import ABCMeta, abstractmethod

class PLC( IO_Device ) :

  # Make class abstract.
  __metaclass__ = ABCMeta

  #============================================================================
  class Tag :
    """
    PLC Tag.  System PLC's use to represent data.
    Notes:
      Use the Attributes subclass to define how the tag behaves.
    """
    list = []

    # Various attributes an I/O word can have.
    class Attributes :
      canRead      = True   # False for write-only.
      canWrite     = True   # False for read-only.
      isPolled     = False  # True if this tag should be polled regularly.
      defaultValue = None   # Default state if tag is unreadable.
    # end class

    #---------------------------------------------------------------------
    def __init__( self, name, plc, tagName, attributes = Attributes(), tagType="DINT" ) :
      """
      Constructor.

      Args:
        name: Name of output.
        plc: Instance of IO_Device.PLC.
        tagName: Which PLC tag this input is assigned.
        tagType: The type of tag value.
        attributes: Attributes of tag (must be instance of Attributes)
      """
      PLC.Tag.list.append( self )
      self._plc        = plc
      self._tagName    = tagName
      self._attributes = attributes
      self._type       = tagType
      self._value      = attributes.defaultValue

    #---------------------------------------------------------------------
    def poll( self ) :
      """
      Update the input by reading the value form PLC.  Call periodically.
      """
      value = self._plc.read( self._tagName )
      if not value == None and not self._plc.isNotFunctional() :
        self.updateFromReadTag( value )
      else :
        self._value = self._attributes.defaultValue

    #---------------------------------------------------------------------
    @staticmethod
    def pollAll() :
      """
      Update all tags.

      Future:
        All tags could be read at once, which may be useful in reducing
        Ethernet traffic.
      """
      for tag in PLC.Tag.list :
        if tag._attributes.isPolled :
          tag.poll()

    #---------------------------------------------------------------------
    def getReadTag( self ) :
      """
      Get read tag.  Used when reading multiple tags at once.

      Returns:
        Name of tag for reading.  None if this is a write-only tag.
      """
      result = None
      if self._attributes.canRead :
        result = self._tagName

      return result

    #---------------------------------------------------------------------
    def updateFromReadTag( self, value ) :
      """
      Update internal state from tag data.  Used when multiple reads have
      been done at once to feed back data.
      """
      if self._attributes.canRead :
        self._value = value[ 0 ]


    #---------------------------------------------------------------------
    def get( self ) :
      """
      Fetch last read value of tag.

      Returns:
        Last read value of tag.

      Note:
        Does not reflect any useful value until polled.  If the PLC isn't
        functional, this value returns a default value.
      """
      return self._value

    #---------------------------------------------------------------------
    def set( self, value ) :
      """
      Set the value.

      Args:
        value: New data to be written.

      Returns:
          True if there was an error, False if not.
      """
      isError = False

      result = self._plc.write( self._tagName, value, self._type )
      if None == result :
        isError = True
      else :
        self._value = value

      return isError
  # end class
  #============================================================================

  #---------------------------------------------------------------------
  @abstractmethod
  def initialize( self ) :
    """
    Try and establish a connection to the PLC.

    Returns:
      True if there was an error, False if connection was made.
    """
    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def isNotFunctional( self ) :
    """
    See if the PLC is communicating correctly.

    Returns:
      True there is a problem with hardware, false if not.
    """
    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def read( self, tag ) :
    """
    Read a tag(s) from the PLC.

    Args:
      tag: A single or a list of PLC tags.

    Returns:
      Result of the data read, or None if there was a problem.
    """
    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def write( self, tag, data=None, typeName=None ) :
    """
    Write a tag(s) to the PLC.

    Args:
      tag: A single or a list of PLC tags.
      data: Data to be written.
      typeName: Type of the tag to write.

    Returns:
        None is returned in case of error otherwise the tag list is returned.
    """
    pass

# end class
