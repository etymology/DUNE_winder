class EnumerationValue( object ):
   def __init__( self, value, label = None ):
      self._set_value( value )
      self._set_label( label )

   def _get_value( self ):
      return self._value

   def _set_value( self, value ):
      self._value = value

   value = property( fget = _get_value )

   def _get_label( self ):
      return self._label

   def _set_label( self, value ):
      self._label = value

   label = property( fget = _get_label )

   def __eq__( self, other ):
      return self.value == other.value

   def __ne__( self, other ):
      return not self == other

   def __lt__( self, other ):
      return self.value < other.value

   def __gt__( self, other ):
      return other.value < self.value

   def __le__( self, other ):
      return not self > other

   def __ge__( self, other ):
      return not self < other

   def __neg__( self ):
      return EnumerationValue( ~self.value )

   def __or__( self, other ):
      return self._get_bitwise_result( self.value | other.value )

   def __and__( self, other ):
      return self._get_bitwise_result( self.value & other.value )

   def __xor__( self, other ):
      return self._get_bitwise_result( self.value ^ other.value )

   def _get_bitwise_result( self, new_value ):
      if self.value != new_value:
         result = EnumerationValue( new_value )
      else:
         result = self

      return result

   def __contains__( self, other ):
      return ( self.value | other.value ) != self.value

   def __int__( self ):
      return self.value

   def __str__( self ):
      if self.label is None:
         result = str( self.value )
      else:
         result = str( self.label )

      return result
