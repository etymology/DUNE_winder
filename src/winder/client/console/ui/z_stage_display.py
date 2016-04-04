from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry, GridLabel
from .kivy_utilities import KivyUtilities
from .labelled_switch import GridLabelledWinderSwitch
from .switch import WinderSwitchStates
from .z_stage_retracts import ZStageRetracts


class _GridZStageRetracts( ZStageRetracts, GridEntry ):
   pass

class ZStageDisplay( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( ZStageDisplay, self ).__init__( **DictOps.dict_combine( kwargs, rows = 4, columns = 3, bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      retracts_title = GridLabel( **DictOps.dict_combine( kwargs, text = "Retracts", row = 3, column = 0, color = AppShare.instance().settings.theme.text_color_value ) )
      stage_title = GridLabel( **DictOps.dict_combine( kwargs, text = "Front\nBack", row = 1, column = 1, row_span = 2, column_span = 2, color = AppShare.instance().settings.theme.text_color_value, bg_color = AppShare.instance().settings.theme.stage_color_value ) )

      self._front_latched_motor_control = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, row = 3, column = 2, column_span = 1, text = "Front Latched", color = AppShare.instance().settings.theme.text_color_value, state = WinderSwitchStates.Error ) )
      self._back_latched_motor_control = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, row = 0, column = 2, column_span = 1, text = "Back Latched", color = AppShare.instance().settings.theme.text_color_value, state = WinderSwitchStates.On ) )

      self._front_retracts = _GridZStageRetracts( **DictOps.dict_combine( kwargs, row = 2, column = 0 ) )
      self._back_retracts = _GridZStageRetracts( **DictOps.dict_combine( kwargs, row = 1, column = 0 ) )

      KivyUtilities.add_children_to_widget( self, [ retracts_title, self._front_latched_motor_control, self._front_retracts, self._back_retracts, stage_title, self._back_latched_motor_control ] )
