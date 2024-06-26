###############################################################################
# Name: ControllogixPLC.py
# Uses: Functions for communicating to Allen-Bradley Controllogix PLC.
# Date: 2016-02-10
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#     The Controllogix PLC provides access to I/O through "tags".  Tags are
#   text names.  Communications to the PLC is done over an Ethernet connection
#   using Common Industrial Protocol (CIP) which specifies how tags are read
#   and written.  The library "pycomm" handles the CIP connection and this
#   class provides the I/O device.
###############################################################################

from .PLC import PLC
from pycomm3.logix_driver import LogixDriver as ClxDriver
import threading

class ControllogixPLC( PLC ) :
  #---------------------------------------------------------------------
  def initialize( self ) :
    """
    Try and establish a connection to the PLC.

    Returns:
      True if there was an error, False if connection was made.
    """
    self._lock.acquire()
    isFunctional = True
    try :
      # Attempt to open a connection to PLC.
      isOk = self._plcDriver.open()
      if not isOk :
        isFunctional = False
    except Exception:
      isFunctional = False

    self._isFunctional = isFunctional
    # if not self._isFunctional :
    #   self._plcDriver.clean_up()

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
  def read( self, tagName:str) :
    """
    Read a tag(s) from the PLC.

    Args:
      tag: A single or a list of PLC tags.

    Returns:
      Result of the data read, or None if there was a problem.
    """

    self._lock.acquire()
    if self._isFunctional :
      try :
        resultingTag = self._plcDriver.read( tagName )
        # if resultingTag.error:
          # print(f"While reading tag {tagName}, PLC threw error {resultingTag.error}")
      except Exception:
        # If tag reading threw an exception, the connection is dead.
        self._isFunctional = False

    self._lock.release()

    return resultingTag.value

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
        result = self._plcDriver.write( tag, data )
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
    PLC.__init__( self, "ControllogixPLC" )
    self._ipAddress = ipAddress
    self._plcDriver = ClxDriver(ipAddress)
    self._isFunctional = False
    self._lock = threading.Lock()
    self.initialize()

# end class
