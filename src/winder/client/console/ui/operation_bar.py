from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from ..command import Command
from .kivy_utilities import KivyUtilities

class SoftwareStopCommand( Command ):
   def stop( self ):
      command = "process.stop()"
      self.send_command( command )

class _SoftwareStopButton( Button ):
   def __init__( self, **kwargs ):
      super( _SoftwareStopButton, self ).__init__( **kwargs )

      self.command = SoftwareStopCommand()

   def on_press( self ):
      self.command.stop()

class OperationBar( BoxLayout ):
   def __init__( self, **kwargs ):
      super( OperationBar, self ).__init__( orientation = "horizontal", **kwargs )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      placeholder = Label( text = "Placeholder" )

      self.software_stop = _SoftwareStopButton( text = "Software stop" )

      KivyUtilities.add_children_to_widget( self, [ self.software_stop, placeholder ] )
