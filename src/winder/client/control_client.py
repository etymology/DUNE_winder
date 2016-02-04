from threading import Lock
import socket
from client_types import ClientTypes
from winder.utility.sockets import socket_file_readlines

class ControlClient( object ):
   def __init__( self, client_type, host, port ):
      self._connection_lock = Lock()
      self._set_client_type( client_type )
      self._set_host( host )
      self._set_port( port )
      self._set_socket( None )
      self._clear_internal_recordkeeping()

   def get_client_type( self ):
      return self._client_type

   def _set_client_type( self, value ):
      self._client_type = value

   client_type = property( fget = get_client_type )

   def get_is_remote_client( self ):
      return self.client_type is ClientTypes.Remote

   def get_is_console_client( self ):
      return self.client_type is ClientTypes.Console

   is_remote_client = property( fget = get_is_remote_client )

   is_console_client = property( fget = get_is_console_client )

   def get_host( self ):
      return self._host

   def _set_host( self, value ):
      self._host = value

   host = property( fget = get_host )

   def get_port( self ):
      return self._port

   def _set_port( self, value ):
      self._port = value

   port = property( fget = get_port )

   def _get_socket( self ):
      return self._sock

   def _set_socket( self, value ):
      self._sock = value

   _socket = property( fget = _get_socket, fset = _set_socket )

   def get_is_connected( self ):
      return self._is_connected

   def _set_is_connected( self, value ):
      self._is_connected = value

   is_connected = property( fget = get_is_connected )

   def get_connected_host( self ):
      return self._connected_host

   def _set_connected_host( self, value ):
      self._connected_host = value

   connected_host = property( fget = get_connected_host )

   def get_connected_port( self ):
      return self._connected_port

   def _set_connected_port( self, value ):
      self._connected_port = value

   connected_port = property( get_connected_port )

   def _clear_internal_recordkeeping( self ):
      self._set_connected_host( None )
      self._set_connected_port( None )
      self._set_is_connected( False )

   def _connect_to( self, host, port, suppress_exceptions = False ):
      if not self.is_connected:
         if self._socket is None:
            self._socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

         try:
            self._socket.connect( ( host, port ) )
         except Exception:
            self._clear_internal_recordkeeping()
         else:
            self._set_connected_host( host )
            self._set_connected_port( port )
            self._set_is_connected( True )

         result = self.is_connected
      elif not suppress_exceptions:
         raise RuntimeError( "Connection attempt aborted: client is already connected to a server." )
      else:
         result = False

      return result

   def _disconnect( self, socket_file, suppress_exceptions = False ):
      if self.is_connected:
         socket_file.close()
         self._set_socket( None )
         self._clear_internal_recordkeeping()

         result = True
      elif not suppress_exceptions:
         raise RuntimeError( "Disconnection attempt aborted: client is not connected to a server." )
      else:
         result = False

      return result

   def send_message( self, message, suppress_exceptions = False ):
      """
      Sends a message to the control server.

      Implementation Note: Each message is sent using a different socket. See https://stackoverflow.com/questions/29571770/python-socketserver-closes-tcp-connection-unexpectedly for why.
      """

      with self._connection_lock:
         if self._connect_to( self.host, self.port, suppress_exceptions ):
            try:
               socket_file = self._socket.makefile( "w+" )

               self._send_data( socket_file, message, suppress_exceptions )

               result = self._receive_response( socket_file, suppress_exceptions )
            finally:
               self._disconnect( socket_file, suppress_exceptions )

            return result
         elif not suppress_exceptions:
            raise RuntimeError( "Cannot sent message: client is not connected." )

   def _send_data( self, socket_file, data, suppress_exceptions = False ):
      try:
         socket_file.write( data + '\n' )
         socket_file.flush()
      except Exception, e:
         if not suppress_exceptions:
            raise RuntimeError( "Unable to send message: %s" % e )

   def _receive_response( self, socket_file, suppress_exceptions = False, reception_buffer_size = 1024 ):
      lines = socket_file_readlines( socket_file )
      result = map( lambda line: line.rstrip( "\r\n" ), lines )

      return result
