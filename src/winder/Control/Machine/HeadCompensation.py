###############################################################################
# Name: HeadCompensation.py
# Uses: Compensation calculations to account for arm and rollers on winder head.
# Date: 2016-08-19
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   This unit is trigonometric intensive.  The equations are explained in
#   the development log, verified visually on drawings and with spreadsheets.
# References:
#   Spreadsheet file "2016-09-09 -- Roller correction worksheet.ods"
#   Spreadsheet file "2016-08-25 -- Tangent circle worksheet.ods".
###############################################################################

import math
from Library.MathExtra import MathExtra
from Library.Geometry.Location import Location
from Library.Geometry.Circle import Circle

class HeadCompensation :

  #---------------------------------------------------------------------
  def __init__( self, machineCalibration ) :
    """
    Constructor.

    Args:
      machineCalibration - Instance of MachineCalibration.
    """
    self._machineCalibration = machineCalibration
    self._anchorPoint = Location( -1 )
    self._orientation = None

  #---------------------------------------------------------------------
  def orientation( self, value = None ) :
    """
    Get/set orientation of connecting wire.

    Args:
      value - New orientation (omit to read).

    Returns:
      The current orientation.
    """

    if None != value :
      self._orientation = value

    return self._orientation

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
  def pinCompensation( self, endPoint ) :
    """
    Get the anchor position while compensating for the pin radius.
    This will compute a point for which the connecting line will run tangent
    to the anchor point circle.

    Args:
      endPoint: Target destination to run tangent line.

    Returns:
      Instance of location.  None if the orientation is incorrect for the
      target location.
    """

    result = None
    if self._orientation :
      pinRadius = self._machineCalibration.pinDiameter / 2
      circle = Circle( self._anchorPoint, pinRadius )
      result = circle.tangentPoint( self._orientation, endPoint )
    else :
      result = self._anchorPoint

    return result

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

    #
    # First compensation is to correct for the angle of the arm on the head.
    #

    # Compute various lengths.
    deltaX = machineLocation.x - self._anchorPoint.x
    deltaZ = machineLocation.z - self._anchorPoint.z
    lengthXZ = math.sqrt( deltaX**2 + deltaZ**2 )
    headRatio = self._machineCalibration.headArmLength / lengthXZ

    # Make correction.
    x = machineLocation.x - deltaX * headRatio
    y = machineLocation.y
    z = machineLocation.z - deltaZ * headRatio

    #
    # Second correction to the correct for the offset caused by the upper and
    # lower roller on the front of the head.
    #

    # Compute various lengths.
    deltaX   = x - self._anchorPoint.x
    deltaY   = y - self._anchorPoint.y
    deltaZ   = z - self._anchorPoint.z
    lengthXZ  = math.sqrt( deltaX**2 + deltaZ**2 )
    lengthXYZ = math.sqrt( deltaX**2 + deltaY**2 + deltaZ**2 )

    # The rollers are in two plans: Y and XZ.
    rollerOffsetY  = self._machineCalibration.headRollerRadius * lengthXZ / lengthXYZ
    rollerOffsetXZ = self._machineCalibration.headRollerRadius * deltaY / lengthXYZ

    # Get the specific X and Z components out of the combine XZ value.
    rollerOffsetX = abs( rollerOffsetXZ * deltaX / lengthXZ )
    rollerOffsetZ = abs( rollerOffsetXZ * deltaZ / lengthXZ )

    # Correct for the roller offset made up of the radius, and the gap between
    # them.
    rollerOffsetY -= self._machineCalibration.headRollerRadius
    rollerOffsetY -= self._machineCalibration.headRollerGap / 2

    # Correct for direction form anchor point.
    if deltaX < 0 :
      rollerOffsetX = -rollerOffsetX

    if deltaZ < 0 :
      rollerOffsetZ = -rollerOffsetZ

    if deltaY > 0 :
      rollerOffsetY  = -rollerOffsetY

    # Make correction.
    x -= rollerOffsetX
    y -= rollerOffsetY
    z -= rollerOffsetZ

    return Location( x, y, z )

  #---------------------------------------------------------------------
  def correctY( self, machineLocation ) :
    """
    Calculation a correction factor to Y that will place X as the nominal
    position.

    Args:
      machineLocation - Actual machine position.

    Returns:
      Corrected Y value.
    """

    #
    # Head arm correction.
    #

    # Compute various lengths.
    deltaX = machineLocation.x - self._anchorPoint.x
    deltaY = machineLocation.y - self._anchorPoint.y
    deltaZ = machineLocation.z - self._anchorPoint.z
    lengthXZ = math.sqrt( deltaX**2 + deltaZ**2 )

    # Compute a correction for the arm.
    headCorrection = -deltaY * self._machineCalibration.headArmLength / lengthXZ

    # Compute the new end point.
    x = machineLocation.x - deltaX * self._machineCalibration.headArmLength / lengthXZ
    y = machineLocation.y + headCorrection
    z = machineLocation.z - deltaZ * self._machineCalibration.headArmLength / lengthXZ

    #
    # Roller correction.
    #

    # Compute various lengths.
    deltaX = x - self._anchorPoint.x
    deltaY = y - self._anchorPoint.y
    deltaZ = z - self._anchorPoint.z
    lengthXZ = math.sqrt( deltaX**2 + deltaZ**2 )
    lengthXYZ = math.sqrt( deltaX**2 + deltaY**2 + deltaZ**2 )

    # Offset to Y caused by the roller.
    # NOTE: This correction actually changes the tangent line, but the change
    # is so small (1 part in 1500) it is ignored.  Otherwise an iterative method
    # is required like what is done for the X correction.
    rollerCorrection  = self._machineCalibration.headRollerRadius * lengthXYZ / lengthXZ
    rollerCorrection -= self._machineCalibration.headRollerRadius
    rollerCorrection -= self._machineCalibration.headRollerGap / 2

    # Direction correction.
    if headCorrection < 0 :
      rollerCorrection = -rollerCorrection

    # Correct the Y position with two offsets.
    correctedY = machineLocation.y + headCorrection + rollerCorrection

    return correctedY

  #---------------------------------------------------------------------
  def correctX( self, machineLocation ) :
    """
    Calculation a correction factor to X that will place Y as the nominal
    position.

    Args:
      machineLocation - Actual machine position.

    Returns:
      Corrected X value.
    """

    # Compute various lengths.
    deltaX = machineLocation.x - self._anchorPoint.x
    deltaY = machineLocation.y - self._anchorPoint.y
    deltaZ = machineLocation.z - self._anchorPoint.z

    lengthY = abs( deltaY )

    # Iterative method that converges on the answer.
    # Easier to solve than the exact solution.  Runs until answer no longer
    # changes (i.e. is as exact as precision allows).  Typically only a few
    # iterations are necessary.  Converges more slowly for small values of
    # x and z.
    lastX = deltaX
    isDone = False
    while not isDone :
      # Head arm compensation.
      xzLength = math.sqrt( lastX**2 + deltaZ**2 )
      x = deltaX
      if xzLength > 0 :
        x += lastX * self._machineCalibration.headArmLength / xzLength

      # Roller compensation.
      if xzLength > 0 :
        scaleFactor = self._machineCalibration.headArmLength / xzLength
        armX = lastX - lastX * scaleFactor
        armZ = deltaZ - deltaZ * scaleFactor
        armXZ = math.sqrt( armX**2 + armZ**2 )

        rollerX  = armXZ**2 + deltaY**2
        rollerX /= armXZ**2
        rollerX  = math.sqrt( rollerX )
        rollerX *= self._machineCalibration.headRollerRadius
        rollerX -= self._machineCalibration.headRollerRadius
        rollerX -= self._machineCalibration.headRollerGap / 2
        rollerX *= armX / lengthY

        x += rollerX

      # See if any changes were made to x.  If not, loop is complete.
      isDone = MathExtra.isclose( x, lastX )
      lastX = x

    # Add the correction to the starting point.
    x += self._anchorPoint.x

    return x

# end class


if __name__ == "__main__":
  from MachineCalibration import MachineCalibration

  # Make up a calibration setup for all tests.
  machineCalibration = MachineCalibration()
  machineCalibration.headArmLength    = 125
  machineCalibration.headRollerRadius = 6.35
  machineCalibration.headRollerGap    = 1.27
  machineCalibration.pinDiameter      = 2.43

  # Setup instance of compensation.
  headCompensation = HeadCompensation( machineCalibration )

  #
  # Above and to the right.
  # Values come from spreadsheet "2016-09-09 -- Roller correction worksheet",
  # on sheet "Head_X+++" and "Head_Y+++"
  #

  # Setup test values.
  anchorPoint = Location( 150, 275, 50 )
  machinePosition = Location( 4000, 2700, 150 )
  headCompensation.anchorPoint( anchorPoint )

  # Run tests.
  correctX = headCompensation.correctX( machinePosition )
  correctY = headCompensation.correctY( machinePosition )
  correctedPositionX = machinePosition.copy( x=correctX )
  correctedPositionY = machinePosition.copy( y=correctY )
  headAngleX = headCompensation.getHeadAngle( correctedPositionX )
  headAngleY = headCompensation.getHeadAngle( correctedPositionY )
  wireX = headCompensation.getActualLocation( correctedPositionX )
  wireY = headCompensation.getActualLocation( correctedPositionY )

  desiredCorrectX = 4125.7838871346
  desiredCorrectY = 2620.7738390836
  desiredHeadAngleX = 88.5591847231 / 180 * math.pi
  desiredHeadAngleY = 88.5121324712 / 180 * math.pi
  desiredWireX = Location( 3997.44147251, 2698.38880455, 146.771896605 )
  desiredWireY = Location( 3871.6603482718, 2619.1626868611, 146.6665025525 )

  assert( MathExtra.isclose( desiredCorrectX, correctX ) )
  assert( MathExtra.isclose( desiredCorrectY, correctY ) )
  assert( MathExtra.isclose( desiredHeadAngleX, headAngleX ) )
  assert( MathExtra.isclose( desiredHeadAngleY, headAngleY ) )
  assert( desiredWireX == wireX )
  assert( desiredWireY == wireY )

  #
  # Below and to the left.
  # Values come from spreadsheet "2016-09-09 -- Roller correction worksheet",
  # on sheet "Head_X---" and "Head_Y---"
  #

  # Setup test values.
  anchorPoint = Location( 4000, 2700, 150 )
  machinePosition = Location( 150, 275, 50 )
  headCompensation.anchorPoint( anchorPoint )

  # Run tests.
  correctX = headCompensation.correctX( machinePosition )
  correctY = headCompensation.correctY( machinePosition )
  correctedPositionX = machinePosition.copy( x=correctX )
  correctedPositionY = machinePosition.copy( y=correctY )
  headAngleX = headCompensation.getHeadAngle( correctedPositionX )
  headAngleY = headCompensation.getHeadAngle( correctedPositionY )
  wireX = headCompensation.getActualLocation( correctedPositionX )
  wireY = headCompensation.getActualLocation( correctedPositionY )

  desiredCorrectX = 25.864056226
  desiredCorrectY = 354.2261609164
  desiredHeadAngleX = -91.4414124836 / 180 * math.pi
  desiredHeadAngleY = -91.4878675288 / 180 * math.pi
  desiredWireX = Location( 154.2074732952, 276.6118480603, 53.2294672071 )
  desiredWireY = Location( 278.3396517282, 355.8373131389, 53.3334974475 )

  assert( MathExtra.isclose( desiredCorrectX, correctX ) )
  assert( MathExtra.isclose( desiredCorrectY, correctY ) )
  assert( MathExtra.isclose( desiredHeadAngleX, headAngleX ) )
  assert( MathExtra.isclose( desiredHeadAngleY, headAngleY ) )
  assert( desiredWireX == wireX )
  assert( desiredWireY == wireY )

  #
  # Above and to the left.
  # Values come from spreadsheet "2016-09-09 -- Roller correction worksheet",
  # on sheet "Head_X-++" and "Head_Y-++"
  #

  # Setup test values.
  anchorPoint = Location( 4000, 275, 50 )
  machinePosition = Location( 150, 2700, 150 )
  headCompensation.anchorPoint( anchorPoint )

  # Run tests.
  correctX = headCompensation.correctX( machinePosition )
  correctY = headCompensation.correctY( machinePosition )
  correctedPositionX = machinePosition.copy( x=correctX )
  correctedPositionY = machinePosition.copy( y=correctY )
  headAngleX = headCompensation.getHeadAngle( correctedPositionX )
  headAngleY = headCompensation.getHeadAngle( correctedPositionY )
  wireX = headCompensation.getActualLocation( correctedPositionX )
  wireY = headCompensation.getActualLocation( correctedPositionY )

  desiredCorrectX = 24.2161128654
  desiredCorrectY = 2620.7738390836
  desiredHeadAngleX = -88.5591847231 / 180 * math.pi
  desiredHeadAngleY = -88.5121324712 / 180 * math.pi
  desiredWireX = Location( 152.5585274877, 2698.388804549, 146.7718966054 )
  desiredWireY = Location( 278.3396517282, 2619.1626868611, 146.6665025525 )

  assert( MathExtra.isclose( desiredCorrectX, correctX ) )
  assert( MathExtra.isclose( desiredCorrectY, correctY ) )
  assert( MathExtra.isclose( desiredHeadAngleX, headAngleX ) )
  assert( MathExtra.isclose( desiredHeadAngleY, headAngleY ) )
  assert( desiredWireX == wireX )
  assert( desiredWireY == wireY )

  #
  # Below and to the right.
  # Values come from spreadsheet "2016-09-09 -- Roller correction worksheet",
  # on sheet "Head_X+-+" and "Head_Y+-+"
  #

  # Setup test values.
  anchorPoint = Location( 150, 2700, 50 )
  machinePosition = Location( 4000, 275, 150 )
  headCompensation.anchorPoint( anchorPoint )

  # Run tests.
  correctX = headCompensation.correctX( machinePosition )
  correctY = headCompensation.correctY( machinePosition )
  correctedPositionX = machinePosition.copy( x=correctX )
  correctedPositionY = machinePosition.copy( y=correctY )
  headAngleX = headCompensation.getHeadAngle( correctedPositionX )
  headAngleY = headCompensation.getHeadAngle( correctedPositionY )
  wireX = headCompensation.getActualLocation( correctedPositionX )
  wireY = headCompensation.getActualLocation( correctedPositionY )

  desiredCorrectX = 4124.135943774
  desiredCorrectY = 354.2261609164
  desiredHeadAngleX = 88.5585875164 / 180 * math.pi
  desiredHeadAngleY = 88.5121324712 / 180 * math.pi
  desiredWireX = Location( 3995.7925267048, 276.6118480603, 146.7705327929 )
  desiredWireY = Location( 3871.6603482718, 355.8373131389, 146.6665025525 )

  assert( MathExtra.isclose( desiredCorrectX, correctX ) )
  assert( MathExtra.isclose( desiredCorrectY, correctY ) )
  assert( MathExtra.isclose( desiredHeadAngleX, headAngleX ) )
  assert( MathExtra.isclose( desiredHeadAngleY, headAngleY ) )
  assert( desiredWireX == wireX )
  assert( desiredWireY == wireY )

  #
  # Pin compensation.
  # Values come from spreadsheet "2016-08-25 -- Tangent circle worksheet".
  #

  # Setup test values.
  anchorPoint = Location( 588.274, 170.594 )
  targetPosition = Location( 598.483, 166.131 )
  headCompensation.anchorPoint( anchorPoint )
  headCompensation.orientation( "TR" )

  newTarget = headCompensation.pinCompensation( targetPosition )
  desiredTarget = Location( 588.8791774069, 171.6475584019 )

  assert( newTarget == desiredTarget )
