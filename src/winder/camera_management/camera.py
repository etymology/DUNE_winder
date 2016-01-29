class Camera( object ):
   def __init__( self, identifier ):
      self.identifier = identifier

   def _get_identifier( self ):
      return self._identifier

   def _set_identifier( self, value ):
      self._identifier = value

   identifier = property( fget = _get_identifier, fset = _set_identifier )

   def get_image( self ):
      raise NotImplementedError
