###############################################################################
# Name: MachineCalibration.py
# Uses: Calibration for machine excluding APA.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.HashedSerializable import HashedSerializable
#from Library.Geometry.Location import Location
from Library.SerializableLocation import SerializableLocation

class MachineCalibration( HashedSerializable ) :
  """
  """

  TOP_NODE_NAME = "MachineCalibration"

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    HashedSerializable.__init__( self )

    # Location of the park position.  Instance of Location.
    self._park = SerializableLocation()

    # Location for loading/unloading the spool.
    self._spoolLoad = SerializableLocation()

    # Locations of the transfer areas.  Single number.
    # NOTE: The left/right transfer areas can transfer from the bottom and up
    # until some height not the top.  Hence a second number for this limit.
    self._transferLeft     = None
    self._transferLeftTop  = None
    self._transferTop      = None
    self._transferRightTop = None
    self._transferBottom   = None

    # Locations of the end-of-travels.  Single number.
    self._limitLeft   = None
    self._limitTop    = None
    self._limitRight  = None
    self._limitBottom = None

    # Location of Z-axis when fully extended, and fully retracted.  Single number.
    self._zFront       = None
    self._zRear        = None

    # End-of-travels for Z-axis.  Single number.
    self._zLimitFront  = None
    self._zLimitRear   = None


  #---------------------------------------------------------------------
  def serialize( self, xmlDocument ) :
    """
    Turn this object into an XML node.

    Args:
      xmlDocument: Instance of xml.dom.minidom.Document.

    Returns:
      Must return an XML node with the data from this object.
    """
    node = xmlDocument.createElement( self.TOP_NODE_NAME )

    self.add( "park",             xmlDocument, node, self._park             )
    self.add( "spoolLoad",        xmlDocument, node, self._spoolLoad        )
    self.add( "transferLeft",     xmlDocument, node, self._transferLeft     )
    self.add( "transferLeftTop",  xmlDocument, node, self._transferLeftTop  )
    self.add( "transferTop",      xmlDocument, node, self._transferTop      )
    self.add( "transferRightTop", xmlDocument, node, self._transferRightTop )
    self.add( "transferBottom",   xmlDocument, node, self._transferBottom   )
    self.add( "limitLeft",        xmlDocument, node, self._limitLeft        )
    self.add( "limitTop",         xmlDocument, node, self._limitTop         )
    self.add( "limitRight",       xmlDocument, node, self._limitRight       )
    self.add( "limitBottom",      xmlDocument, node, self._limitBottom      )
    self.add( "zFront",           xmlDocument, node, self._zFront           )
    self.add( "zRear",            xmlDocument, node, self._zRear            )
    self.add( "zLimitFront",      xmlDocument, node, self._zLimitFront      )
    self.add( "zLimitRear",       xmlDocument, node, self._zLimitRear       )

    #self.serializeLocation( "Park", xmlDocument, node, self._park )
    #self.serializeLocation( "SpoolLoad", xmlDocument, node, self._spoolLoad )

    #self.serializeFloat( "transferLeft",     xmlDocument, node, self._transferLeft     )
    #self.serializeFloat( "transferLeftTop",  xmlDocument, node, self._transferLeftTop  )
    #self.serializeFloat( "transferTop",      xmlDocument, node, self._transferTop      )
    #self.serializeFloat( "transferRightTop", xmlDocument, node, self._transferRightTop )
    #self.serializeFloat( "transferBottom",   xmlDocument, node, self._transferBottom   )
    #self.serializeFloat( "limitLeft",        xmlDocument, node, self._limitLeft        )
    #self.serializeFloat( "limitTop",         xmlDocument, node, self._limitTop         )
    #self.serializeFloat( "limitRight",       xmlDocument, node, self._limitRight       )
    #self.serializeFloat( "limitBottom",      xmlDocument, node, self._limitBottom      )
    #self.serializeFloat( "zFront",           xmlDocument, node, self._zFront           )
    #self.serializeFloat( "zRear",            xmlDocument, node, self._zRear            )
    #self.serializeFloat( "zLimitFront",      xmlDocument, node, self._zLimitFront      )
    #self.serializeFloat( "zLimitRear",       xmlDocument, node, self._zLimitRear       )

    return node

  #---------------------------------------------------------------------
  def unserialize( self, node ) :
    """
    Take an XML node and load values into this object.

    Args:
      node: Instance of xml.dom.minidom.Node.

    Returns:
      True if there was an error, False if not.
    """

    #calibrationNode = node.getElementsByTagName( self.TOP_NODE_NAME )

    self._park.unserializeNode( "park", node )
    #self._park = self.unserializeLocation( "Park", node )
    #self._spoolLoad = self.unserializeLocation( "SpoolLoad", node )

    self._transferLeft     = self.unserializeFloat( "transferLeft",     node )
    self._transferLeftTop  = self.unserializeFloat( "transferLeftTop",  node )
    self._transferTop      = self.unserializeFloat( "transferTop",      node )
    self._transferRightTop = self.unserializeFloat( "transferRightTop", node )
    self._transferBottom   = self.unserializeFloat( "transferBottom",   node )
    self._limitLeft        = self.unserializeFloat( "limitLeft",        node )
    self._limitTop         = self.unserializeFloat( "limitTop",         node )
    self._limitRight       = self.unserializeFloat( "limitRight",       node )
    self._limitBottom      = self.unserializeFloat( "limitBottom",      node )
    self._zFront           = self.unserializeFloat( "zFront",           node )
    self._zRear            = self.unserializeFloat( "zRear",            node )
    self._zLimitFront      = self.unserializeFloat( "zLimitFront",      node )
    self._zLimitRear       = self.unserializeFloat( "zLimitRear",       node )

  #-------------------------------------------------------------------
  @staticmethod
  def load( filePath, fileName ) :
    """
    Load a calibration file and return instance.

    Args:
      filePath: Directory of file.
      fileName: File name to load.

    Returns:
      Instance of Calibration.
    """

    return HashedSerializable.load( filePath, fileName, MachineCalibration )


if __name__ == "__main__":
  machineCalibration = MachineCalibration()

  machineCalibration._park = SerializableLocation( 1, 2 )
  machineCalibration._spoolLoad = SerializableLocation( 3, 4 )
  machineCalibration._transferLeft     = 1
  machineCalibration._transferLeftTop  = 2
  machineCalibration._transferTop      = 3
  machineCalibration._transferRightTop = 4
  machineCalibration._transferBottom   = 5

  machineCalibration._limitLeft   = 6
  machineCalibration._limitTop    = 7
  machineCalibration._limitRight  = 8
  machineCalibration._limitBottom = 9

  machineCalibration._zFront       = 10
  machineCalibration._zRear        = 11

  machineCalibration._zLimitFront  = 12
  machineCalibration._zLimitRear   = 13

  machineCalibration.save( ".", "machineCalibrationTest.xml" )

  machineCalibration = MachineCalibration.load( ".", "machineCalibrationTest.xml" )


  print machineCalibration._park
  print machineCalibration._spoolLoad
  print machineCalibration._transferLeft
  print machineCalibration._transferLeftTop
  print machineCalibration._transferTop
  print machineCalibration._transferRightTop
  print machineCalibration._transferBottom

  print machineCalibration._limitLeft
  print machineCalibration._limitTop
  print machineCalibration._limitRight
  print machineCalibration._limitBottom

  print machineCalibration._zFront
  print machineCalibration._zRear

  print machineCalibration._zLimitFront
  print machineCalibration._zLimitRear
