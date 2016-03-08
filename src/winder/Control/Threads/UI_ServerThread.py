###############################################################################
# Name: UI_ServerThread.py
# Uses: User Interface server thread.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   The user interface server is a TCP socket that accepts commands and
#   dispatches these commands to a handler.  The handler processes the command
#   and returns results which are then sent back to the client.
###############################################################################
from PrimaryThread import PrimaryThread
from Control.Settings import Settings
import select
import socket
import threading     # For additional threads.

#------------------------------------------------------------------------------
# PrimaryThread to handle an individual connection from a client socket.
#------------------------------------------------------------------------------
class _Client( threading.Thread ):
  #---------------------------------------------------------------------
  def __init__( self, ( socket, address ), callback, log ):
    """
    Constructor.

    Args:
      socket: Connection to client.
      address: Address of client (ignored)
      callback: Function to send data from client. What the callback returns is then sent back to client.

    """


    threading.Thread.__init__( self )

    self._socket   = socket
    self._callback = callback
    self._log      = log
    self.start()

  #---------------------------------------------------------------------
  def run( self ):
    """
    Handle request from client.

    """
    ( address, port ) = self._socket.getpeername()

    self._log.add(
      self.__class__.__name__,
      "UI_CONNECT",
      "Connection from " + str( address ) + ":" + str( port ) + " established.",
      [ address, port ]
    )

    isRunning = True
    while isRunning :
      try:
        # Get the client request.
        data = self._socket.recv( Settings.SERVER_MAX_DATA_SIZE )
      except Exception :
        # If there was a problem it is probably because the socket was
        # closed.  Just shutdown the client thread.
        isRunning = False

      # Did we get anything?
      if isRunning and not '' == data :

        # Process the request.
        result = str( self._callback( data ) )

        # Send the results back to client.
        self._socket.send( str( result ) )
      else:
        # If there is no data, it is also an indication the socket was closed.
        isRunning = False

    # End the connection.
    self._socket.close()

    self._log.add(
      self.__class__.__name__,
      "UI_CONNECT",
      "Connection from " + str( address ) + ":" + str( port ) + " closed.",
      [ address, port ]
    )

# end class

#------------------------------------------------------------------------------
# User interface server thread.
#------------------------------------------------------------------------------
class UI_ServerThread( PrimaryThread ):
  #---------------------------------------------------------------------
  def __init__( self, commandCallback, log ):
    """
    Constructor.

    Args:
      callback: Function to send data from client.

    """

    PrimaryThread.__init__( self, "UI_ServerThread" )
    self._callback = commandCallback
    self._log = log

  #---------------------------------------------------------------------
  def run( self ):
    """
    Body of thread. Accepts client connections and swans threads to deal with client requests.

    """

    # Assume all is well.
    isError = False

    # Attempt to open a listening socket...
    try:
      server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      server.bind( ( '', Settings.SERVER_PORT ) )
      server.listen( Settings.SERVER_BACK_LOG )
    except socket.error:
      # Unable to open listening socket.
      isError = True
      if server:
        server.close()

    # If all went alright...
    if not isError :
      # While the system is running...
      while PrimaryThread.isRunning :

        # Wait for a connection, or 100 ms.
        inputReady, _, _ = \
          select.select( [ server ], [], [], 0.1 )

        # For all the results the unblocked...
        for readySource in inputReady:
          # Was the source our server getting a connection?
          if readySource == server:
            # Start a thread to deal with this client
            _Client( server.accept(), self._callback, self._log )
        # end for

      # end while

    # Close server socket.
    server.close()

# end class
