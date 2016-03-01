from ..clients import ConsoleControlClient
from .settings import Settings


class AppShare( object ):
   _instance = None

   @staticmethod
   def instance():
      if AppShare._instance is None:
         AppShare._instance = AppShare()

      return AppShare._instance

   def __init__( self ):
      self.clear()

   def clear( self ):
      self._set_settings( None )
      self._set_client_connection( None )

   def _get_settings( self ):
      if self._settings is None:
         self._set_settings( Settings() )

      return self._settings

   def _set_settings( self, value ):
      self._settings = value

   settings = property( fget = _get_settings )

   def _get_client_connection( self ):
      if self._client_connection is None:
         self._set_client_connection( ConsoleControlClient( self.settings.server_address, self.settings.server_listening_port ) )

      return self._client_connection

   def _set_client_connection( self, value ):
      self._client_connection = value

   client_connection = property( fget = _get_client_connection )
