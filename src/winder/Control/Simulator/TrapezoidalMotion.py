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
      endPosition: Finial position.  Use None for jogging.
    """
    self._point = [ self.Point() for _ in range( self.Point.POINTS ) ]

    if None == endPosition :
      self.computeJog( maxAcceleration, velocity, startPosition )
    else :
      self.compute( maxAcceleration, minAcceleration, velocity, startPosition, endPosition )

    # for point in self._point :
    #   print point.t, point.a, point.v, point.x
    #
    # print
    # print

  #---------------------------------------------------------------------
  def computeStop( self, minAcceleration, currentTime ) :
    """
    Used to stop current motion using a deceleration term.

    Args:
      minAcceleration: Maximum negative acceleration.
      currentTime: Current simulation time.
    """

    # Figure out where we are currently.
    startPosition     = self.interpolatePosition( currentTime )
    startVelocity     = self.interpolateVelocity( currentTime )
    startAcceleration = self.interpolateAcceleration( currentTime )

    # Starting point is where the current state of motion.
    self._point[ self.Point.T0 ].t = currentTime
    self._point[ self.Point.T0 ].a = startAcceleration
    self._point[ self.Point.T0 ].v = startVelocity
    self._point[ self.Point.T0 ].x = startPosition

    # Compute time needed to slow down to zero velocity.
    decelerationTime = 0
    if minAcceleration > 0 :
      decelerationTime = abs( startVelocity ) / minAcceleration

    # Correct for direction of travel.
    if startVelocity > 0 :
      minAcceleration = -minAcceleration

    # Compute the point to slow to stop.
    self._nextPoint( self.Point.T1, self.Point.T0, minAcceleration, decelerationTime )

    # Fill remaining points with no motion.
    self._nextPoint( self.Point.T2, self.Point.T1, 0, 0 )
    self._nextPoint( self.Point.T3, self.Point.T2, 0, 0 )

  #---------------------------------------------------------------------
  def computeJog( self, maxAcceleration, velocity, startPosition ) :
    """
    Compute internal poin table for a jog operation.  Call before using
    'interpolatePosition'.

    Args:
      maxAcceleration: Maximum positive acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.

    Returns:
      Modifies self._point. Nothing is returned.
    """

    # Jerk, acceleration and velocity are magnitudes, so force an absolute value.
    maxAcceleration = abs( float( maxAcceleration ) )

    if None == startPosition :
      startPosition = 0

    forwardAcceleration =  maxAcceleration
    if velocity < 0 :
      forwardAcceleration = -forwardAcceleration
      velocity = -velocity

    # We must either not be moving or have a acceleration and velocity term.
    assert ( 0 != maxAcceleration ), "Cannot move without a acceleration term"
    assert ( 0 != velocity ), "Cannot move without a velocity term"

    # First point is the starting position and no motion.
    self._point[ self.Point.T0 ].t = 0.0
    self._point[ self.Point.T0 ].a = 0.0
    self._point[ self.Point.T0 ].v = 0.0
    self._point[ self.Point.T0 ].x = startPosition

    accelerationTime = velocity / maxAcceleration
    self._nextPoint( self.Point.T1, self.Point.T0, forwardAcceleration, accelerationTime )

    # Setup next point with 0 time.  Then force the time to infinite so the motion
    # never stops.
    self._nextPoint( self.Point.T2, self.Point.T1, 0, 0 )
    self._point[ self.Point.T2 ].t = float( "inf" )

    # Last point is the same as previous.
    self._point[ self.Point.T3 ] = self._point[ self.Point.T2 ]

    # for point in self._point :
    #   print point.t, point.a, point.v, point.x
    #
    # print
    # print


  #---------------------------------------------------------------------
  def compute( self, maxAcceleration, minAcceleration, velocity, startPosition, endPosition ) :
    """
    Compute internal point table using the specified settings. Call before using
    'interpolatePosition'.

    Args:
      maxAcceleration: Maximum positive acceleration.
      minAcceleration: Maximum negative acceleration.
      velocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.

    Returns:
      Modifies self._point. Nothing is returned.
    """

    # Jerk, acceleration and velocity are magnitudes, so force an absolute value.
    maxAcceleration = abs( float( maxAcceleration ) )
    minAcceleration = abs( float( minAcceleration ) )
    velocity        = abs( float( velocity        ) )

    if None == endPosition :
      endPosition = 0

    if None == startPosition :
      startPosition = 0

    forwardAcceleration =  maxAcceleration
    reverseAcceleration = -minAcceleration
    svelocity   = velocity
    position = endPosition - startPosition
    if position < 0 :
      position = -position
      forwardAcceleration = -forwardAcceleration
      reverseAcceleration = -reverseAcceleration
      svelocity   = -velocity

    # We must either not be moving or have a acceleration and velocity term.
    assert ( 0 == position or ( 0 != maxAcceleration and 0 != minAcceleration ) ), "Cannot move without a acceleration term"
    assert ( 0 == position or 0 != velocity ), "Cannot move without a velocity term"

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

      # Force the last position to end at the right location and time.
      # Avoids tiny rounding errors.
      self._point[ self.Point.T3 ].a = 0.0
      self._point[ self.Point.T3 ].v = 0.0
      self._point[ self.Point.T3 ].x = endPosition

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

    return time >= 0 and time < self._point[ self.Point.T3 ].t

  #---------------------------------------------------------------------
  @staticmethod
  def computeLimitingVelocity(
    maxAcceleration,
    minAcceleration,
    startPosition,
    endPosition,
    desiredTime
  ) :
    """
    Calculate a limiting velocity that will result in the desired time.  Useful
    for synchronizing multi-axis motion.

    Args:
      maxAcceleration: Maximum positive acceleration.
      minAcceleration: Maximum negative acceleration.
      startPosition: Starting position.
      endPosition: Finial position.
      desiredTime: Amount of time to traverse this distance.

    Returns:
      Limiting velocity needed to obtain this time.  0 if the time needed is
      greater than desired time denoting the operation cannot be done.

    Notes:
      Desired time should be more than the minimum time needed to reach the destination
      with given accelerations.  Otherwise, 0 is returned.
    """

    delta = abs( endPosition - startPosition )

    # Start with the radicand.
    accumulator  = maxAcceleration**2 * minAcceleration**2 * desiredTime** 2
    accumulator -= 2 * maxAcceleration**2 * minAcceleration * delta
    accumulator -= 2 * maxAcceleration * minAcceleration**2 * delta

    # Can this be accomplished (i.e. radicand greater than 0)?
    if accumulator >= 0 :
      accumulator  = sqrt( accumulator )
      accumulator  = maxAcceleration * minAcceleration * desiredTime - accumulator
      accumulator /= maxAcceleration + minAcceleration
    else :
      # Cannot be done in this amount of time.
      accumulator = 0

    return accumulator

  #---------------------------------------------------------------------
  @staticmethod
  def computeTimeLimited(
    maxAcceleration,
    minAcceleration,
    maxVelocity,
    startPosition,
    endPosition,
    desiredTime
  ) :
    """
    Calculate a limiting velocity and accelerations that will result in the
    desired time as well as keep the same acceleration time.  Useful
    for synchronizing multi-axis motion.

    Args:
      maxAcceleration: Maximum positive acceleration.
      minAcceleration: Maximum negative acceleration.
      maxVelocity: Maximum velocity.
      startPosition: Starting position.
      endPosition: Finial position.
      desiredTime: Amount of time to traverse this distance.

    Returns:
      An array with three elements (in order): Limiting positive acceleration,
      negative acceleration, and velocity.

    Notes:
      Desired time should be more than the minimum time needed to reach the destination
      with given accelerations.  Otherwise, 0 is returned.
    """

    # Distance traversed.
    delta = abs( endPosition - startPosition )

    # Time needed to reach full velocity.
    accelerationTime = maxVelocity / maxAcceleration
    decelerationTime = maxVelocity / minAcceleration

    # If the time needed to fully accelerate to full speed isn't long enough...
    if accelerationTime + decelerationTime > desiredTime :
      # Calculate transition points.
      t1 = desiredTime * minAcceleration / ( minAcceleration + maxAcceleration )
      t2 = desiredTime * maxAcceleration / ( minAcceleration + maxAcceleration )

      # Calculate velocity actually achieved.
      velocity = maxAcceleration * t1

      # Calculate new accelerations.
      newPositiveAcceleration = 2 * delta / ( t1 * ( t1 + t2 ) )
      newNegitiveAcceleration = newPositiveAcceleration * t1 / t2
    else:
      # New limiting velocity.
      velocity  = 2 * delta
      velocity /= ( 2 * desiredTime - accelerationTime - decelerationTime )

      # New accelerations.
      newPositiveAcceleration = velocity * maxAcceleration / maxVelocity
      newNegitiveAcceleration = velocity * minAcceleration / maxVelocity

    return [ newPositiveAcceleration, newNegitiveAcceleration, velocity ]

  #---------------------------------------------------------------------
  @staticmethod
  def computeTravelTime(
    maxAcceleration,
    minAcceleration,
    maxVelocity,
    startPosition,
    endPosition
  ) :
    """
    Return total time need for travel.

    Args:
      maxAcceleration: Maximum positive acceleration.
      minAcceleration: Maximum negative acceleration.
      maxVelocity: Maximum maxVelocity.
      startPosition: Starting position.
      endPosition: Finial position.

    Returns:
      Time needed for travel.
    """

    delta = abs( endPosition - startPosition )

    result = 0

    # Don't bother if there isn't any motion.
    if delta > 0 :
      # Time if max maxVelocity is reached.
      t1  = delta / maxVelocity
      t1 += maxVelocity / ( 2 * maxAcceleration )
      t1 += maxVelocity / ( 2 * minAcceleration )

      # Time if max maxVelocity is not reached.
      t2  = 1.0 / minAcceleration
      t2 += 1.0 / maxAcceleration
      t2 *= 2 * delta
      t2  = sqrt( t2 )

      # Maximum maxVelocity using t2.
      finialVelocity  = maxAcceleration + minAcceleration
      finialVelocity *= minAcceleration
      finialVelocity  = 2 * maxAcceleration * delta / finialVelocity
      finialVelocity  = sqrt( finialVelocity )
      finialVelocity *= minAcceleration

      # We can use t2 (which should always be lower) if it does not exceed the
      # maximum maxVelocity.
      if finialVelocity < maxVelocity :
        result = t2
      else :
        result = t1

    return result

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
