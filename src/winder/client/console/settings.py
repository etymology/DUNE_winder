from ConfigParser import SafeConfigParser
import os.path
import sys
from .ui.theme.ui_theme_loader import UiThemeLoader

class ConfigurationFile:
   DefaultFilepath = "./configuration"

   class Sections:
      Client = "Client"
      Server = "Server"
      Ui = "UI"

   class Keys:
      ResourcePath = "resource_path"
      ServerAddress = "address"
      ServerListeningPort = "port"
      ThemeFile = "theme"

class Settings( object ):
   _execution_directory = None

   @staticmethod
   def get_execution_directory():
      if Settings._execution_directory is None:
         _execution_directory = os.path.dirname( os.path.normcase( os.path.normpath( sys.argv[ 0 ] ) ) )

      return _execution_directory

   def __init__( self, file_path = ConfigurationFile.DefaultFilepath, *args, **kwargs ):
      self._initialize( file_path )

   def _initialize( self, configuration_file_path ):
      self._load_configuration_file( configuration_file_path )
      self._load_resource_directory()
      self._load_theme_file()
      self._load_server_information()

   def _load_configuration_file( self, file_path ):
      if not os.path.isabs( file_path ):
         path = os.path.join( Settings.get_execution_directory(), file_path )
      else:
         path = file_path

      path = os.path.normcase( os.path.normpath( path ) )

      if os.path.exists( path ):
         conf = SafeConfigParser()
         conf.read( path )

         self._set_configuration_file( conf )
      else:
         raise IOError( "Configuration file '%s' does not exist." % path )

   def _load_resource_directory( self ):
      if self.configuration_file.has_option( ConfigurationFile.Sections.Client, ConfigurationFile.Keys.ResourcePath ):
         path = self.configuration_file.get( ConfigurationFile.Sections.Client, ConfigurationFile.Keys.ResourcePath )

         if not os.path.isabs( path ):
            path = os.path.normcase( os.path.normpath( os.path.join( Settings.get_execution_directory(), path ) ) )

         if os.path.exists( path ):
            if os.path.isdir( path ):
               self._set_resource_directory( path )
            else:
               raise ValueError( "Malformed configuration file: resource path '%s' is not a directory." % path )
         else:
            raise ValueError( "Malformed configuration file: resource path '%s' does not exist." % path )
      else:
         raise ValueError( "Malformed configuration file: missing the resource path." )

   def _load_theme_file( self ):
      if self.configuration_file.has_option( ConfigurationFile.Sections.Ui, ConfigurationFile.Keys.ThemeFile ):
         theme_file_name = self.configuration_file.get( ConfigurationFile.Sections.Ui, ConfigurationFile.Keys.ThemeFile )

         theme_file_path = os.path.normcase( os.path.normpath( os.path.join( self.theme_directory, theme_file_name ) ) )
         if os.path.exists( theme_file_path ):
            if os.path.isfile( theme_file_path ):
               loader = UiThemeLoader( theme_file_path, self.theme_directory )
               self._set_theme( loader.theme )
            else:
               raise ValueError( "Malformed configuration file: theme file path '%s' is not a file." % theme_file_path )
         else:
            raise ValueError( "Malformed configuration file: theme file path '%s' does not exist." % theme_file_path )
      else:
         raise ValueError( "Malformed configuration file: missing the theme file name." )

   def _load_server_information( self ):
      if self.configuration_file.has_option( ConfigurationFile.Sections.Server, ConfigurationFile.Keys.ServerAddress ):
         address = self.configuration_file.get( ConfigurationFile.Sections.Server, ConfigurationFile.Keys.ServerAddress )
         self._set_server_address( address )
      else:
         raise ValueError( "Malformed configuration file: server address is missing." )

      if self.configuration_file.has_option( ConfigurationFile.Sections.Server, ConfigurationFile.Keys.ServerListeningPort ):
         port = self.configuration_file.getint( ConfigurationFile.Sections.Server, ConfigurationFile.Keys.ServerListeningPort )
         self._set_server_listening_port( port )
      else:
         raise ValueError( "Malformed configuration file: server listening port is missing." )

   def _get_configuration_file( self ):
      return self._configuration_file

   def _set_configuration_file( self, value ):
      self._configuration_file = value

   configuration_file = property( fget = _get_configuration_file )

   def _get_resource_directory( self ):
      return self._resource_directory

   def _set_resource_directory( self, value ):
      self._resource_directory = value

   resource_directory = property( fget = _get_resource_directory )

   def _get_theme_directory( self ):
      return os.path.join( self.resource_directory, "themes" )

   theme_directory = property( fget = _get_theme_directory )

   def _get_theme_file_path( self ):
      return self._theme_file_path

   def _set_theme_file_path( self, value ):
      self._theme_file_path = value

   theme_file_path = property( fget = _get_theme_file_path )

   def _get_theme( self ):
      return self._theme

   def _set_theme( self, value ):
      self._theme = value

   theme = property( fget = _get_theme )

   def _get_server_address( self ):
      return self._server_address

   def _set_server_address( self, value ):
      self._server_address = value

   server_address = property( fget = _get_server_address )

   def _get_server_listening_port( self ):
      return self._server_listening_port

   def _set_server_listening_port( self, value ):
      self._server_listening_port = value

   server_listening_port = property( fget = _get_server_listening_port )
