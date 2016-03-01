###############################################################################
# Name: SystemTime.py
# Uses: Normal system time source.
# Date: 2016-02-12
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-12 - QUE - Creation.
###############################################################################

from Library.TimeSource import TimeSource
import datetime

class SystemTime( TimeSource ) :
  #-------------------------------------------------------------------
  def get( self ) :
    """
    Return the current time.

    Returns:
      Returns current time.
    """

    return datetime.datetime.utcnow()
