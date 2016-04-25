from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_sparse_grid_layout import SparseGridLayout, GridEntry, GridLabel
from .kivy_utilities import KivyUtilities
from .labelled_switch import GridLabelledWinderSwitch
from .switch import WinderSwitchStates

class ZStageDisplay( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( ZStageDisplay, self ).__init__( **DictOps.dict_combine( kwargs, rows = 5, columns = 10, bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      common_kwargs = { ZStageDisplay.Keys.Color: AppShare.instance().settings.theme.control_color_value, "color": AppShare.instance().settings.theme.text_color_value }

      head_present_text = "Head Present"
      latched_text = "Latched"

      self.stage_retract_1 = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 0, row = 4, text = "Retract 1", state = WinderSwitchStates.Error ) )
      self.stage_retract_2 = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 0, row = 3, text = "Retract 2", state = WinderSwitchStates.Error ) )
      self.stage_extend = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 2, row = 3, text = "Extend", state = WinderSwitchStates.Off ) )
      self.stage_head_present = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 3, row = 4, text = head_present_text, state = WinderSwitchStates.Off ) )
      self.stage_latched = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 3, row = 2, text = latched_text, state = WinderSwitchStates.Off ) )
      self.latch_arm_position = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 3, row = 1, text = "Latch Arm Position", state = WinderSwitchStates.Off ) )
      self.fixed_head_present = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 6, row = 4, text = head_present_text, state = WinderSwitchStates.On ) )
      self.fixed_latched = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 6, row = 2, text = latched_text, state = WinderSwitchStates.On ) )
      self.fixed_compressed = GridLabelledWinderSwitch( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 2, column = 7, row = 3, text = "Compressed", state = WinderSwitchStates.On ) )
      stage_label = GridLabel( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 5, column = 0, row = 0, text = "Stage Switches" ) )
      fixed_label = GridLabel( **DictOps.dict_combine( kwargs, common_kwargs, column_span = 3, column = 6, row = 0, text = "Fixed Switches" ) )

      KivyUtilities.add_children_to_widget( self, [ self.stage_retract_1, self.stage_retract_2, self.stage_extend, self.stage_head_present, self.stage_latched, self.latch_arm_position, self.fixed_head_present, self.fixed_latched, self.fixed_compressed, stage_label, fixed_label ] )
