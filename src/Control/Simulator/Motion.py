###############################################################################
# Name: Motion.py
# Uses: Compute position over time given properties of motion.
# Date: 2016-02-05
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-05 - QUE - Creation.
###############################################################################

from math import sqrt, pow

class Motion :
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
    T4 = 4
    T5 = 5
    T6 = 6
    T7 = 7
    POINTS = 8

    t = 0  # Time.
    j = 0  # Jerk.
    a = 0  # Acceleration.
    v = 0  # Velocity.
    x = 0  # Position.
  # end class

  #---------------------------------------------------------------------
  def _calculateX( self, j, a, v, x, t ) :
    """
    Calculate ending x position given jerk, acceleration, velocity, initial position, and time.

    Args:
      j: Jerk.
      a: Acceleration.
      v: Velocity.
      x: Initial position.
      t: Time from initial position.

    Returns:
      Position after time.
    """

    return x + v * t + 1.0 / 2.0 * a * t * t + 1.0 / 6.0 * j * t * t * t

  #---------------------------------------------------------------------
  def _calculateV( self, j, a, v, t ) :
    """
    Calculate ending velocity given jerk, acceleration, initial velocity, and time.

    Args:
      j: Jerk.
      a: Acceleration.
      v: Initial velocity.
      t: Time from initial position.

    Returns:
      Velocity after time.
    """

    return v + a * t + 1.0 / 2.0 * j * t * t

  #---------------------------------------------------------------------
  def _calculateA( self, j, a, t ) :
    """
    Calculate ending acceleration given jerk, initial acceleration and time.

    Args:
      j: Jerk.
      a: Initial acceleration.
      t: Time from initial position.

    Returns:
      Acceleration after time.
    """

    return a + j * t

  #---------------------------------------------------------------------
  def _nextPoint( self, thisPoint, lastPoint, j, t ) :
    """
    Calculate transition point.

    Args:
      thisPoint: Point (self.Point.*) to calculate.
      lastPoint: Previous point.
      j: Jerk.
      t: Time.

    Returns:
      self._point[ thisPoint ] and self._point[ lastPoint ] are modified. Nothing is returned.
    """

    thisPoint = self._point[ thisPoint ]
    lastPoint = self._point[ lastPoint ]

    thisPoint.t = t + lastPoint.t
    thisPoint.j = 0
    lastPoint.j = j
    thisPoint.a = self._calculateA( j, lastPoint.a, t )
    thisPoint.v = self._calculateV( j, lastPoint.a, lastPoint.v, t )
    thisPoint.x = self._calculateX( j, lastPoint.a, lastPoint.v, lastPoint.x, t )

  #------------------------------------
  # Public functions.
  #------------------------------------

  #---------------------------------------------------------------------
  def __init__(        \
    self,              \
    jerk = 0,          \
    acceleration = 0,  \
    velocity = 0,      \
    startPosition = 0, \
    endPosition = 0    \
    ) :
    """
    Constructor with full parameter set.

    Args:
      jerk: Jerk term.
      acceleration: Maximum acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.

    """
    self._point = [ self.Point() for _ in range( self.Point.POINTS ) ]
    self.compute( jerk, acceleration, velocity, startPosition, endPosition )

  #---------------------------------------------------------------------
  def compute( self, jerk, acceleration, velocity, startPosition, endPosition ) :
    """
    Compute internal point table using the specified settings. Call before using 'interpolatePosition'.

    Args:
      jerk: Jerk term.
      acceleration: Maximum acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.

    Returns:
      Modifies self._point. Nothing is returned.
    """


    # Jerk, acceleration and velocity are magnitudes, so force an absolute value.
    jerk         = abs( jerk         )
    acceleration = abs( acceleration )
    velocity     = abs( velocity     )

    position = endPosition - startPosition
    forwardJerk =  jerk
    reverseJerk = -jerk
    svelocity   = velocity
    if position < 0 :
      position = -position
      forwardJerk = -forwardJerk
      reverseJerk = -reverseJerk
      svelocity   = -velocity

    # We must either not be moving or have a jerk term.
    assert ( 0 == position or not 0 == jerk ), "Cannot move without a jerk term"

    # If actually moving...
    if not 0 == position :

      # First point is the starting position and no motion.
      self._point[ self.Point.T0 ].t = 0.0
      self._point[ self.Point.T0 ].j = 0.0
      self._point[ self.Point.T0 ].a = 0.0
      self._point[ self.Point.T0 ].v = 0.0
      self._point[ self.Point.T0 ].x = startPosition

      # Time it takes to reach maximum acceleration.
      timeToFullAcceleration = acceleration / jerk

      # Time until midpoint where jerk must be reversed to avoid exceeding
      # maximum velocity.
      timeToMidVelocity = sqrt( jerk * velocity ) / jerk

      # Time until midpoint where jerk must be reversed to avoid exceeding
      # desired position.
      timeToMidPosition =                  \
        pow                                \
        (                                  \
          jerk * jerk * position / 2.0,    \
          1.0 / 3.0                        \
        )                                  \
        / jerk

      # First time point is the smallest of the various times.
      t1 = \
        min( min( timeToFullAcceleration, timeToMidVelocity ), timeToMidPosition )

      self._nextPoint( self.Point.T1, self.Point.T0, forwardJerk, t1 )

      # Second time point is either the dwell time at maximum acceleration,
      # or zero in the event maximum acceleration is never reached.
      t2 =                                        \
        (                                         \
          (                                       \
            svelocity                             \
            - 2 * self._point[ self.Point.T1 ].v  \
          )                                       \
          / self._point[ self.Point.T1 ].a
        )

      if ( ( timeToFullAcceleration > timeToMidVelocity ) \
        or ( timeToFullAcceleration > timeToMidPosition ) ) :
          t2 = 0

      self._nextPoint( self.Point.T2, self.Point.T1, 0, t2 )
      self._nextPoint( self.Point.T3, self.Point.T2, reverseJerk, t1 )

      # Time at maximum velocity.
      t4 =                                                                \
        (                                                                 \
          endPosition                                                     \
          - ( 2 * self._point[ self.Point.T3 ].x - startPosition )        \
        )                                                                 \
        / self._point[ self.Point.T3 ].v

      self._nextPoint( self.Point.T4, self.Point.T3, 0, t4 )

      self._nextPoint( self.Point.T5, self.Point.T4, reverseJerk, t1 )
      self._nextPoint( self.Point.T6, self.Point.T5, 0, t2 )
      self._nextPoint( self.Point.T7, self.Point.T6, forwardJerk, t1 )
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
    return time >= 0 and time < self._point[ self.Point.T7 ].t

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
          self._point[ index ].j,         \
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
          self._point[ index ].j,         \
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
      result =                            \
        self._calculateA(                 \
          self._point[ index ].j,         \
          self._point[ index ].a,         \
          time - self._point[ index ].t   \
        )

    return result

  #---------------------------------------------------------------------
  def hardStop( self, time ) :
    """
    $$$DEBUG

    Returns:
      $$$DEBUG
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
  jerk, acceleration, velocity, startPosition, endPosition = map( float, sys.argv[ 1:6 ] )

  # Create instance of motion class.
  motion = Motion( jerk, acceleration, velocity, startPosition, endPosition )

  # Print the transition points.
  for index in range( 0, motion.Point.POINTS ) :
    print                                    \
      "T%u %9.4f: %9.4f %9.4f %9.4f %9.2f" % \
      (                                      \
        index,                               \
        motion._point[ index ].t,            \
        motion._point[ index ].j,            \
        motion._point[ index ].a,            \
        motion._point[ index ].v,            \
        motion._point[ index ].x             \
      )

  print ""

  # Print an interpolation.
  COUNT = 50
  OVER  = 5
  for count in range( -OVER, COUNT + OVER + 1 ) :
    time = count * motion._point[ motion.Point.T7 ].t / COUNT
    print "%f,%f,%f,%f" % ( time, motion.interpolatePosition( time ), motion.interpolateVelocity( time ), motion.interpolateAcceleration( time ) )
