###############################################################################
# Name: HeadPosition.py
# Uses: Handling the passing around of the head via Z-axis.
# Date: 2016-04-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from G_CodeFunctions.HeadLocationG_Code import HeadLocationG_Code

class HeadPosition :

  FRONT = 0
  PARTIAL_FRONT = 1
  PARTIAL_BACK  = 2
  BACK = 3

  PARTIAL = 4
  OTHER_SIDE = 5

  #---------------------------------------------------------------------
  def __init__( self, gCodePath, geometry, initialPosition ) :
    """
    Constructor.

    Args:
      gCodePath: An instance of G_CodePath.
      geometry: An instance of LayerGeometry (or child of).
      initialPosition: Initial position of Z axis.
    """
    self._gCodePath = gCodePath
    self._geometry = geometry
    self._currentPostion = initialPosition

  #---------------------------------------------------------------------
  def get( self ) :
    """
    Get the current position of the head.

    Returns:
      Current position of head (FRONT/PARTIAL_FRONT/PARTIAL_BACK/BACK).
    """
    return self._currentPostion

  #---------------------------------------------------------------------
  def set( self, location ) :
    """
    Set new location of head.

    Args:
      location: Where to place the head (FRONT/PARTIAL_FRONT/PARTIAL_BACK/BACK).
    """

    # Partial for the current side.
    if HeadPosition.PARTIAL == location :
      if HeadPosition.BACK == self._currentPostion :
        location = HeadPosition.PARTIAL_BACK
      elif HeadPosition.FRONT == self._currentPostion :
        location = HeadPosition.PARTIAL_FRONT
      else :
        print location, self._currentPostion
        raise Exception()

    # Switch to other side.
    if HeadPosition.OTHER_SIDE == location :
      if HeadPosition.BACK == self._currentPostion or HeadPosition.PARTIAL_BACK == self._currentPostion :
        location = HeadPosition.FRONT
      elif HeadPosition.FRONT == self._currentPostion or HeadPosition.PARTIAL_FRONT == self._currentPostion :
        location = HeadPosition.BACK

    if self._currentPostion != location :

      # $$$DEBUG - Evaluate and clean-up.
      # # Latch needed?
      # if HeadPosition.BACK == self._currentPostion or HeadPosition.BACK == location :
      #   # Latch to front or back?
      #   if self._currentPostion == HeadPosition.BACK :
      #     self._gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      #   else :
      #     self._gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      #
      #   # Get/set it from/to back.
      #   #self._gCodePath.push( z=self._geometry.backZ )

      # # Front and back are both in front.  This is because is the destination
      # # is the back, we leave the head at the back and return to the front.
      # if HeadPosition.BACK == location or HeadPosition.FRONT == location :
      #   self._gCodePath.push( z=self._geometry.frontZ )
      # elif HeadPosition.PARTIAL_FRONT == location :
      #   self._gCodePath.push( z=self._geometry.partialZ_Front )
      # elif HeadPosition.PARTIAL_BACK == location :
      #   self._gCodePath.push( z=self._geometry.partialZ_Back )
      # #self._gCodePath.push()

      self._gCodePath.pushG_Code( HeadLocationG_Code( location ) )
      self._gCodePath.push()

      self._currentPostion = location
