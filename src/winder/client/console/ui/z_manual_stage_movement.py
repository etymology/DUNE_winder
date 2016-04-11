from winder.utility.collections import DictOps

from ..application_shared import AppShare
from ..movement_command import MovementCommand
from .kivy_mixins import BackgroundColorMixin
from .kivy_sparce_grid_layout import SparseGridLayout, GridLabel, GridImageButton, GridEntry
from .kivy_utilities import KivyUtilities

class _ZMovementCommand( MovementCommand ):
   def move_start( self, z ):
      command = "process.jogZ( %s )" % ( z )
      return self.send_command( command )

   def move_stop( self ):
      return self.move_start( 0 )

   def move_to( self, z_pos, maximum_velocity = None ):
      command = "process.manualSeekZ( {:f}, {} )".format( z_pos, maximum_velocity )
      return self.send_command( command )

class _PositiveZDirectionControl( GridImageButton, _ZMovementCommand ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( rate )

   def on_release( self ):
      self.move_stop()

class _NegativeZDirectionControl( GridImageButton, _ZMovementCommand ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( -rate )

   def on_release( self ):
      self.move_stop()

class ManualZStageMovement( SparseGridLayout, BackgroundColorMixin ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( ManualZStageMovement, self ).__init__( **DictOps.dict_combine( kwargs, rows = 3, columns = 3, bg_color = AppShare.instance().settings.theme.control_color_value ) )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all, "size_hint" ) )

   def _construct( self, **kwargs ):
      common_kwargs = { MovementCommand.Keys.MovementRateCallback : self._movement_rate_callback }

      to_back_label = GridLabel( **DictOps.dict_combine( kwargs, common_kwargs, row = 0, column = 0, text = "Toward Back", color = AppShare.instance().settings.theme.text_color_value ) )
      to_front_label = GridLabel( **DictOps.dict_combine( kwargs, common_kwargs, row = 0, column = 2, text = "Toward Front", color = AppShare.instance().settings.theme.text_color_value ) )
      back_direction_control = _NegativeZDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 0, source = AppShare.instance().settings.theme.neg_z_arrow ) )
      forward_direction_control = _PositiveZDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 2, source = AppShare.instance().settings.theme.pos_z_arrow ) )
      self.position_label = GridLabel( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 1, text = "--", color = AppShare.instance().settings.theme.text_color_value ) )

      KivyUtilities.add_children_to_widget( self, [ to_back_label, back_direction_control, forward_direction_control, to_front_label, self.position_label ] )

   def update_z_position( self, value ):
      # If the PLC is unavailable, the value is None.
      if value is not None:
         text = "{:.2f} mm".format( value )
      else:
         text = "--"

      self.position_label.text = text
