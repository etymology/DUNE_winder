from winder.utility.data_transformation import str_as_char_list, str_to_int, int_to_chars, bytes_to_int
from winder.utility.enumeration_value import EnumerationValue

class PayloadFormats:
   Binary = EnumerationValue( 0, "Binary" )
   String = EnumerationValue( 1, "String" )

   @staticmethod
   def get_all_formats():
      return [ PayloadFormats.Binary, PayloadFormats.String ]

   @staticmethod
   def get_format( value, suppress_exceptions = False ):
      result = None

      for enum in PayloadFormats.get_all_formats():
         if int( enum ) == value:
            result = enum
            break

      if not suppress_exceptions and result is None:
         raise ValueError( "Value (%d) is not in the enumeration." )

      return result

class ProtocolVersionIds:
   Version_1_0 = EnumerationValue( 0, "v1.0" )

   _version_values = None

   @staticmethod
   def get_version_values():
      if ProtocolVersionIds._version_values is None or len( ProtocolVersionIds._version_values ) == 0:
         ProtocolVersionIds._version_values = { ProtocolVersionIds.Version_1_0 : 0x08 }

      return ProtocolVersionIds._version_values

   @staticmethod
   def get_protocol_version_id( version_value ):
      result = None

      keys = ProtocolVersionIds.get_version_values().keys()
      for key in keys:
         if ProtocolVersionIds.get_version_values()[key] == version_value:
            result = key
            break

      return result

   _sending_formatters = None

   @staticmethod
   def get_sending_formatters():
      if ProtocolVersionIds._sending_formatters is None or len( ProtocolVersionIds._sending_formatters ) == 0:
         ProtocolVersionIds._sending_formatters = { ProtocolVersionIds.Version_1_0 : _format_payload_for_sending_proto_10 }

      return ProtocolVersionIds._sending_formatters

   _socket_readers = None

   @staticmethod
   def get_socket_readers():
      if ProtocolVersionIds._socket_readers is None:
         ProtocolVersionIds._socket_readers = { ProtocolVersionIds.Version_1_0 : _read_payload_from_socket_proto_10 }

      return ProtocolVersionIds._socket_readers

def format_payload_for_sending( data = None, data_format = PayloadFormats.Binary, protocol_version_id = ProtocolVersionIds.Version_1_0 ):
   """
   Returns: list of characters
   """

   if protocol_version_id is ProtocolVersionIds.Version_1_0:
      result = ProtocolVersionIds.get_sending_formatters()[protocol_version_id]( data, data_format, protocol_version_id )
   else:
      raise ValueError( "Protocol version (%s) is not supported." % protocol_version_id )

   return result

def _format_payload_for_sending_proto_10( data, data_format, protocol_version_id ):
   """
   Format: <protocol version ID : 1-byte><data package length length : 1-byte><data package length : <data package length length> bytes><data format : 1-byte><data>

   Returns: list of characters
   """

   if data is None:
      data = []

   result = int_to_chars( ProtocolVersionIds.get_version_values()[ protocol_version_id ] )

   payload_format_width = 1

   data_length = len( data )

   if data_length > 0:
      data_package_length_field = int_to_chars( data_length + payload_format_width )

      result.extend( int_to_chars( len( data_package_length_field ) ) )
      result.extend( data_package_length_field )
      result.extend( int_to_chars( int( data_format ) ) )

      if data_format is PayloadFormats.String:
         data = str_as_char_list( data )
      elif data_format is not PayloadFormats.Binary:
         raise ValueError( "Data format (%s) is not supported." % data_format )

      result.extend( data )
   else:
      result.extend( int_to_chars( data_length ) )

   return result

def read_payload_from_socket( target_socket, chunk_size = 2048 ):
   """
   Returns:
   Tuple of:
      1. protocol version ID
      2. packet payload (as a string)
   """

   if target_socket is None:
      raise ValueError( "Socket to read from cannot be None." )
   elif chunk_size <= 0:
      raise ValueError( "Chunk size (%d) must be positive." % chunk_size )
   else:
      protocol_version_id_value = str_to_int( _read_from_socket( target_socket, 1, chunk_size ) )
      protocol_version_id = ProtocolVersionIds.get_protocol_version_id( protocol_version_id_value )

      if protocol_version_id is None:
         raise IOError( "Protocol version ID (%d) is not supported." )
      else:
         payload = ProtocolVersionIds.get_socket_readers()[ protocol_version_id ]( target_socket, chunk_size )

      result = ( protocol_version_id, payload )

      return result

def _read_payload_from_socket_proto_10( target_socket, chunk_size ):
   """
   Format: <protocol version ID : 1-byte><data package length length : 1-byte><data package length : <data package length length> bytes><data format : 1-byte><data>

   Returns:
   Tuple of:
      1. protocol version ID
      2. packet payload (as a string)
   """

   data_package_length_length = str_to_int( _read_from_socket( target_socket, 1, chunk_size ) )

   if data_package_length_length > 0:
      payload_format_value_width = 1

      data_package_length = str_to_int( _read_from_socket( target_socket, data_package_length_length, chunk_size ) )
      data_length = data_package_length - payload_format_value_width

      payload_format_value = str_to_int( _read_from_socket( target_socket, payload_format_value_width, chunk_size ) )
      raw_payload_data = _read_from_socket( target_socket, data_length, chunk_size )

      payload_format = PayloadFormats.get_format( payload_format_value )

      if payload_format is PayloadFormats.Binary:
         result = bytes_to_int( raw_payload_data )
      elif payload_format is PayloadFormats.String:
         result = raw_payload_data
      else:
         raise ValueError( "Data format (%s) is not supported." % payload_format )
   else:
      result = []

   return result

def _read_from_socket( target_socket, data_amount, chunk_size ):
   if target_socket is None:
      raise ValueError( "Socket to read from cannot be None." )
   elif data_amount < 0:
      raise ValueError( "Cannot read negative data amount (%d) from socket." % data_amount )
   elif chunk_size <= 0:
      raise ValueError( "Chunk size (%d) must be positive." % chunk_size )
   else:
      data_pieces = []
      data_quantity_read = 0

      while data_quantity_read < data_amount:
         data_remaining = data_amount - data_quantity_read
         if data_remaining >= chunk_size:
            piece_size = chunk_size
         else:
            piece_size = data_remaining

         data_piece = target_socket.recv( piece_size )

         data_pieces.append( data_piece )
         data_quantity_read += len( data_piece )

      result = "".join( data_pieces )

      return result
