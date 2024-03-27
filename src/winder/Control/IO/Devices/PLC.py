###############################################################################
# Name: PLC.py
# Uses: Abstract PLC class.
# Date: 2016-02-26
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from .IO_Device import IO_Device
from abc import ABCMeta, abstractmethod
import six
from six.moves import range

class PLC( six.with_metaclass(ABCMeta, IO_Device) ) :

  # There is a limit to the length of packets to/from the PLC.  When reading
  # tags the request must be limited.  I have found no documentation as to how
  # to calculate this limit, but found I could read 18 with the tag name sizes
  # currently in the queue.  So 14 seems a safe number.
  MAX_TAG_READS = 14

  #============================================================================
  class Tag :
    """
    PLC Tag.  System PLC's use to represent data.
    Notes:
      Use the Attributes subclass to define how the tag behaves.
    """

    # List of all tags.
    list = []

    # Look-up table to match tag names to instances of Tag.  The look-up is
    # a list of tag instances in case there are multiple Tag instances for the
    # same tag name.
    map = {}

    # Various attributes an I/O word can have.
    class Attributes :
      canRead      = True   # False for write-only.
      canWrite     = True   # False for read-only.
      isPolled     = False  # True if this tag should be polled regularly.
      defaultValue = None   # Default state if tag is unreadable.
    # end class

    #---------------------------------------------------------------------
    def __init__( self, plc, tagName, attributes = Attributes(), tagType="DINT" ) :
      """
      Constructor.

      Args:
        plc: Instance of IO_Device.PLC.
        tagName: Which PLC tag this input is assigned.
        tagType: The type of tag value.
        attributes: Attributes of tag (must be instance of Attributes)
      """

      # Cannot create a tag that cannot be read but is polled.
      assert( attributes.canRead or not attributes.isPolled )

      PLC.Tag.list.append( self )

      # Add this tag to the look-up table.
      if tagName in PLC.Tag.map :
        PLC.Tag.map[ tagName ].append( self )
      else:
        PLC.Tag.map[ tagName ] = [ self ]

      self._plc        = plc
      self._tagName    = tagName
      self._attributes = attributes
      self._type       = tagType
      self._value      = attributes.defaultValue

    #---------------------------------------------------------------------
    def getName( self ) :
      """
      Return name of this tag.

      Args:
        name: Name of this tag.
      """
      return self._tagName

    #---------------------------------------------------------------------
    def poll( self ):
      """
      Update the input by reading the value form PLC.  Call periodically.
      """
      value = self._plc.read( self._tagName )
      if value is not None and not self._plc.isNotFunctional():
        self.updateFromReadTag( value[ 0 ] )
      else:
        self._value = self._attributes.defaultValue

    #---------------------------------------------------------------------
    @staticmethod
    def pollAll( plc ):
      """
      Update all tags.

      Future:
        All tags could be read at once, which may be useful in reducing
        Ethernet traffic.
      """

      tags_to_read = []
      for tag in PLC.Tag.list:
        # If this tag is polled...
        if tag._attributes.isPolled:
          tagName = tag.getReadTag()

          # If this tag is not already in the list...
          if tagName not in tags_to_read:
            tags_to_read.append( tagName )
      
      results = {}
      for tag_name in tags_to_read:
          try:
              tag_value = plc.read(tag_name)
              results[tag_name] = tag_value
          except Exception as e:
              print(f"Error reading tag {tag_name}: {e}")
              results[tag_name] = None

      if results is None:
        for tagName in tags_to_read :
          for tag in PLC.Tag.map[ tagName ] :
            tag._value = tag._attributes.defaultValue

      else:
        # Distribute the results to the tag objects.
        for tag_name in results :
          # For each object that uses this tag name...
          for tag in PLC.Tag.map[tag_name] :
            # Send it the result.
            tag.updateFromReadTag( results[tag_name] )


    #---------------------------------------------------------------------
    def getReadTag( self ):
      """
      Get read tag.  Used when reading multiple tags at once.

      Returns:
        Name of tag for reading.  None if this is a write-only tag.
      """
      return self._tagName if self._attributes.canRead else None

    #---------------------------------------------------------------------
    def updateFromReadTag( self, value ) :
      """
      Update internal state from tag data.  Used when multiple reads have
      been done at once to feed back data.
      """
      if self._attributes.canRead :
        self._value = value


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
    def set( self, value ):
      """
      Set the value.

      Args:
        value: New data to be written.

      Returns:
          True if there was an error, False if not.
      """
      isError = False

      result = self._plc.write( self._tagName, value, self._type )
      if result is None:
        isError = True
      else:
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
