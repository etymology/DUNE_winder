from winder.camera_management.camera_manager import CameraManager
from winder.logging.enumeration_value import EnumerationValue
from winder.logging.log_manager import LogManager
from winder.logging.log_sources import LogSources
from winder.time_management.time_manager import TimeManager

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

      self.is_running = start_server

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

if __name__ == "__main__":
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

   server = ControlServer( get_log_directory() )

   print( "Server is running?: %s" % server.is_running )
