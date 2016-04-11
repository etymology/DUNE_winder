from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from winder.utility.collections import DictOps

from .kivy_sparce_grid_layout import GridEntry
from .kivy_utilities import KivyUtilities
from .switch import WinderSwitch

class LabelledWinderSwitch( BoxLayout ):
   def __init__( self, **kwargs ):
      super( LabelledWinderSwitch, self ).__init__( **DictOps.dict_combine( kwargs, orientation = "horizontal", spacing = 10 ) )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self._label = Label( **kwargs )
      self._switch = WinderSwitch( **DictOps.dict_combine( kwargs, size_hint = [ .75, .75 ] ) )

      KivyUtilities.add_children_to_widget( self, [ self._label, self._switch ] )

   def _get_switch_state( self ):
      return self._switch.state

   def _set_switch_state( self, value ):
      self._switch.state = value

   state = property( fget = _get_switch_state, fset = _set_switch_state )

   def _get_label_text( self ):
      return self._label.text

   def _set_label_text( self, value ):
      self._label.text = value

   text = property( fget = _get_label_text, fset = _set_label_text )

class GridLabelledWinderSwitch( GridEntry, LabelledWinderSwitch ):
   pass
