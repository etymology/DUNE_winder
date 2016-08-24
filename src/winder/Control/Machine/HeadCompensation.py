###############################################################################
# Name: HeadCompensation.py
# Uses: Compensation calculations to account for arm on winder head.
# Date: 2016-08-19
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
from Library.Geometry.Location import Location

class HeadCompensation :

  #---------------------------------------------------------------------
  def __init__( self, machineCalibration ) :
    """
    Constructor.

    Args:
      machineCalibration - Instance of MachineCalibration.
    """
    self._machineCalibration = machineCalibration
    self._anchorPoint = Location()

  #---------------------------------------------------------------------
  def anchorPoint( self, location = None ) :
    """
    Get/set anchor point.

    Args:
      location - Location of the anchor point (omit to read).

    Returns:
      The current anchor point.
    """
    if None != location :
      self._anchorPoint = location.copy()

    return self._anchorPoint

  #---------------------------------------------------------------------
  def getHeadAngle( self, location ) :
    """
    Get the angle of the arm.

    Args:
      location: Location of actual machine position.

    Returns:
      Angle of the arm (-pi to +pi).
    """
    deltaX = location.x - self._anchorPoint.x
    deltaZ = location.z - self._anchorPoint.z
    return math.atan2( deltaX, deltaZ )

  #---------------------------------------------------------------------
  def getActualLocation( self, machineLocation ) :
    """
    Get the actual wire position given machine position.  Assume an anchor
    point has been specified.

    Args:
      machineLocation - Actual machine position.

    Returns:
      Location object with the adjusted coordinates.
    """
    deltaX = machineLocation.x - self._anchorPoint.x
    deltaZ = machineLocation.z - self._anchorPoint.z

    xzHypotenuse = math.sqrt( deltaX**2 + deltaZ**2 )
    armLength = self._machineCalibration.headArmLength
    ratio = armLength / xzHypotenuse

    x = machineLocation.x - deltaX * ratio
    y = machineLocation.y
    z = machineLocation.z - deltaZ * ratio

    return Location( x, y, z )

  #---------------------------------------------------------------------
  def correctY( self, machineLocation ) :
    """
    Calculation a correction factor to Y that will place X as the nominal
    position.

    Args:
      machineLocation - Actual machine position.

    Returns:
      Correct Y value.
    """
    deltaX = machineLocation.x - self._anchorPoint.x
    deltaY = machineLocation.y - self._anchorPoint.y
    deltaZ = machineLocation.z - self._anchorPoint.z

    xzHypotenuse = math.sqrt( deltaX**2 + deltaZ**2 )
    armLength = self._machineCalibration.headArmLength
    ratio = armLength / xzHypotenuse

    y = machineLocation.y - deltaY * ratio

    return y

  #---------------------------------------------------------------------
  def correctX( self, machineLocation ) :
    """
    Calculation a correction factor to X that will place Y as the nominal
    position.

    Args:
      machineLocation - Actual machine position.

    Returns:
      Correct X value.
    """

    deltaX = machineLocation.x - self._anchorPoint.x
    deltaZ = machineLocation.z - self._anchorPoint.z
    armLength = self._machineCalibration.headArmLength

    # Iterative method that converges on the answer.
    # Easier to solve than the exact solution.  Runs until answer no longer
    # changes (i.e. is as exact as precision allows).  Typically only a few
    # iterations are necessary.  Converges more slowly for small values of
    # x and z.
    lastX = deltaX
    isDone = False
    while not isDone :
      x = deltaX + lastX * armLength / math.sqrt( lastX**2 + deltaZ**2 )

      change = abs( x - lastX )
      isDone = ( change < 1e12 )
      lastX = x

    x += self._anchorPoint.x

    return x

# end class


if __name__ == "__main__":
  from DefaultCalibration import DefaultMachineCalibration

  machineCalibration = DefaultMachineCalibration()

  # Setup test values.
  machineCalibration.headArmLength = 3
  anchorPoint = Location( 2, 8, 6 )
  machinePosition = Location( 5, 13, 15 )

  # Setup instance of compensation.
  headCompensation = HeadCompensation( machineCalibration )
  headCompensation.anchorPoint( anchorPoint )

  # Run tests.
  actualLocation = headCompensation.getActualLocation( machinePosition )
  correctY = headCompensation.correctY( machinePosition )
  correctX = headCompensation.correctX( machinePosition )

  # Desired answers (within 6 decimal places).
  desiredActualLocation = Location( 4.051317, 13, 12.153950 )
  desiredCorrectY = 11.418861
  desiredCorrectX = 6.5

  # Verify results.
  assert( round( actualLocation.x, 6 ) == desiredActualLocation.x )
  assert( round( actualLocation.y, 6 ) == desiredActualLocation.y )
  assert( round( actualLocation.z, 6 ) == desiredActualLocation.z )
  assert( round( correctY, 6 ) == desiredCorrectY )
  assert( round( correctX, 6 ) == desiredCorrectX )
