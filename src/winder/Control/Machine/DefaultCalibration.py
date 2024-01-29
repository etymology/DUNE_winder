###############################################################################
# Name: DefaultCalibration.py
# Uses: Generate a default calibration file for layer based on nominal geometry.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from __future__ import absolute_import
import os

from Library.Geometry.Location import Location
from Library.SerializableLocation import SerializableLocation

from Machine.LayerCalibration import LayerCalibration
from Machine.MachineCalibration import MachineCalibration
from Machine.UV_LayerGeometry import UV_LayerGeometry
from Machine.X_LayerGeometry import X_LayerGeometry
from Machine.V_LayerGeometry import V_LayerGeometry
from Machine.U_LayerGeometry import U_LayerGeometry
from Machine.G_LayerGeometry import G_LayerGeometry

from RecipeGenerator.LayerX_Recipe import LayerX_Recipe
from RecipeGenerator.LayerV_Recipe import LayerV_Recipe
from RecipeGenerator.LayerU_Recipe import LayerU_Recipe
from RecipeGenerator.LayerG_Recipe import LayerG_Recipe

class DefaultMachineCalibration( MachineCalibration ) :

  #---------------------------------------------------------------------
  def __init__( self, outputFilePath=None, outputFileName=None ) :
    """
    Constructor.

    Args:
      outputFilePath - Path to save/load data.
      outputFileName - Name of data file.
    """
    MachineCalibration.__init__( self, outputFilePath, outputFileName )
    geometry = UV_LayerGeometry()

    # Location of the park position.
    self.parkX = 0
    self.parkY = 0

    # Location for loading/unloading the spool.
    self.spoolLoadX = 0
    self.spoolLoadY = 0

    self.transferLeft     = geometry.left
    self.transferLeftTop  = geometry.top / 2
    self.transferTop      = geometry.top
    self.transferRight    = geometry.right
    self.transferRightTop = geometry.top / 2
    self.transferBottom   = geometry.bottom

    self.limitLeft        = geometry.limitLeft
    self.limitTop         = geometry.limitTop
    self.limitRight       = geometry.limitRight
    self.limitBottom      = geometry.limitBottom
    self.zFront           = 0
    self.zBack            = geometry.zTravel
    self.zLimitFront      = geometry.limitRetracted
    self.zLimitRear       = geometry.limitExtended
    self.headArmLength    = geometry.headArmLength
    self.headRollerRadius = geometry.headRollerRadius
    self.headRollerGap    = geometry.headRollerGap
    self.pinDiameter      = geometry.pinDiameter

    if outputFilePath and outputFileName :
      # If there isn't a calibration file, create it.  Otherwise, load what
      # has already been saved.
      if not os.path.isfile( outputFilePath + "/" + outputFileName ) :
        self.save()
      else :
        self.load()

class DefaultLayerCalibration( LayerCalibration ) :

  #---------------------------------------------------------------------
  def __init__( self, outputFilePath, outputFileName, layerName ) :
    """
    Export node list to calibration file.  Debug function.

    Args:
      outputFileName: File name to create.
      layerName: Name of recipe.
    """

    if "X" == layerName :
      geometry = X_LayerGeometry()
      recipe = LayerX_Recipe( geometry )
    elif "V" == layerName :
      geometry = V_LayerGeometry()
      recipe = LayerV_Recipe( geometry )
    elif "U" == layerName :
      geometry = U_LayerGeometry()
      recipe = LayerU_Recipe( geometry )
    elif "G" == layerName :
      geometry = G_LayerGeometry()
      recipe = LayerG_Recipe( geometry )
    else :
      raise "Unknown layer: " + str( layerName )

    LayerCalibration.__init__( self, layerName )
    self.offset = geometry.apaLocation.add( geometry.apaOffset )
    self.offset = SerializableLocation.fromLocation( self.offset )
    self.zFront = geometry.mostlyRetract
    self.zBack  = geometry.mostlyExtend

    for node in recipe.nodes :
      location = recipe.nodes[ node ]
      newLocation = SerializableLocation( location.x, location.y, location.z )
      self.setPinLocation( node, newLocation )

    if outputFilePath and outputFileName :
      self.save( outputFilePath, outputFileName, "LayerCalibration" )

# end class

if __name__ == "__main__":
  DefaultMachineCalibration( ".", "MachineCalibration.xml" )
  DefaultLayerCalibration( ".", "X_Calibration.xml", "X" )
  DefaultLayerCalibration( ".", "V_Calibration.xml", "V" )
  DefaultLayerCalibration( ".", "U_Calibration.xml", "U" )
  DefaultLayerCalibration( ".", "G_Calibration.xml", "G" )
