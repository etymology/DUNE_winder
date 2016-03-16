from .application_shared import AppShare

class Command( object ):
   def send_command( self, command ):
      return AppShare.instance().client_connection.send_message( command )

   def send_commands( self, commands ):
      return AppShare.instance().client_connection.send_messages( commands )
