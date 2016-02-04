from __future__ import print_function

from threading import Lock, Thread
import SocketServer
import sys

from winder.utility.enumeration_value import EnumerationValue
from winder.utility.sockets import socket_file_readlines

class ControlServerThread( Thread ):
   class States:
      NotStarted = EnumerationValue( 0 )
      Initializing = EnumerationValue( 1 )
      ReadyToRun = EnumerationValue( 2 )
      Running = EnumerationValue( 3 )
      Stopping = EnumerationValue( 4 )

   def __init__( self, control_server_instance, host, port, shutdown_poll_interval_seconds = 0.5, thread_name = "wcs_communication", is_daemon = True ):
      self._state_lock = Lock()
      self._set_current_state( ControlServerThread.States.Initializing )

      Thread.__init__( self )
      self.name = thread_name
      self.daemon = is_daemon

      self._set_control_server_instance( control_server_instance )

      self._initialize_communication_server( host, port, shutdown_poll_interval_seconds )

      self._set_current_state( ControlServerThread.States.ReadyToRun )

   def _initialize_communication_server( self, host, port, shutdown_poll_interval_seconds ):
      self._set_shutdown_poll_interval_seconds( shutdown_poll_interval_seconds )
      self._socket_server = SocketServer.ThreadingTCPServer( ( host, port ), ControlServerThread.SocketHandler )

   def get_control_server_instance( self ):
      return self._cs_instance

   def _set_control_server_instance( self, value ):
      if value is not None:
         self._cs_instance = value
      else:
         raise ValueError( "Control Server instance cannot be None." )

   control_server = property( fget = get_control_server_instance )

   def _get_socket_server( self ):
      return self._sock_server

   def _set_socket_server( self, value ):
      self._sock_server = value

   _socket_server = property( fget = _get_socket_server, fset = _set_socket_server )

   def get_current_state( self ):
      with self._state_lock:
         return self._current_thread_state

   def _set_current_state( self, value ):
      with self._state_lock:
         self._current_thread_state = value

   current_state = property( fget = get_current_state )

   def get_is_initializing( self ):
      return self.current_state is ControlServerThread.States.Initializing

   def get_is_ready_to_run( self ):
      return self.current_state is ControlServerThread.States.ReadyToRun

   def get_is_running( self ):
      return self.current_state is ControlServerThread.States.Running

   def get_is_stopping( self ):
      return self.current_state is ControlServerThread.States.Stopping

   is_initializing = property( fget = get_is_initializing )

   is_ready_to_run = property( fget = get_is_ready_to_run )

   is_running = property( fget = get_is_running )

   is_stopping = property( fget = get_is_stopping )

   def get_shutdown_poll_interval_seconds( self ):
      return self._shutdown_poll_interval_seconds

   def _set_shutdown_poll_interval_seconds( self, value ):
      self._shutdown_poll_interval_seconds = value

   shutdown_poll_interval_seconds = property( fget = get_shutdown_poll_interval_seconds )

   def start( self ):
      if self.is_ready_to_run:
         Thread.start( self )

      self._set_current_state( ControlServerThread.States.Running )
      return self.is_running

   def stop( self, suppress_exceptions = False ):
      if self.is_running:
         self._set_current_state( ControlServerThread.States.Stopping )
         self._socket_server.shutdown()
      elif not suppress_exceptions:
         raise RuntimeError( "Cannot stop: control_server thread is not running." )

   def run( self ):
      self._socket_server.serve_forever()

   class SocketHandler( SocketServer.StreamRequestHandler ):
      """
      See: https://docs.python.org/2/library/socketserver.html
      """

      def __init__( self, request, client_address, server ):
         SocketServer.StreamRequestHandler.__init__( self, request, client_address, server )

      def handle( self ):
         data = self._receive_request_data()

         response_data = "Echo Chamber:\r\n%s" % "\r\n".join( data )

         self._send_request_response( response_data )

      def _send_request_response( self, data ):
         self.wfile.write( data + '\n' )
         self.wfile.flush()

         print( "Response data sent: %s" % data )

      def _receive_request_data( self ):
         lines = socket_file_readlines( self.rfile )
         result = map( lambda line: line.rstrip( "\r\n" ), lines )

         return result

