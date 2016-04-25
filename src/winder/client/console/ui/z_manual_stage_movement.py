import re

from kivy.properties import BooleanProperty
from kivy.uix.label import Label

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from ..movement_command import MovementCommand
from .display_selection_layout import DisplaySelectionLayout
from .kivy_sparce_grid_layout import SparseGridLayout, GridBoxLayout, GridButton, GridEntry, GridImageButton, GridLabel, GridTextInput
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

class _ZPositionSeekInput( GridTextInput ):
   class Keys:
      ZValue = "z"

   float_pattern = r"[+-]?(?:\d+(?:\.\d*)?)|(?:\.\d+)"
   valid_pattern = r"\s*(?P<{1}>{0})\s*".format( float_pattern, Keys.ZValue )
   valid_expression = re.compile( valid_pattern )

   def __init__( self, **kwargs ):
      self._set_seek_z_position( None )

      super( _ZPositionSeekInput, self ).__init__( **DictOps.dict_combine( kwargs, multiline = False ) )

   def _set_validity( self ):
      self.is_valid = self.valid_expression.match( self.text ) is not None
      self.is_invalid = not self.is_valid

   is_valid = BooleanProperty( False )
   is_invalid = BooleanProperty( True )

   def _get_seek_z_position( self ):
      return self._seek_z_pos

   def _set_seek_z_position( self, value ):
      self._seek_z_pos = value

   seek_z_position = property( fget = _get_seek_z_position )

   def _process_text( self ):
      self._set_validity()
      if self.is_valid:
         match = self.valid_expression.match( self.text ) # match will not be None
         z_pos_str = match.groupdict()[ _ZPositionSeekInput.Keys.ZValue ]

         z_pos = float( z_pos_str )
      else:
         z_pos = None

      self._set_seek_z_position( z_pos )

   def insert_text( self, substring, from_undo = False ):
      result = super( _ZPositionSeekInput, self ).insert_text( substring, from_undo )

      self._process_text()

      return result

   def set_text( self, new_text ):
      self.text = new_text
      self._process_text()

class _ZPositionSeekButton( GridButton, _ZMovementCommand ):
   class Keys:
      InputControl = "input"

   def __init__( self, **kwargs ):
      if _ZPositionSeekButton.Keys.InputControl in kwargs:
         self.input_control = kwargs[ _ZPositionSeekButton.Keys.InputControl ]
         del kwargs[ _ZPositionSeekButton.Keys.InputControl ]
      else:
         raise ValueError( "Missing the input control." )

      super( _ZPositionSeekButton, self ).__init__( **kwargs )

   def on_press( self ):
      if self.input_control.is_valid:
         if self.movement_rate_callback is not None:
            rate = self.movement_rate_callback()
         else:
            rate = None

         self.move_to( self.input_control.seek_z_position, rate )

class _ManualZStageMovement_Jog( SparseGridLayout ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( _ManualZStageMovement_Jog, self ).__init__( **DictOps.dict_combine( kwargs, rows = 3, columns = 3, bg_color = AppShare.instance().settings.theme.control_color_value ) )

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

   def update_position( self, x_pos, y_pos, z_pos ):
      # If the PLC is unavailable, both x_pos and y_pos are None.
      if x_pos is not None and y_pos is not None:
         text = "{:.2f} mm".format( z_pos )
      else:
         text = "--"

      self.position_label.text = text

class _ManualZStageMovement_Seek( SparseGridLayout ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( _ManualZStageMovement_Seek, self ).__init__( **DictOps.dict_combine( kwargs, rows = 3, columns = 3 ) )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all, "size_hint" ) )

   def _construct( self, **kwargs ):
      common_kwargs = { MovementCommand.Keys.MovementRateCallback : self._movement_rate_callback }

      position_title = Label( text = "Position: ", color = AppShare.instance().settings.theme.text_color_value )
      self.position_label = Label( text = "--", color = AppShare.instance().settings.theme.text_color_value )

      position_layout = GridBoxLayout( **DictOps.dict_combine( kwargs, row = 2, column = 1, orientation = "horizontal" ) )
      KivyUtilities.add_children_to_widget( position_layout, [ position_title, self.position_label ] )

      self.seek_z_position_input = _ZPositionSeekInput( **DictOps.dict_combine( kwargs, row = 1, column = 0, column_span = 3 ) ) # size_hint = ( None, 1 )
      self.seek_z_position_button = _ZPositionSeekButton( **DictOps.dict_combine( kwargs, common_kwargs, row = 0, column = 1, input = self.seek_z_position_input, text = "Go to Position", color = AppShare.instance().settings.theme.text_color_value, valign = "middle", bg_color = AppShare.instance().settings.theme.control_color_value ) ) # size_hint = ( None, 1 )

      KivyUtilities.add_children_to_widget( self, [ position_layout, self.seek_z_position_input, self.seek_z_position_button ] )

   def update_position( self, x_pos, y_pos, z_pos ):
      # If the PLC is unavailable, both x_pos and y_pos are None.
      if x_pos is not None and y_pos is not None:
         text = "{:.2f} mm".format( z_pos )
      else:
         text = "--"

      self.position_label.text = text

class ManualZStageMovement( DisplaySelectionLayout ):
   class Ids:
      Jog = "jog"
      Seek = "seek"

   def __init__( self, movement_rate_callback, initial_children = None, **kwargs ):
      super( ManualZStageMovement, self ).__init__( initial_children, **kwargs )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      common_kwargs = { MovementCommand.Keys.MovementRateCallback : self._movement_rate_callback }

      self.jog_movement = _ManualZStageMovement_Jog( **DictOps.dict_combine( kwargs, common_kwargs ) )
      self.seek_movement = _ManualZStageMovement_Seek( **DictOps.dict_combine( kwargs, common_kwargs ) )

      self.add_widget( self.jog_movement, self.Ids.Jog )
      self.add_widget( self.seek_movement, self.Ids.Seek )

   def select_movement_type( self, is_jog_mode_selected ):
      if is_jog_mode_selected:
         selected_id = self.Ids.Jog
      else:
         selected_id = self.Ids.Seek

      self.selected_id = selected_id

   def update_position( self, x_pos, y_pos, z_pos ):
      return self.selected_item.update_position( x_pos, y_pos, z_pos )
