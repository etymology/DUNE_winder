###############################################################################
# Name: UI_ClientConnection.py
# Uses: Socket interface to remote system.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
###############################################################################
import socket

class UI_ClientConnection:
  #---------------------------------------------------------------------
  def __init__( self, address, port, maxReceiveSize ) :
    """
    Constructor.

    Args:
      address - Address of server.
      port - Port of server.
      maxReceiveSize - Largest packet that can be read.
    """

    self._connection = socket.socket()
    self._connection.connect( (address, port) )
    self._maxReceiveSize = maxReceiveSize

  #---------------------------------------------------------------------
  def get( self, command ) :
    """
    Fetch data from remote server.

    Args:
      command: A command to execute on remote server.

    Returns:
      The results of the command to remote server.
    """

    self._connection.send( command )
    return self._connection.recv( self._maxReceiveSize )

  #---------------------------------------------------------------------
  def __call__( self, command ) :
    """
    Emulating callable object is mapped to the "get" function.

    Args:
      command: A command to execute on remote server.

    Returns:
      The results of the command to remote server.
    """

    return self.get( command )