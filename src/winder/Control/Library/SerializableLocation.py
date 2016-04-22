###############################################################################
# Name: SerializableLocation.py
# Uses: Serializable version of Location.
# Date: 2016-04-19
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Serializable import Serializable
from Library.Geometry.Location import Location

class SerializableLocation( Location, Serializable ) :
  pass