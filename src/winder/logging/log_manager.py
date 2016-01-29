from threading import Lock
import csv
import os.path

class LogManager( object ):
   def __init__( self, time_manager, log_directory, machine_log_name = "machine messages.log", field_delimiter = ',', field_quote_character = '"' ):
      self._machine_log_field_delimiter = field_delimiter
      self._machine_log_quote_character = field_quote_character
      self._machine_log_lock = Lock()

      self._machine_log_file = None
      self._apa_log_file = None

      self._time_manager = time_manager
      self.log_directory = log_directory
      self.machine_log_filename = machine_log_name

   def add_message( self, message_source, message_type, message_description, message_data = None, operator_id = None, apa_id = None ):
      message_timestamp = self._time_manager.formatted_current_time_utc

      if message_data is None:
         message_data = ""
      if operator_id is None:
         operator_id = "<No operator>"
      if apa_id is None:
         apa_id = "<No APA>"

      with self._machine_log_lock:
         row = [ message_timestamp, str( apa_id ), str( message_source ), str( message_type ), str( message_description ), str( message_data ), str( operator_id ) ]
         self._machine_log.writerow( row )

   def get_messages( self ):
      raise NotImplementedError

   def get_messages_since( self, last_retrieved_message_id ):
      raise NotImplementedError

   def get_log_directory( self ):
      return self._log_directory

   def _set_log_directory( self, value ):
      if value is None:
         raise ValueError( "Log directory cannot be None." )
      else:
         name = os.path.normcase( os.path.normpath( value ) )
         if len( name ) == 0:
            raise ValueError( "Log directory name cannot be empty." )
         elif not os.path.isabs( name ):
            raise ValueError( "Log directory ('%s') must be an absolute reference." % name )
         elif not os.path.isdir( name ):
            raise ValueError( "Provided log directory ('%s') is not a directory." % name )
         else:
            self._log_directory = name

   log_directory = property( fget = get_log_directory, fset = _set_log_directory )

   def get_machine_log_filename( self ):
      return self._machine_log_filename

   def _set_machine_log_filename( self, value ):
      if value is None:
         raise ValueError( "Machine log filename cannot be None." )
      else:
         name = os.path.normcase( os.path.normpath( value ) )
         if len( name ) == 0:
            raise ValueError( "Machine log filename cannot be empty." )
         else:
            if not os.path.isabs( name ):
               name = os.path.join( self.log_directory, name )
            self._machine_log_filename = name

   machine_log_filename = property( fget = get_machine_log_filename, fset = _set_machine_log_filename )

   def _get_machine_log( self ):
      if self._machine_log_file is None:
         try:
            f = open( self.machine_log_filename, "a" )
         except Exception, e:
            raise IOError( "Unable to open machine log ('%s') for writing: %s" % ( self.machine_log_filename, str( e ) ) )
         else:
            self._machine_log_file = csv.writer( f, delimiter = self._machine_log_field_delimiter, quotechar = self._machine_log_quote_character, quoting = csv.QUOTE_MINIMAL )

      return self._machine_log_file

   def _set_machine_log( self, value ):
      self._machine_log_file = value

   _machine_log = property( fget = _get_machine_log, fset = _set_machine_log )

   def _get_time_manager( self ):
      return self._time_manager_instance

   def _set_time_manager( self, value ):
      if value is None:
         raise ValueError( "Time manager cannot be None." )
      else:
         self._time_manager_instance = value

   _time_manager = property( fget = _get_time_manager, fset = _set_time_manager )
