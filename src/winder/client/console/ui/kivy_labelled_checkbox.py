from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label

class LabelledCheckbox( BoxLayout ):
   def __init__( self, **kwargs ):
      kwargs[ "orientation" ] = "horizontal"
      super( LabelledCheckbox, self ).__init__( **kwargs )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.label = Label( **kwargs )
      self.checkbox = CheckBox( **kwargs )

      self.add_widget( self.label )
      self.add_widget( self.checkbox )

   def get_value( self ):
      return self.checkbox.active

   def set_value( self, value ):
      self.checkbox.active = value

   value = property( fget = get_value, fset = set_value )

   def get_text( self ):
      return self.label.text

   def set_text( self, value ):
      self.label.text = value

   text = property( fget = get_text, fset = set_text )
