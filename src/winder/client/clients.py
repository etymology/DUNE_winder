from client_types import ClientTypes
from control_client import ControlClient

class ConsoleControlClient( ControlClient ):
   def __init__( self, host, port ):
      ControlClient.__init__( self, ClientTypes.Console, host, port )

class RemoteControlClient( ControlClient ):
   def __init__( self, host, port ):
      ControlClient.__init__( self, ClientTypes.Remote, host, port )
