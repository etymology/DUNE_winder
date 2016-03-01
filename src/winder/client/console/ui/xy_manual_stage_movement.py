from winder.utility.collections import DictOps
from ..application_shared import AppShare
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry, GridImageButton, GridLabel

class _PositiveXDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "+X pressed." )

   def on_release( self ):
      print( "+X released." )

class _NegativeXDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "-X pressed." )

   def on_release( self ):
      print( "-X released." )

class _PositiveYDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "+Y pressed." )

   def on_release( self ):
      print( "+Y released." )

class _NegativeYDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "-Y pressed." )

   def on_release( self ):
      print( "-Y released." )

class ManualXyStageMovement( SparseGridLayout ):
   def __init__( self, **kwargs ):
      super( ManualXyStageMovement, self ).__init__( rows = 3, columns = 3, **kwargs )
      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      negative_x_direction_control = _NegativeXDirectionControl( **DictOps.dict_combine( kwargs, row = 1, column = 0, source = AppShare.instance().settings.theme.neg_x_arrow ) )
      positive_x_direction_control = _PositiveXDirectionControl( **DictOps.dict_combine( kwargs, row = 1, column = 2, source = AppShare.instance().settings.theme.pos_x_arrow ) )
      negative_y_direction_control = _NegativeYDirectionControl( **DictOps.dict_combine( kwargs, row = 0, column = 1, source = AppShare.instance().settings.theme.neg_y_arrow ) )
      positive_y_direction_control = _PositiveYDirectionControl( **DictOps.dict_combine( kwargs, row = 2, column = 1, source = AppShare.instance().settings.theme.pos_y_arrow ) )

      position_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 1 , text = "--", color = AppShare.instance().settings.theme.text_color ) )

      self.position_label = position_label

      self.add_widget( negative_x_direction_control )
      self.add_widget( positive_x_direction_control )
      self.add_widget( negative_y_direction_control )
      self.add_widget( positive_y_direction_control )
      self.add_widget( self.position_label )

   def update_xy_position( self, x_pos, y_pos ):
      if x_pos is not None and y_pos is not None:
         text = "%d, %d" % ( x_pos, y_pos )
      else:
         text = "--"

      self.position_label.text = text
