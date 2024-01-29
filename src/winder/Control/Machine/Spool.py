###############################################################################
# Name: Spool.py
# Uses: Wire spool.
# Date: 2016-03-08
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


class Spool :
  #---------------------------------------------------------------------
  def __init__( self, initialWire=0, lowWireQuantity=0 ) :
    """
    Constructor.

    Args:
      initialWire: Amount of wire the spool has (in meters).
      lowWireQuantity: Minimal amount of wire (in meters) before considered low.
    """
    self._wire = initialWire
    self._low = lowWireQuantity

  #---------------------------------------------------------------------
  def subtract( self, length ):
    """
    Subtract off a length of wire from spool.

    Args:
      length: Amount to subtract (in meters).
    """
    if self._wire != -1:
      self._wire -= length

  #---------------------------------------------------------------------
  def isLow( self ):
    """
    Check to see if spool is low.

    Returns:
      True if low on wire, False if not.
    """
    return self._wire < self._low and self._wire != -1

  #---------------------------------------------------------------------
  def getWire( self ) :
    """
    Get the amount of wire on the spool.

    Returns:
      Amount of wire (in meters) on the spool.
    """
    return self._wire

  #---------------------------------------------------------------------
  def setWire( self, amount ) :
    """
    Set how much wire spool contains.

    Args:
      amount: Amount of wire (in meters) the spool has.  -1 to disable.
    """
    self._wire = amount

# end class
