from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry, GridLabel, GridLabelledCheckbox
from .z_stage_retracts import ZStageRetracts

class _GridZStageRetracts( ZStageRetracts, GridEntry ):
   pass

class ZStageDisplay( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( ZStageDisplay, self ).__init__( **DictOps.dict_combine( kwargs, rows = 4, columns = 3 ) )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      self.bg_color = AppShare.instance().settings.theme.control_color_value

      retracts_title = GridLabel( **DictOps.dict_combine( kwargs, text = "Retracts", row = 3, column = 0, color = AppShare.instance().settings.theme.text_color_value ) )
      stage_title = GridLabel( **DictOps.dict_combine( kwargs, text = "Front\nBack", row = 1, column = 1, row_span = 2, column_span = 2, color = AppShare.instance().settings.theme.text_color_value ) )
      stage_title.bg_color = AppShare.instance().settings.theme.stage_color_value

      self._front_latched_motor_control = GridLabelledCheckbox( **DictOps.dict_combine( kwargs, row = 3, column = 2, column_span = 1, text = "Front Latched", color = AppShare.instance().settings.theme.text_color_value ) )
      self._back_latched_motor_control = GridLabelledCheckbox( **DictOps.dict_combine( kwargs, row = 0, column = 2, column_span = 1, text = "Back Latched", color = AppShare.instance().settings.theme.text_color_value ) )

      self._front_retracts = _GridZStageRetracts( **DictOps.dict_combine( kwargs, row = 2, column = 0 ) )
      self._back_retracts = _GridZStageRetracts( **DictOps.dict_combine( kwargs, row = 1, column = 0 ) )

      self.add_widget( retracts_title )
      self.add_widget( self._front_latched_motor_control )
      self.add_widget( self._front_retracts )
      self.add_widget( self._back_retracts )
      self.add_widget( stage_title )
      self.add_widget( self._back_latched_motor_control )
