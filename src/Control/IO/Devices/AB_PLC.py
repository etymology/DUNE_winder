#==============================================================================
# Name: AB_PLC.py
# Uses: Functions for communicating to Allen-Bradley Controllogix PLC.
# Date: 2016-02-10
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-10 - QUE - Creation.
# Notes:
#     The Controllogix PLC provides access to I/O through "tags".  Tags are
#   text names.  Communications to the PLC is done over an Ethernet connection
#   using Common Industrial Protocol (CIP) which specifies how tags are read
#   and written.  The library "pycomm" handles the CIP connection and this
#   class provides the I/O device.
#==============================================================================

from IO_Device import IO_Device
from pycomm.ab_comm.clx import Driver as ClxDriver
import threading

class AB_PLC( IO_Device ) :
  #---------------------------------------------------------------------
  def initialize( self ) :
    """
    Try and establish a connection to the PLC.

    Returns:
      True if there was an error, False if connection was made.
    """
    self._lock.acquire()
    self._isFunctional = True
    try :
      #self._plc.close()

      # Attempt to open a connection to PLC.
      isOk = self._plc.open( self._ipAddress )
      if not isOk :
        self._isFunctional = False
    except Exception:
      self._isFunctional = False

    if not self._isFunctional :
      self._plc.clean_up()

    self._lock.release()

    return self._isFunctional

  #---------------------------------------------------------------------
  def isNotFunctional( self ) :
    """
    See if the PLC is communicating correctly.

    Returns:
      True there is a problem with hardware, false if not.
    """
    return not self._isFunctional

  #---------------------------------------------------------------------
  def read( self, tag ) :
    """
    Read a tag(s) from the PLC.

    Args:
      tag: A single or a list of PLC tags.

    Returns:
      Result of the data read, or None if there was a problem.
    """

    self._lock.acquire()
    result = None
    if self._isFunctional :
      try :
        result = self._plc.read_tag( tag )
      except Exception:
        # $$$DEBUG print "Unable to read", tag, self._isFunctional

        # If tag reading threw an exception, the connection is dead.
        self._isFunctional = False

    self._lock.release()

    return result

  #---------------------------------------------------------------------
  def write( self, tag, data=None, typeName=None ) :
    """
    Write a tag(s) to the PLC.

    Args:
      tag: A single or a list of PLC tags.
      data: Data to be written.
      typeName: Type of the tag to write.

    Returns:
        None is returned in case of error otherwise the tag list is returned.
    """

    self._lock.acquire()
    result = None
    if self._isFunctional :
      try :
        result = self._plc.write_tag( tag, data, typeName )
      except Exception:
        # If tag reading threw an exception, the connection is dead.
        self._isFunctional = False

    self._lock.release()
    return result

  #---------------------------------------------------------------------
  def __init__( self, ipAddress ) :
    """
    Constructor.

    Args:
      ipAddress: IP address of PLC to communicate with.
    """
    IO_Device.__init__( self, "ControllogixPLC" )
    self._ipAddress = ipAddress
    self._plc = ClxDriver()
    self._isFunctional = False
    self._lock = threading.Lock()
    self.initialize()

# end class
