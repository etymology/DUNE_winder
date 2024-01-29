###############################################################################
# Name: SerializableLocation.py
# Uses: Serializable version of Location.
# Date: 2016-04-19
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from Library.Serializable import Serializable
from Library.Geometry.Location import Location

class SerializableLocation( Location, Serializable ) :

  #---------------------------------------------------------------------
  @staticmethod
  def fromLocation( location ) :
    result = SerializableLocation()
    result.x = location.x
    result.y = location.y
    result.z = location.z

    return result
