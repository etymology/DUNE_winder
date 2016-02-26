###############################################################################
# Name: SimulatedPLC.py
# Uses: Simulated PLC.
# Date: 2016-02-26
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-26 - QUE - Creation.
# Notes:
#   The simulated PLC allows a list of PLC tags to be setup, and then just
#   accepts and returns whatever was last written to the tag.
###############################################################################

from PLC import PLC

class SimulatedPLC( PLC ) :

  tags = {}

  #---------------------------------------------------------------------
  def isNotFunctional( self ) :
    """
    See if the PLC is communicating correctly.

    Returns:
      True there is a problem with hardware, false if not.
    """
    pass

  #---------------------------------------------------------------------
  def read( self, tag ) :
    """
    Read a tag(s) from the PLC.

    Args:
      tag: A single or a list of PLC tags.

    Returns:
      Result of the data read, or None if there was a problem.
    """
    result = None
    if tag in tags.keys() :
      result = tags[ tag ]

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
    if tag in tags.keys() :
      tags[ tag ] = data

  #---------------------------------------------------------------------
  def setupTag( self, tag, data=None ) :
    """
    Setup a tag
    """
    tags[ tag ] = data

# end class
