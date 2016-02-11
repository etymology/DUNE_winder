import re

def int_to_bytes( value ):
   if value < 0:
      raise ValueError( "Invalid value (%d): only non-negative integers can be converted." % value )
   else:
      hex_str = _strip_hex_prefix( hex( value ) )
      return _str_to_bytes( hex_str )

def int_to_chars( value ):
   byte_list = int_to_bytes( value )
   return map( lambda c: chr( c ), byte_list )

def str_as_char_list( s ):
   return [x for x in s]

def bytes_to_str( data_bytes ):
   chars = map( ord, data_bytes )
   return "".join( chars )

def bytes_to_hex_str( data_bytes ):
   hex_chars = map( _byte_to_character_digit, data_bytes )
   return "".join( hex_chars )

def _get_hex_value_re():
   pattern = r"\s*(?:0[xX])([0-9a-fA-F]+)\s*"
   return re.compile( pattern )

def _strip_hex_prefix( hex_str ):
   if hex_str is not None:
      match = _get_hex_value_re().match( hex_str )
      if len( match.groups() ) > 0:
         result = match.group( 1 )
      else:
         result = None
      return result
   else:
      raise ValueError( "Input hex-string cannot be None." )

def _character_digit_to_byte( char ):
   low_digit_value = ord( '0' )
   high_digit_value = ord( '9' )
   low_lower_value = ord( 'a' )
   high_lower_value = ord( 'f' )
   low_higher_value = ord( 'A' )
   high_higher_value = ord( 'F' )

   char_value = ord( char )

   if char_value >= low_digit_value and char_value <= high_digit_value:
      result = char_value - low_digit_value
   elif char_value >= low_lower_value and char_value <= high_lower_value:
      result = 10 + char_value - low_lower_value
   elif char_value >= low_higher_value and char_value <= high_higher_value:
      result = 10 + char_value - low_higher_value
   else:
      raise ValueError( "Character '%s' is not a hexadecimal character." % char )

   return result

def _byte_to_character_digit( digit ):
   if digit >= 10:
      char_base = 'a'
      digit -= 10
   else:
      char_base = '0'

   return chr( digit + ord( char_base ) )

def _str_to_bytes( s ):
   return map( _character_digit_to_byte, str_as_char_list( s ) )

def hex_str_to_int( hex_str ):
   """
   The input string is assumed to be lacking a hexadecimal prefix.
   """

   return int( "0x" + hex_str )

def bytes_to_int( data ):
   hex_str = bytes_to_hex_str( data )
   return hex_str_to_int( hex_str )

def str_to_int( s ):
   chars = str_as_char_list( s )

   result = 0
   for char in chars:
      result <<= 4
      result += ord( char )

   return result
