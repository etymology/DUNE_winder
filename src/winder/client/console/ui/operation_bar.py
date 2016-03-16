from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class _SoftwareStopButton( Button ):
   def on_press( self ):
      print( "Software stop pressed." )

class OperationBar( BoxLayout ):
   def __init__( self, **kwargs ):
      super( OperationBar, self ).__init__( orientation = "horizontal", **kwargs )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      placeholder = Label( text = "Placeholder" )

      self.software_stop = _SoftwareStopButton( text = "Software stop" )

      self.add_widget( placeholder )
      self.add_widget( self.software_stop )
