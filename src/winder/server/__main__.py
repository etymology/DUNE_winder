from __future__ import print_function

import os.path
import sys
from control_server import ControlServer

def get_log_directory():
   pwd = os.getcwd()
   result = os.path.abspath( os.path.join( pwd, "logs" ) )

   if not os.path.exists( result ):
      try:
         os.makedirs( result )
      except Exception, e:
         raise IOError( "Unable to create the log directory ('%s'): %s" % ( result, e ) )

   return result

if __name__ == "__main__":
   try:
      server = ControlServer( get_log_directory() )
   except Exception, e:
      print( "Error starting server: %s" % e, file = sys.stderr )
   else:
      if server.is_running:
         exit_command = "exit"

         print( "Control server is running." )
         print( "Enter '%s' to shutdown the server." % exit_command )

         value_entered = ""
         while value_entered.strip() != exit_command:
            try:
               value_entered = raw_input( "> " )
            except EOFError:
               value_entered = exit_command

         print( "Control server is shutdown." )
      else:
         print( "Unable to start server.", file = sys.stderr )
