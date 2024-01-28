###############################################################################
# Name: SimulatedPLC.py
# Uses: Simulated PLC.
# Date: 2016-02-26
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   The simulated PLC allows a list of PLC tags to be setup, and then just
#   accepts and returns whatever was last written to the tag.
###############################################################################

from PLC import PLC

class SimulatedPLC( PLC ) :

  tags = {}
  writeCallbacks = {}
  readCallbacks = {}

  #---------------------------------------------------------------------
  def initialize( self ) :
    """
    Try and establish a connection to the PLC.

    Returns:
      True if there was an error, False if connection was made.
    """
    return False

  #---------------------------------------------------------------------
  def isNotFunctional( self ) :
    """
    See if the PLC is communicating correctly.

    Returns:
      True there is a problem with hardware, false if not.
    """
    return False

  #---------------------------------------------------------------------
  def _fetch( self, tag ) :
    """
    Fetch data from tag.
    Only for individual tags as opposed to lists.

    Args:
      tag: A single PLC tag.

    Returns:
      Result of the data read, or None if there was a problem.
    """
    result = None
    if tag in SimulatedPLC.tags.keys() :
      result = SimulatedPLC.tags[ tag ]

      if tag in SimulatedPLC.readCallbacks :
        result = SimulatedPLC.readCallbacks[ tag ]( tag, result )

    return result

  #---------------------------------------------------------------------
  def read( self, tag ) :
    """
    Read a tag(s) from the PLC.

    Args:
      tag: A single or a list of PLC tags.

    Returns:
      Result of the data read, or None if there was a problem.
    """
    result = []

    if not isinstance( tag, list ) :
      value = self._fetch( tag )
      result.append( value )
    else:
      tags = tag
      for tag in tags :
        value = self._fetch( tag )
        result.append( [ tag, value, "" ] )

    return result

  #---------------------------------------------------------------------
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
    if tag in SimulatedPLC.tags.keys() :
      if tag in SimulatedPLC.writeCallbacks :
        data = SimulatedPLC.writeCallbacks[ tag ]( tag, data )

      SimulatedPLC.tags[ tag ] = data

    return []

  #---------------------------------------------------------------------
  def getTag( self, tag ) :
    """
    Return tag data.  Simulator function.

    Args:
      tag: Which tag.

    Returns:
      Data in tag.  This is not an array like 'read' will return.
    """
    result = self.read( tag )
    if result :
      result = result[ 0 ]

    return result

  #---------------------------------------------------------------------
  def setupTag( self, tag, data=None, writeCallback=None, readCallback=None ) :
    """
    Setup a tag.

    Args:
      tag: Name of tag to add.
      data: Initial data in tag.
    """
    SimulatedPLC.tags[ tag ] = data

    if writeCallback :
      SimulatedPLC.writeCallbacks[ tag ] = writeCallback

    if readCallback :
      SimulatedPLC.readCallbacks[ tag ] = readCallback

    return tag

# end class
