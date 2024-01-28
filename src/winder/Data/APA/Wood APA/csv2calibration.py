import sys

sys.path.append( '../../../Control' )

from Machine.LayerCalibration import LayerCalibration
from Library.SerializableLocation import SerializableLocation
from Machine.X_LayerGeometry import X_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.G_LayerGeometry import G_LayerGeometry

if len( sys.argv ) != 4 :
  print "Syntax:"
  print "  csv2calibration <layer> <input CSV> <output XML>"
  sys.exit( -1 )

layer          = sys.argv[ 1 ]
inputFileName  = sys.argv[ 2 ]
outputFileName = sys.argv[ 3 ]

# Read all lines.
with open( inputFileName, "r" ) as inputFile :
  lines = inputFile.read().split( "\n" )

points = []
for line in lines:
  # Skip blank lines.
  if line != "":
    cols = line.split( "\t" )
    points.append( cols )

if "X" == layer :
  geometry = X_LayerGeometry()
elif "V" == layer :
  geometry = V_LayerGeometry()
elif "U" == layer :
  geometry = U_LayerGeometry()
elif "G" == layer :
  geometry = G_LayerGeometry()
else :
  raise "Unknown layer: " + str( layer )

layerCalibration = LayerCalibration( layer )

# Offset of 0,0 on the APA to machine offset.
layerCalibration.offset = SerializableLocation()

# Z-positions to level with front/back of pins.
layerCalibration.zFront = geometry.mostlyExtend
layerCalibration.zBack  = geometry.mostlyRetract

# For each point...
for point in points :
  pinFront = int( point[ 0 ] )
  pinBack  = ( geometry.frontBackOffset - pinFront ) % geometry.frontBackModulus + 1

  print pinFront, pinBack, geometry.frontBackOffset, geometry.frontBackModulus

  x = point[ 1 ]
  y = point[ 2 ]

  locationFront = SerializableLocation( x, y, layerCalibration.zFront )
  locationBack  = SerializableLocation( x, y, layerCalibration.zBack  )

  layerCalibration.setPinLocation( "B" + str( pinFront ), locationFront ) # Switched B<->F mgb 231012
  layerCalibration.setPinLocation( "F" + str( pinBack  ), locationBack  )

layerCalibration.save( ".", outputFileName )
