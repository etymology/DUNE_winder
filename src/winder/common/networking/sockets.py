from .packet_payload import ProtocolVersionIds, PayloadFormats, format_payload_for_sending, read_payload_from_socket

def send_payload( target_socket, payload, payload_format = PayloadFormats.String, protocol_version_id = ProtocolVersionIds.Version_1_0 ):
   if target_socket is None:
      raise ValueError( "Socket to write to cannot be None." )
   elif protocol_version_id is None:
      raise ValueError( "Protocol ID cannot be None." )
   else:
      package_payload = format_payload_for_sending( payload, payload_format, protocol_version_id )
      package_payload_string = "".join( package_payload )

      target_socket.sendall( package_payload_string )

def read_payload( target_socket, chunk_size = 2048 ):
   return read_payload_from_socket( target_socket, chunk_size )[1]
