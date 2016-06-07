###############################################################################
# Name: Motion.py
# Uses: Compute position over time given properties of motion abstract class.
# Date: 2016-02-05
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from abc import ABCMeta, abstractmethod

class Motion :

  # Make class abstract.
  __metaclass__ = ABCMeta

  #---------------------------------------------------------------------
  @abstractmethod
  def isMoving( self, time ):
    """
    See if there is motion for the given time.

    Args:
      time: Time for which to check.

    Returns:
      True if in motion at this time, False if not.
    """


  #---------------------------------------------------------------------
  @abstractmethod
  def interpolatePosition( self, time ) :
    """
    Compute a position based on time.

    Args:
      time: Time for which to get position.

    Returns:
      Position at this time.
    """

  #---------------------------------------------------------------------
  @abstractmethod
  def interpolateVelocity( self, time ) :
    """
    Compute a velocity based on time.

    Args:
      time: Time for which to get velocity.

    Returns:
      Velocity at this time.
    """

  #---------------------------------------------------------------------
  @abstractmethod
  def interpolateAcceleration( self, time ) :
    """
    Compute an acceleration based on time.

    Args:
      time: Time for which to get acceleration.

    Returns:
      Acceleration at this time.
    """


  #---------------------------------------------------------------------
  @abstractmethod
  def hardStop( self, time ) :
    """
    Compute position from an instant stop at current time.

    Args:
      time - Current time.
    """

# end class

