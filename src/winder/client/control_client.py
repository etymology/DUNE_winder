from threading import Lock
from client_types import ClientTypes
from winder.Control.Library.UI_ClientConnection import UI_ClientConnection

class ControlClient( object ):
   def __init__( self, client_type, host, port ):
      self._connection_lock = Lock()
      self._set_client_type( client_type )
      self._set_host( host )
      self._set_port( port )
      self._set_client_connection( None )

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

   def _get_client_connection( self ):
      return self._client_conn

   def _set_client_connection( self, value ):
      self._client_conn = value

   _client_connection = property( fget = _get_client_connection )

   def send_message( self, message, suppress_exceptions = False ):
      """
      Sends a message to the control server.
      """

      return self.send_messages( [ message ] , suppress_exceptions )[ 0 ]

   def send_messages( self, messages, suppress_exceptions = False ):
      """
      Sends a message to the control server.
      """

      with self._connection_lock:
         if self._client_connection is None:
            self._set_client_connection( UI_ClientConnection( self.host, self.port, 1024 ) )

         result = []
         for message in messages:
            try:
               result.append( self._client_connection.get( message ) )
            except Exception, e:
               if not suppress_exceptions:
                  raise e

      return result
