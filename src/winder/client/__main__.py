from __future__ import print_function

import argparse
import sys

from clients import ConsoleControlClient, RemoteControlClient

def _process_client_type( client_type ):
   return str( client_type ).lower().strip()

def _create_argument_parser():
   result = argparse.ArgumentParser( description = "runs a control client" )

   result.add_argument( "-t", "--client-type", type = _process_client_type, help = "client type" )

   group = result.add_mutually_exclusive_group()
   group.add_argument( "-d", "--data", type = str, help = "data to send" )
   group.add_argument( "-i", "--interactive", action = "store_true", default = False, help = "run interactive shell" )

   return result

def main( args = None ):
   if args is None:
      args = []

   result = 0

   parser = _create_argument_parser()
   arguments = parser.parse_args( args )

   host = "localhost"
   port = 35023

   if arguments.client_type == "console":
      client = ConsoleControlClient( host, port )
   elif arguments.client_type == "remote":
      client = RemoteControlClient( host, port )
   else:
      if arguments.client_type is None:
         error_message = "No client type provided"
      else:
         error_message = "Invalid client type ('%s')" % arguments.client_type
      error_message += "; needs to be one of: console, remote"
      print( error_message, file = sys.stderr )

      result = 1

   if result == 0:
      if arguments.interactive:
         exit_command = "exit"
         shell_prompt = "> "

         if client.is_console_client:
            client_mode = "Console"
         elif client.is_remote_client:
            client_mode = "Remote"

         print( "%s client: Interactive mode." % client_mode )
         print( "Enter '%s' to exit." % exit_command )

         while True:
            input_line = raw_input( shell_prompt )

            if input_line == exit_command:
               break
            else:
               _send_message_to( client, input_line )
      elif len( arguments.data ) > 0:
         _send_message_to( client, arguments.data )

   return result

def _send_message_to( client, data ):
   try:
      response = client.send_message( data )
   except RuntimeError, e:
      print( "Unable to send message: %s" % e, file = sys.stderr )
   else:
      print( response )

if __name__ == "__main__":
   args = sys.argv[ 1: ]
   sys.exit( main( args ) )
