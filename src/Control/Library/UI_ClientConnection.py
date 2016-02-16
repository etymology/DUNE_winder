#==============================================================================
# Name: UI_ClientConnection.py
# Uses: Socket interface to remote system.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================
import socket

class UI_ClientConnection:
  #---------------------------------------------------------------------
  def __init__( self, address, port, maxReceiveSize ) :
    """
    $$$DEBUG

    Returns:
      
    """

    self._connection = socket.socket()
    self._connection.connect( (address, port) )
    self._maxReceiveSize = maxReceiveSize

  #---------------------------------------------------------------------
  def get( self, command ) :
    """
    $$$DEBUG

    Returns:
      
    """

    self._connection.send( command )
    return self._connection.recv( self._maxReceiveSize )

  #---------------------------------------------------------------------
  def __call__( self, command ) :
    """
    $$$DEBUG

    Returns:
      
    """

    return self.get( command )