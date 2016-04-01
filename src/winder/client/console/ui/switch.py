from kivy.properties import OptionProperty

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_shape_widgets import EllipseWidget
from .kivy_sparce_grid_layout import GridEntry

class WinderSwitchStates:
   Error = -1
   Off = 0
   On = 1

class WinderSwitch( EllipseWidget ):
   class Keys:
      State = "state"

   state = OptionProperty( WinderSwitchStates.Off, options = [ WinderSwitchStates.Off, WinderSwitchStates.On, WinderSwitchStates.Error ] )

   def __init__( self, **kwargs ):
      self._construct_color_table()

      initial_state = DictOps.extract_optional_value( kwargs, WinderSwitch.Keys.State )

      self.bind( state = self._update_state )
      super( WinderSwitch, self ).__init__( **DictOps.dict_combine( kwargs, shape_size = [ .75, .75 ] ) )

      if initial_state is not None:
         self.state = initial_state

   def _construct_color_table( self ):
      self._color_tables = {}

      self._color_tables[ WinderSwitchStates.Off ] = [ 0, 0, 1 ]
      self._color_tables[ WinderSwitchStates.On ] = [ 0, 1, 0 ]
      self._color_tables[ WinderSwitchStates.Error] = [ 1, 0, 0 ]

   def _update_state( self, instance, value ):
      self.shape_color = self._color_tables[ self.state ]

class GridWinderSwitch( GridEntry, WinderSwitch ):
   pass
