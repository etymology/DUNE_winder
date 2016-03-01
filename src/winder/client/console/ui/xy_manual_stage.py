from winder.utility.collections import DictOps
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry
from .xy_manual_stage_movement import ManualXyStageMovement

class _GridManualXyStageMovement( ManualXyStageMovement, GridEntry ):
   pass

class XyStage( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( XyStage, self ).__init__( **DictOps.dict_combine( kwargs, rows = 2, columns = 2 ) )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      self.xy_movement_control = _GridManualXyStageMovement( **DictOps.dict_combine( kwargs, row = 1, column = 0, column_span = 2 ) )

      self.add_widget( self.xy_movement_control )
