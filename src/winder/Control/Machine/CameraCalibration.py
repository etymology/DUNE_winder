###############################################################################
# Name: CameraCalibration.py
# Uses: Use calibration data from vision system to generate layer calibration.
# Date: 2016-12-22
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

class CameraCalibration :

  #---------------------------------------------------------------------
  def __init__( self, captureData, width, height, pixelsPer_mm = None ) :
    """
    Constructor.

    Args:
      captureData: Capture data acquired by camera unit.
      width: Pixel width of camera.
      height: Pixel height of camera.
      pixelsPer_mm: Number of pixels/mm represented by camera.
    """
    self._captureData = captureData
    self._width = width
    self._height = height
    self._pixelsPer_mm = pixelsPer_mm

  #---------------------------------------------------------------------
  def computePixelPer_mm( self, startX, startY, deltaX, deltaY ) :
    """
    Construct pin locations based on capture data.

    Args:
      startX: Starting location in X.
      startY: Starting location in Y.
      deltaX: Nominal change in X for next pin.  (Can be 0 for Y traverse.)
      deltaY: Nominal change in Y for next pin.  (Can be 0 for X traverse.)
    Returns:
      Pixels/mm.  None if there is an error deriving the value.
    """

    sumX_X  = 0
    sumX_XX = 0
    sumX_Y  = 0
    sumX_XY = 0

    sumY_X  = 0
    sumY_XX = 0
    sumY_Y  = 0
    sumY_XY = 0

    index = 0
    count = 0

    # Loop to compute pixels/mm.
    # Does so by using linear regression to compute the slope between the
    # nominal position error and camera X/Y data.  Works because we can assume
    # the pins are evenly spaced by the given delta.
    for row in self._captureData :
      if row[ "Status" ] > 0 :
        count += 1

        # Location capture should have taken place.
        nominalX = index * deltaX + startX
        nominalY = index * deltaY + startY

        # Location capture took place.
        motorX  = row[ "MotorX" ]
        motorY  = row[ "MotorY" ]

        # Location camera saw pin.
        cameraX = row[ "CameraX" ]
        cameraY = row[ "CameraY" ]

        # Error between where we wanted to trigger, and where we did trigger.
        errorX = nominalX - motorX
        errorY = nominalY - motorY

        # Accumulate data for X.
        sumX_X  += errorX
        sumX_XX += errorX * errorX
        sumX_Y  += cameraX
        sumX_XY += cameraX * errorX

        # Accumulate data for Y.
        sumY_X  += errorY
        sumY_XX += errorY * errorY
        sumY_Y  += cameraY
        sumY_XY += cameraY * errorY

      index += 1

    # Denominator for slope calculation.
    denominator = count * sumX_XX - sumX_X**2

    # Avoid divide-by-zero.
    if denominator > 0 :
      # Calculate slope.
      slopeX  = count * sumX_XY - sumX_Y * sumX_X
      slopeX /= denominator
    else:
      slopeX = 0

    # Denominator for slope calculation.
    denominator = count * sumY_XX - sumY_X**2

    if denominator > 0 :
      # Calculate slope.
      slopeY  = count * sumY_XY - sumY_Y * sumY_X
      slopeY /= denominator
    else:
      slopeY = 0

    # Whichever slope isn't 0 is the pixels/mm value.
    if slopeX > 0 :
      pixelsPer_mm = slopeX
    elif slopeY > 0 :
      pixelsPer_mm = slopeY
    else:
      pixelsPer_mm = None

    self._pixelsPer_mm = pixelsPer_mm

    return pixelsPer_mm

  #---------------------------------------------------------------------
  def computePinLocations( self, startingPin, direction, maxPins ) :
    """
    Construct pin locations based on capture data.

    Args:
      startingPin: Name of starting pin (Side/number format i.e. F101).
      direction: Direction for next pin number (+1/-1).
      maxPins: Number of pins before wrap around.
    Returns:
      Array of dictionaries with pin locations.  Dictionaries have three keys:
      "Pin", "x", and "y".  Missing pins will have their x/y values set to None.
    """

    centerX = self._width / 2
    centerY = self._height / 2

    pinSide   = startingPin[ 0 ]
    pinNumber = int( startingPin[ 1: ] ) - 1

    #
    # Loop to compute each pin location.
    #
    locations = []
    for row in self._captureData :

      pin = pinSide + str( pinNumber + 1 )
      newPin = { "Pin" : pin }

      if row[ "Status" ] > 0 :
        newPin[ "x" ] = row[ "MotorX" ] + ( ( row[ "CameraX" ] - centerX ) / self._pixelsPer_mm )
        newPin[ "y" ] = row[ "MotorY" ] + ( ( row[ "CameraY" ] - centerY ) / self._pixelsPer_mm )
      else :
        newPin[ "x" ] = None
        newPin[ "y" ] = None

      locations.append( newPin )

      pinNumber += direction
      if pinNumber > maxPins :
        pinNumber = 0
      elif pinNumber < 0 :
        pinNumber = maxPins - 1

    return locations


if __name__ == "__main__":

  #
  # Unit test data.
  # This comes from the spreadsheet '2016-12-20 -- Calibration worksheet.ods',
  # on sheet 'SimulatedXY'.
  # Spreadsheet generates random data and expected results.
  #

  # Test input data.
  INPUT_DATA = [
    {"Status" : 1,"MotorX" : 300,"MotorY" : 110,"CameraX" : 318.97473423928,"CameraY" : 242.938638808206,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 306.47810424678,"MotorY" : 110,"CameraX" : 334.493492848155,"CameraY" : 244.36545536617,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 315.577390874736,"MotorY" : 110,"CameraX" : 323.023190793411,"CameraY" : 243.003660566103,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 324.812859703787,"MotorY" : 110,"CameraX" : 314.87892899078,"CameraY" : 242.15560173838,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 333.312151013873,"MotorY" : 110,"CameraX" : 308.543979744087,"CameraY" : 245.807091103725,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 340.151679445989,"MotorY" : 110,"CameraX" : 317.866107137449,"CameraY" : 247.053878010539,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 349.670304485597,"MotorY" : 110,"CameraX" : 304.597147163425,"CameraY" : 246.687966775868,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 355.803824748844,"MotorY" : 110,"CameraX" : 323.842622803861,"CameraY" : 247.484455250421,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 362.979629277252,"MotorY" : 110,"CameraX" : 333.39442079912,"CameraY" : 249.135497405842,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 370.548498604447,"MotorY" : 110,"CameraX" : 334.340884881261,"CameraY" : 252.354796703121,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 381.139197506011,"MotorY" : 110,"CameraX" : 307.928979807615,"CameraY" : 253.128277784791,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 386.020616489463,"MotorY" : 110,"CameraX" : 338.523601881226,"CameraY" : 255.054315745907,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 395.584789968096,"MotorY" : 110,"CameraX" : 326.099545959295,"CameraY" : 255.185682847671,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 405.482152090408,"MotorY" : 110,"CameraX" : 300.445942579596,"CameraY" : 258.721181388019,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 411.99891726207,"MotorY" : 110,"CameraX" : 318.355173747729,"CameraY" : 262.690228032384,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 420.214562436566,"MotorY" : 110,"CameraX" : 313.621229111806,"CameraY" : 262.935142315859,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 427.866465658881,"MotorY" : 110,"CameraX" : 320.693596310486,"CameraY" : 263.275998362705,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 437.2002993403,"MotorY" : 110,"CameraX" : 305.565516598942,"CameraY" : 266.10677761664,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 443.792681883089,"MotorY" : 110,"CameraX" : 321.309305022805,"CameraY" : 265.44869027875,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 452.692520598881,"MotorY" : 110,"CameraX" : 312.59541732284,"CameraY" : 272.921397503258,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 459.591615981422,"MotorY" : 110,"CameraX" : 326.111522267737,"CameraY" : 272.89281062711,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 466.737228278071,"MotorY" : 110,"CameraX" : 332.435711261896,"CameraY" : 272.154769587053,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 474.776436796412,"MotorY" : 110,"CameraX" : 335.167472030962,"CameraY" : 275.813183443773,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 484.955385124311,"MotorY" : 110,"CameraX" : 309.562848827711,"CameraY" : 273.893919424737,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 490.70198219642,"MotorY" : 110,"CameraX" : 331.225561600003,"CameraY" : 275.0449640612,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 501.466769508086,"MotorY" : 110,"CameraX" : 304.964133664705,"CameraY" : 279.845382677903,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 509.380204966292,"MotorY" : 110,"CameraX" : 308.266421148208,"CameraY" : 279.376405633997,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 517.009551597759,"MotorY" : 110,"CameraX" : 307.818600550795,"CameraY" : 281.703354333969,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 523.872558983974,"MotorY" : 110,"CameraX" : 323.651378905817,"CameraY" : 286.199132912732,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 530.101148935966,"MotorY" : 110,"CameraX" : 338.943230544548,"CameraY" : 283.400954265518,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 541.641851983964,"MotorY" : 110,"CameraX" : 298.14310666664,"CameraY" : 287.025868091602,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 548.94113175571,"MotorY" : 110,"CameraX" : 312.151856796977,"CameraY" : 286.426453640053,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 554.432452006266,"MotorY" : 110,"CameraX" : 333.139706441278,"CameraY" : 288.019967832401,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 565.820600667968,"MotorY" : 110,"CameraX" : 298.001276129848,"CameraY" : 290.983452057695,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 572.95083035063,"MotorY" : 110,"CameraX" : 307.561711344774,"CameraY" : 293.922541331228,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 581.1982931979,"MotorY" : 110,"CameraX" : 304.939621394322,"CameraY" : 290.527911530034,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 586.821906954981,"MotorY" : 110,"CameraX" : 330.712094073852,"CameraY" : 295.541554803617,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 596.199912364595,"MotorY" : 110,"CameraX" : 314.202444209369,"CameraY" : 300.269775182096,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 604.98366480507,"MotorY" : 110,"CameraX" : 309.326445440329,"CameraY" : 296.031643166724,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 610.709405411035,"MotorY" : 110,"CameraX" : 332.995309564698,"CameraY" : 295.962571893835,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 621.713248849846,"MotorY" : 110,"CameraX" : 299.723749152713,"CameraY" : 304.127553036883,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 628.419045197778,"MotorY" : 110,"CameraX" : 312.138413310294,"CameraY" : 305.1226162407,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 635.245287933387,"MotorY" : 110,"CameraX" : 324.20665272993,"CameraY" : 302.685751463662,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 642.219658281654,"MotorY" : 110,"CameraX" : 342.916088008395,"CameraY" : 308.09889493777,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 650.121248819865,"MotorY" : 110,"CameraX" : 341.68286444525,"CameraY" : 309.953215148605,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 659.376314568333,"MotorY" : 110,"CameraX" : 326.671169137486,"CameraY" : 309.304235907075,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 667.14522315003,"MotorY" : 110,"CameraX" : 330.002100150851,"CameraY" : 311.511561923895,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 676.267140870914,"MotorY" : 110,"CameraX" : 315.93699404105,"CameraY" : 314.071992353269,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 682.533696552739,"MotorY" : 110,"CameraX" : 336.868626514099,"CameraY" : 317.16002393344,"MatchLevel" : 100},
    {"Status" : 1,"MotorX" : 692.333124917001,"MotorY" : 110,"CameraX" : 316.748446992162,"CameraY" : 313.233635328372,"MatchLevel" : 100},
  ]

  # The calculated pixels/mm for test data.
  TRUE_PIXELS_PER_MM = 10.7681814064

  # The calculated pixels/mm for test data.
  EXPECTED_DATA = [
    { "x": 299.904787473202,"y": 110.272900195242 },
    { "x": 307.824059733705,"y": 110.4054032154 },
    { "x": 315.858143090854,"y": 110.278938518283 },
    { "x": 324.33728534114,"y": 110.200182524516 },
    { "x": 332.248274039337,"y": 110.539282436333 },
    { "x": 339.9535129421,"y": 110.655066788375 },
    { "x": 348.239900199558,"y": 110.621086005469 },
    { "x": 356.160674495225,"y": 110.695052856926 },
    { "x": 364.223518128451,"y": 110.848378854428 },
    { "x": 371.880281970645,"y": 111.147342920483 },
    { "x": 380.018207829406,"y": 111.21917316298 },
    { "x": 387.740832854893,"y": 111.398036973722 },
    { "x": 396.151231573144,"y": 111.410236536193 },
    { "x": 403.666241243218,"y": 111.738564821807 },
    { "x": 411.846168511822,"y": 112.10715506881 },
    { "x": 419.622190275711,"y": 112.129899325638 },
    { "x": 427.930877306893,"y": 112.161553328666 },
    { "x": 435.859823836009,"y": 112.424437017852 },
    { "x": 443.914272054483,"y": 112.363322952899 },
    { "x": 452.004885203664,"y": 113.057284815397 },
    { "x": 460.159169780627,"y": 113.054630061074 },
    { "x": 467.89208542549,"y": 112.986091000279 },
    { "x": 476.184982163407,"y": 113.325833963241 },
    { "x": 483.98612664153,"y": 113.147599222703 },
    { "x": 491.744457353212,"y": 113.254492354702 },
    { "x": 500.070445860869,"y": 113.700288950759 },
    { "x": 508.29055218195,"y": 113.656736838642 },
    { "x": 515.878311419919,"y": 113.87283170296 },
    { "x": 524.211648637836,"y": 114.290337538819 },
    { "x": 531.860334617336,"y": 114.030481343831 },
    { "x": 539.612085535161,"y": 114.367113286521 },
    { "x": 548.212304583616,"y": 114.311447949086 },
    { "x": 555.652686505051,"y": 114.459431543735 },
    { "x": 563.77766295733,"y": 114.734639038246 },
    { "x": 571.795733850508,"y": 115.007581066487 },
    { "x": 579.79969318948,"y": 114.692334724224 },
    { "x": 587.816698337998,"y": 115.157932682167 },
    { "x": 595.661515436476,"y": 115.597024502784 },
    { "x": 603.99245243997,"y": 115.203445322102 },
    { "x": 611.916230321782,"y": 115.197030936025 },
    { "x": 619.830270649347,"y": 115.955281641031 },
    { "x": 627.688969580271,"y": 116.047689371386 },
    { "x": 635.635943752709,"y": 115.821387019572 },
    { "x": 644.34778810632,"y": 116.324085039767 },
    { "x": 652.134853868564,"y": 116.496288696155 },
    { "x": 659.995840641094,"y": 116.436020465427 },
    { "x": 668.074080101204,"y": 116.641006426706 },
    { "x": 675.889824980179,"y": 116.878783850092 },
    { "x": 684.100221658274,"y": 117.165557583151 },
    { "x": 692.031165571674,"y": 116.800928825808 },
  ]

  import itertools
  from Library.MathExtra import MathExtra

  # Create instance of camera.
  camera = CameraCalibration( INPUT_DATA, 640, 480 )

  # Start with computing the number of pixels/mm.
  pixelsPer_mm = camera.computePixelPer_mm( 300, 110, 8, 0 )

  assert( MathExtra.isclose( TRUE_PIXELS_PER_MM, pixelsPer_mm ) )

  # Calculate resulting pin positions.
  # (Parameters don't matter.)
  pinLocations = camera.computePinLocations( "F1", 1, 1000 )

  assert( len( pinLocations ) == len( EXPECTED_DATA ) )

  # Verify results.
  for a, b in itertools.izip( pinLocations, EXPECTED_DATA ) :
    assert( MathExtra.isclose( a[ "x" ], b[ "x" ] ) )
    assert( MathExtra.isclose( a[ "y" ], b[ "y" ] ) )
