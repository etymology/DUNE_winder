class Theme( object ):
   def __init__( self, file_location, *args, **kwargs ):
      super( Theme, self ).__init__( *args, **kwargs )
      self._set_file_location( file_location )

   def _get_file_location( self ):
      return self._file_location

   def _set_file_location( self, value ):
      self._file_location = value

   file_location = property( fget = _get_file_location )

   def _has_file_location( self ):
      return self.file_location is not None

   has_file_location = property( fget = _has_file_location )
