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

   def _get_settings( self ):
      if self._settings is None:
         self._set_settings( Settings() )

      return self._settings

   def _set_settings( self, value ):
      self._settings = value

   settings = property( fget = _get_settings )
