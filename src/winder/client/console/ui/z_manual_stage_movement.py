from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .kivy_sparce_grid_layout import SparseGridLayout, GridLabel, GridImageButton, GridEntry

class _PositiveZDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "+Z pressed." )

   def on_release( self ):
      print( "+Z released." )

class _NegativeZDirectionControl( GridImageButton ):
   def on_press( self ):
      print( "-Z pressed." )

   def on_release( self ):
      print( "-Z released." )

class ManualZStageMovement( SparseGridLayout, BackgroundColorMixin ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( ManualZStageMovement, self ).__init__( **DictOps.dict_combine( kwargs, rows = 2, columns = 5 ) )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )

   def _construct( self, **kwargs ):
      self.bg_color = AppShare.instance().settings.theme.control_color_value

#       common_kwargs = { _XyCommands.Keys.MovementRateCallback : self._movement_rate_callback }

      to_back_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 0, text = "To Back", color = AppShare.instance().settings.theme.text_color_value ) )
      to_front_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 4, text = "To Front", color = AppShare.instance().settings.theme.text_color_value ) )
      back_direction_control = _NegativeZDirectionControl( **DictOps.dict_combine( kwargs, row = 1, column = 1, source = AppShare.instance().settings.theme.neg_z_arrow ) )
      forward_direction_control = _PositiveZDirectionControl( **DictOps.dict_combine( kwargs, row = 1, column = 3, source = AppShare.instance().settings.theme.pos_z_arrow ) )
      direction_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 2, text = "Z", color = AppShare.instance().settings.theme.text_color_value ) )
      position_label = GridLabel( **DictOps.dict_combine( kwargs, row = 0, column = 2, text = "--", color = AppShare.instance().settings.theme.text_color_value ) )

      self.add_widget( to_back_label )
      self.add_widget( back_direction_control )
      self.add_widget( direction_label )
      self.add_widget( forward_direction_control )
      self.add_widget( to_front_label )
      self.add_widget( position_label )

      self.position_label = position_label

   def update_z_position( self, value ):
      if value is not None:
         text = "%d, %d" % ( value[0], value[1] )
      else:
         text = "--"

      self.position_label.text = text
