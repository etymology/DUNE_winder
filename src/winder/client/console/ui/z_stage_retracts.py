from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .kivy_sparce_grid_layout import SparseGridLayout, GridLabel, GridCheckbox, GridEntry

class ZStageRetracts( SparseGridLayout, BackgroundColorMixin ):
   def __init__( self, **kwargs ):
      super( ZStageRetracts, self ).__init__( **DictOps.dict_combine( kwargs, rows = 3, columns = 3 ) )

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

      self.sw1_closed = False
      self.sw2_closed = False

   def _construct( self, **kwargs ):
      self.bg_color = AppShare.instance().settings.theme.control_color_value

      self._sw1_open_indicator = GridCheckbox( **DictOps.dict_combine( kwargs, row = 1, column = 1 ) )
      self._sw1_closed_indicator = GridCheckbox( **DictOps.dict_combine( kwargs, row = 1, column = 2 ) )
      self._sw2_open_indicator = GridCheckbox( **DictOps.dict_combine( kwargs, row = 0, column = 1 ) )
      self._sw2_closed_indicator = GridCheckbox( **DictOps.dict_combine( kwargs, row = 0, column = 2 ) )

      open_indicator_title = GridLabel( **DictOps.dict_combine( kwargs, row = 2, column = 1, text = "Open", color = AppShare.instance().settings.theme.text_color_value ) )
      closed_indicator_title = GridLabel( **DictOps.dict_combine( kwargs, row = 2, column = 2, text = "Closed", color = AppShare.instance().settings.theme.text_color_value ) )

      switch_1_title = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 0, text = "SW1", color = AppShare.instance().settings.theme.text_color_value ) )
      switch_2_title = GridLabel( **DictOps.dict_combine( kwargs, row = 0, column = 0, text = "SW2", color = AppShare.instance().settings.theme.text_color_value ) )

      self.add_widget( open_indicator_title )
      self.add_widget( closed_indicator_title )
      self.add_widget( switch_1_title )
      self.add_widget( switch_2_title )
      self.add_widget( self._sw1_open_indicator )
      self.add_widget( self._sw1_closed_indicator )
      self.add_widget( self._sw2_open_indicator )
      self.add_widget( self._sw2_closed_indicator )

   def _get_switch_1_closed( self ):
      return self._sw1_closed

   def _set_switch_1_closed( self, value ):
      self._sw1_closed = value
      self._update_switch_1()

   sw1_closed = property( fget = _get_switch_1_closed, fset = _set_switch_1_closed )

   def _update_switch_1( self ):
      self._sw1_open_indicator.active = not self.sw1_closed
      self._sw1_closed_indicator.active = self.sw1_closed

   def _get_switch_2_closed( self ):
      return self._sw2_closed

   def _set_switch_2_closed( self, value ):
      self._sw2_closed = value
      self._update_switch_2()

   sw2_closed = property( fget = _get_switch_2_closed, fset = _set_switch_2_closed )

   def _update_switch_2( self ):
      self._sw2_open_indicator.active = not self.sw2_closed
      self._sw2_closed_indicator.active = self.sw2_closed
