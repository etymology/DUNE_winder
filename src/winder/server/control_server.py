from __future__ import print_function

from control_server_thread import ControlServerThread

from winder.camera_management.camera_manager import CameraManager
from winder.logging.log_manager import LogManager
from winder.logging.log_sources import LogSources
from winder.time_management.time_manager import TimeManager
from winder.utility.enumeration_value import EnumerationValue

class ControlServer( object ):
   class LogMessageTypes:
      Debug = EnumerationValue( 0 )
      Information = EnumerationValue( 1 )
      Warning = EnumerationValue( 2 )
      Error = EnumerationValue( 3 )

   def __init__( self, logging_directory, start_server = True ):
      self.is_running = False
      self._initialize( start_server, logging_directory )

   def _initialize( self, start_server, logging_directory ):
      self.time_manager = TimeManager()
      self.log_manager = LogManager( self.time_manager, logging_directory )
      self._initialize_camera_manager()

      self._initialize_server_communication( start_server )

   def _initialize_camera_manager( self ):
      try:
         self.camera_manager = CameraManager()
      except Exception, e:
         message = "Error initializing camera manager: %s" % e
         message_type = ControlServer.LogMessageTypes.Error
      else:
         message = "Camera manager initialized."
         message_type = ControlServer.LogMessageTypes.Information
      finally:
         self.log_manager.add_message( LogSources.MasterServer, message_type, message )

   def _initialize_server_communication( self, start_listening, host = "localhost", port = 35023, shutdown_poll_interval_seconds = 0.5 ):
      self._socket_server_thread = ControlServerThread( self, host, port, shutdown_poll_interval_seconds )

      if start_listening:
         self.start()

   def _get_is_running( self ):
      return self._is_running

   def _set_is_running( self, value ):
      self._is_running = value

   is_running = property( fget = _get_is_running, fset = _set_is_running )

   def _get_time_manager( self ):
      return self._time_manager

   def _set_time_manager( self, value ):
      self._time_manager = value

   time_manager = property( fget = _get_time_manager, fset = _set_time_manager )

   def _get_log_manager( self ):
      return self._log_manager

   def _set_log_manager( self, value ):
      self._log_manager = value

   log_manager = property( fget = _get_log_manager, fset = _set_log_manager )

   def _get_camera_manager( self ):
      return self._camera_manager

   def _set_camera_manager( self, value ):
      self._camera_manager = value

   camera_manager = property( fget = _get_camera_manager, fset = _set_camera_manager )

   def _get_socket_server_thread( self ):
      return self._ss_thread

   def _set_socket_server_thread( self, value ):
      self._ss_thread = value

   _socket_server_thread = property( fget = _get_socket_server_thread, fset = _set_socket_server_thread )

   def start( self ):
      if not self.is_running:
         self.is_running = self._socket_server_thread.start()
      else:
         raise RuntimeError( "Cannot start control server: server is already running." )

   def stop( self, suppress_exceptions = False ):
      if self.is_running:
         self._socket_server_thread.stop( suppress_exceptions )
         self._socket_server_thread.join()
         self.is_running = self._socket_server_thread.is_running
      elif not suppress_exceptions:
         raise RuntimeError( "Cannot stop control system server: server is not running." )

if __name__ == "__main__":
   import sys

   def get_log_directory():
      import os
      import os.path

      pwd = os.getcwd()
      result = os.path.abspath( os.path.join( pwd, "logs" ) )

      if not os.path.exists( result ):
         try:
            os.makedirs( result )
         except Exception, e:
            raise IOError( "Unable to create the log directory ('%s'): %s" % ( result, e ) )

      return result

   try:
      server = ControlServer( get_log_directory() )
   except Exception, e:
      print( "Error starting server: %s" % e, file = sys.stderr )
   else:
      if server.is_running:
         exit_command = "exit"

         print( "Server is running." )
         print( "Enter '%s' to shutdown the server." % exit_command )

         value_entered = ""
         while value_entered.strip() != exit_command:
            try:
               value_entered = raw_input( "> " )
            except EOFError:
               value_entered = exit_command

         print( "Server is shutdown." )
      else:
         print( "Unable to start server.", file = sys.stderr )
