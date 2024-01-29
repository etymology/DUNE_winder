###############################################################################
# Name: LayerError.py
# Uses: Introduce error into a layer.
# Date: 2016-10-31
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from __future__ import absolute_import
import math
import random

class LayerError :
  #---------------------------------------------------------------------
  @staticmethod
  def addError( layer, maxError, standardDeviations=3 ) :
    """
    Introduce an error into pin locations.

    Args:
      layer: Layer to introduce error.
      maxError: Maximum amount of error to introduce.
      standardDeviations: Number of standard deviations to distribute noise.
    Notes:
      This uses the Box-Muller transform to generate uniformly distributed
      random numbers.  All values over 'maxError' are discarded.  What results
      are errors with a maximum range and fairly Gaussian distribution.  The
      number of standard deviations determines the amount of scatter.  The
      higher the value the less scatter.  A value of 3 standard deviations
      follows the three-sigma rule, discards only 0.3% of values and gives a
      very good Gaussian distribution curve.
    """

    # Standard deviation used for Box-Muller.
    standardDeviation = maxError / standardDeviations

    # Loop through all pins...
    pins = layer.getPinNames()
    for pinName in pins :
      pin = layer.getPinLocation( pinName )

      # Start saturated (forces first update).
      valueX = float( "inf" )
      valueY = float( "inf" )

      # Loop until the random error is within tolerance...
      while ( abs( valueX ) > maxError ) or ( abs( valueY ) > maxError ) :
        # Box-Muller transform.  Returns two values.
        # NOTE: Could have used 'random.gauss' but this method gives us two
        # values at a time, which is what we want.
        partA = standardDeviation * math.sqrt( -2 * math.log( random.random() ) )
        partB = 2 * math.pi * random.random()
        valueX = partA * math.sin( partB )
        valueY = partA * math.cos( partB )

      # Adjust pin location.
      pin.x += valueX
      pin.y += valueY

  #---------------------------------------------------------------------
  @staticmethod
  def rotate( layer, angle ) :
    """
    Introduce rotational error into pin positions.

    Args:
      layer: Layer to introduce error.
      angle: Amount of rotational error (in degrees).

    Notes:
      Rotates clockwise about pin center.
    """

    # Convert angle to radians.
    angle = math.radians( angle )

    # Min/max values for pin locations.
    minX = float( 'inf' )
    maxX = float( '-inf' )
    minY = float( 'inf' )
    maxY = float( '-inf' )

    # Get the min/max values for all pin locations.
    pins = layer.getPinNames()
    for pinName in pins :
      pin = layer.getPinLocation( pinName )
      minX = min( minX, pin.x )
      maxX = max( maxX, pin.x )
      minY = min( minY, pin.y )
      maxY = max( maxY, pin.y )

    # Find the center of all pins.
    centerX = ( maxX - minX ) / 2 + minX
    centerY = ( maxY - minY ) / 2 + minY

    # Rotate each pin about the center.
    for pinName in pins :
      pin = layer.getPinLocation( pinName )

      # Delta from center location.
      deltaX = pin.x - centerX
      deltaY = pin.y - centerY

      # Rotate point.
      # We use the rotation matrix:
      #  [ x' ] = [  cos  sin ][ x ]
      #  [ y' ] = [ -sin  cos ][ y ]
      # (in expanded form) and then correct for center.
      pin.x = centerX + deltaX * math.cos( angle ) + deltaY * math.sin( angle )
      pin.y = centerY - deltaX * math.sin( angle ) + deltaY * math.cos( angle )
