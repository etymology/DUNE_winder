###############################################################################
# Name: TrapezoidalMotion.py
# Uses: Trapezoidal motion using min/max acceleration, and max velocity limits.
# Date: 2016-06-06
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Motion import Motion
from math import sqrt, pow

class TrapezoidalMotion( Motion ) :
  #------------------------------------
  # Private data.
  #------------------------------------

  # Transition point.
  # There are 8 such points needed to compute travel location.
  class Point :
    T0 = 0
    T1 = 1
    T2 = 2
    T3 = 3
    POINTS = 4

    t = 0  # Time.
    a = 0  # Acceleration.
    v = 0  # Velocity.
    x = 0  # Position.
  # end class

  #---------------------------------------------------------------------
  def _calculateX( self, a, v, x, t ) :
    """
    Calculate ending x position given jerk, acceleration, velocity, initial position, and time.

    Args:
      a: Acceleration.
      v: Velocity.
      x: Initial position.
      t: Time from initial position.

    Returns:
      Position after time.
    """

    return x + v * t + 1.0 / 2.0 * a * t ** 2

  #---------------------------------------------------------------------
  def _calculateV( self, a, v, t ) :
    """
    Calculate ending velocity given jerk, acceleration, initial velocity, and time.

    Args:
      a: Acceleration.
      v: Initial velocity.
      t: Time from initial position.

    Returns:
      Velocity after time.
    """

    return v + a * t

  # #---------------------------------------------------------------------
  # def _calculateA( self, j, a, t ) :
  #   """
  #   Calculate ending acceleration given jerk, initial acceleration and time.
  #
  #   Args:
  #     j: Jerk.
  #     a: Initial acceleration.
  #     t: Time from initial position.
  #
  #   Returns:
  #     Acceleration after time.
  #   """
  #
  #   return a + j * t

  #---------------------------------------------------------------------
  def _nextPoint( self, thisPoint, lastPoint, a, t ) :
    """
    Calculate transition point.

    Args:
      thisPoint: Point (self.Point.*) to calculate.
      lastPoint: Previous point.
      a: Acceleration.
      t: Time.

    Returns:
      self._point[ thisPoint ] and self._point[ lastPoint ] are modified. Nothing is returned.
    """

    thisPoint = self._point[ thisPoint ]
    lastPoint = self._point[ lastPoint ]

    thisPoint.t = t + lastPoint.t
    thisPoint.a = 0
    lastPoint.a = a
    thisPoint.v = self._calculateV( lastPoint.a, lastPoint.v, t )
    thisPoint.x = self._calculateX( lastPoint.a, lastPoint.v, lastPoint.x, t )

  #------------------------------------
  # Public functions.
  #------------------------------------

  #---------------------------------------------------------------------
  def __init__(
    self,
    maxAcceleration = 0,
    minAcceleration = 0,
    velocity = 0,
    startPosition = 0,
    endPosition = 0
    ) :
    """
    Constructor with full parameter set.

    Args:
      acceleration: Maximum acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.

    """
    self._point = [ self.Point() for _ in range( self.Point.POINTS ) ]
    self.compute( maxAcceleration, minAcceleration, velocity, startPosition, endPosition )

    # for point in self._point :
    #   print point.t, point.a, point.v, point.x
    #
    # print
    # print


  #---------------------------------------------------------------------
  def compute( self, maxAcceleration, minAcceleration, velocity, startPosition, endPosition ) :
    """
    Compute internal point table using the specified settings. Call before using 'interpolatePosition'.

    Args:
      acceleration: Maximum acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.

    Returns:
      Modifies self._point. Nothing is returned.
    """

    # Jerk, acceleration and velocity are magnitudes, so force an absolute value.
    maxAcceleration = abs( maxAcceleration )
    minAcceleration = abs( minAcceleration )
    velocity        = abs( velocity        )

    if None == endPosition :
      endPosition = 0

    if None == startPosition :
      startPosition = 0

    position = endPosition - startPosition
    forwardAcceleration =  maxAcceleration
    reverseAcceleration = -minAcceleration
    svelocity   = velocity
    if position < 0 :
      position = -position
      forwardAcceleration = -forwardAcceleration
      reverseAcceleration = -reverseAcceleration
      svelocity   = -velocity

    # $$$DEBUG # We must either not be moving or have a jerk term.
    # $$$DEBUG assert ( 0 == position or not 0 == jerk ), "Cannot move without a jerk term"
    # $$$DEBUG assert ( 0 == position or 0 != velocity ), "Cannot move without a velocity term"

    # If actually moving...
    if not 0 == position :

      # First point is the starting position and no motion.
      self._point[ self.Point.T0 ].t = 0.0
      self._point[ self.Point.T0 ].a = 0.0
      self._point[ self.Point.T0 ].v = 0.0
      self._point[ self.Point.T0 ].x = startPosition

      t2 = sqrt( 2 * position / ( minAcceleration**2 / maxAcceleration + minAcceleration ) )
      t1 = minAcceleration / maxAcceleration * t2

      accelerationTime = velocity / maxAcceleration
      decelerationTime = velocity / minAcceleration

      riseTime = min( accelerationTime, t1 )

      self._nextPoint( self.Point.T1, self.Point.T0, forwardAcceleration, riseTime )

      accelerationDistance = self._calculateX( maxAcceleration, 0, 0, accelerationTime )
      decelerationDistance = self._calculateX( minAcceleration, 0, 0, decelerationTime )

      distance = position - accelerationDistance - decelerationDistance

      dwellTime = max( distance / velocity, 0 )

      self._nextPoint( self.Point.T2, self.Point.T1, 0, dwellTime )

      if dwellTime :
        fallTime = decelerationTime
      else :
        fallTime = t2

      self._nextPoint( self.Point.T3, self.Point.T2, reverseAcceleration, fallTime )

    else:
      self._point = [ self.Point() for _ in range( self.Point.POINTS ) ]
      for point in self._point :
        point.x = startPosition

  #---------------------------------------------------------------------
  def _getIndex( self, time ) :
    """
    Get the index of the point to use for the given time.

    Args:
      time: Time for which to do compute.

    Returns:
      Point index that covers this time.
    """

    # Search for starting point.
    index = 0
    while ( ( index < self.Point.POINTS )     \
        and ( self._point[ index ].t <= time  ) ) :
      index += 1

    # Index has overshot, back it up.
    index -= 1

    return index

  #---------------------------------------------------------------------
  def isMoving( self, time ):
    """
    See if there is motion for the given time.

    Args:
      time: Time for which to check.

    Returns:
      True if in motion at this time, False if not.
    """

    #print time, self._point[ self.Point.T7 ].t, time < self._point[ self.Point.T7 ].t
    return time >= 0 and time < self._point[ self.Point.T3 ].t

  #---------------------------------------------------------------------
  def interpolatePosition( self, time ) :
    """
    Compute a position based on time.

    Args:
      time: Time for which to get position.

    Returns:
      Position at this time.
    """


    # Start with initial position.
    result = self._point[ self.Point.T0 ].x

    # Search for starting point.
    index = self._getIndex( time )

    # If starting from somewhere other than the first point...
    if index >= 0 :
      # Result calculated using this starting point.
      result =                            \
        self._calculateX(                 \
          self._point[ index ].a,         \
          self._point[ index ].v,         \
          self._point[ index ].x,         \
          time - self._point[ index ].t   \
        )

    return result

  #---------------------------------------------------------------------
  def interpolateVelocity( self, time ) :
    """
    Compute a velocity based on time.

    Args:
      time: Time for which to get velocity.

    Returns:
      Velocity at this time.
    """


    # Start with initial position.
    result = self._point[ self.Point.T0 ].x

    # Search for starting point.
    index = self._getIndex( time )

    # If starting from somewhere other than the first point...
    if index >= 0 :
      # Result calculated using this starting point.
      result =                            \
        self._calculateV(                 \
          self._point[ index ].a,         \
          self._point[ index ].v,         \
          time - self._point[ index ].t   \
        )

    return result

  #---------------------------------------------------------------------
  def interpolateAcceleration( self, time ) :
    """
    Compute an acceleration based on time.

    Args:
      time: Time for which to get acceleration.

    Returns:
      Acceleration at this time.
    """


    # Start with initial position.
    result = self._point[ self.Point.T0 ].x

    # Search for starting point.
    index = self._getIndex( time )

    # If starting from somewhere other than the first point...
    if index >= 0 :
      # Result calculated using this starting point.
      result = self._point[ index ].a

    return result

  #---------------------------------------------------------------------
  def hardStop( self, time ) :
    """
    Compute position from an instant stop at current time.

    Args:
      time - Current time.
    """

    currentPosition = self.interpolatePosition( time )
    self.compute( 0, 0, 0, currentPosition, currentPosition )

# end class

#------------------------------------------------------------------------------
# Unit test.
#   Motion.py <jerk> <acceleration> <velocity> <startPosition> <endPosition>
#------------------------------------------------------------------------------
if __name__ == "__main__":

  import sys

  # Get command line parameters.
  maxAcceleration, minAcceleration, velocity, startPosition, endPosition = map( float, sys.argv[ 1:6 ] )

  # print maxAcceleration, minAcceleration, velocity, startPosition, endPosition

  # Create instance of motion class.
  motion = TrapezoidalMotion( maxAcceleration, minAcceleration, velocity, startPosition, endPosition )

  # Print the transition points.
  for index in range( 0, motion.Point.POINTS ) :
    print                                    \
      "T%u %9.4f: %9.4f %9.4f %9.2f" % \
      (                                      \
        index,                               \
        motion._point[ index ].t,            \
        motion._point[ index ].a,            \
        motion._point[ index ].v,            \
        motion._point[ index ].x             \
      )

  print ""

  # Print an interpolation.
  COUNT = 50
  OVER  = 5
  for count in range( -OVER, COUNT + OVER + 1 ) :
    time = count * motion._point[ motion.Point.T3 ].t / COUNT
    print "%f,%f,%f,%f" % ( time, motion.interpolatePosition( time ), motion.interpolateVelocity( time ), motion.interpolateAcceleration( time ) )