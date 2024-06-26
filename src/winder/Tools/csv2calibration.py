from __future__ import absolute_import
from __future__ import print_function
import sys

sys.path.append( '../../../Control' )

from Machine.LayerCalibration import LayerCalibration
from Library.SerializableLocation import SerializableLocation
from Machine.X_LayerGeometry import X_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.G_LayerGeometry import G_LayerGeometry

if len( sys.argv ) != 4 :
  print("Syntax:")
  print("  csv2calibration <layer> <input CSV> <output XML>")
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

if layer == "G":
  geometry = G_LayerGeometry()
elif layer == "U":
  geometry = U_LayerGeometry()
elif layer == "V":
  geometry = V_LayerGeometry()
elif layer == "X":
  geometry = X_LayerGeometry()
else:
  raise f"Unknown layer: {str(layer)}"

layerCalibration = LayerCalibration( layer )

# Offset of 0,0 on the APA to machine offset.
layerCalibration.offset = SerializableLocation()

# Z-positions to level with front/back of pins.
layerCalibration.zFront = geometry.mostlyExtend
layerCalibration.zBack  = geometry.mostlyRetract

# For each point...
for point in points:
  pinFront = int( point[ 0 ] )
  pinBack  = ( 399 - pinFront ) % 2399 + 1
  x = point[ 1 ]
  y = point[ 2 ]

  locationFront = SerializableLocation( x, y, layerCalibration.zFront )
  locationBack  = SerializableLocation( x, y, layerCalibration.zBack  )

  layerCalibration.setPinLocation(f"F{pinFront}", locationFront)
  layerCalibration.setPinLocation(f"B{str(pinBack)}", locationBack)

layerCalibration.save( ".", outputFileName )
