from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry
from .z_fixed_display import ZFixedDisplay
from .z_manual_stage_movement import ManualZStageMovement
from .z_stage_display import ZStageDisplay


class _GridZStageDisplay( GridEntry, ZStageDisplay ):
   pass

class _GridZFixedDisplay( GridEntry, ZFixedDisplay ):
   pass

class _GridManualZStageMovement( GridEntry, ManualZStageMovement ):
   pass

class ZStage( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( ZStage, self ).__init__( **DictOps.dict_combine( kwargs, rows = 2, columns = 2, bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      self.z_stage_movement_control = _GridManualZStageMovement( **DictOps.dict_combine( kwargs, row = 1, column = 0, column_span = 2 ) )
      self.z_stage_display = _GridZStageDisplay( **DictOps.dict_combine( kwargs, row = 0, column = 0 ) )
      self.z_fixed_display = _GridZFixedDisplay( **DictOps.dict_combine( kwargs, row = 0, column = 1 ) )

      self.add_widget( self.z_stage_movement_control )
      self.add_widget( self.z_stage_display )
      self.add_widget( self.z_fixed_display )
