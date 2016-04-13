import re

from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from ..movement_command import MovementCommand
from .kivy_mixins import BackgroundColorMixin
from .kivy_sparce_grid_layout import GridBoxLayout
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry, GridImageButton, GridLabel
from .kivy_utilities import KivyUtilities

class _XyCommands( MovementCommand ):
   def move_start( self, x, y ):
      command = "process.jogXY( %s, %s )" % ( x, y )
      return self.send_command( command )

   def move_stop( self ):
      return self.move_start( 0, 0 )

   def move_to( self, x, y, maximum_velocity = None ):
      command = "process.manualSeekXY( {:f}, {:f}, {} )".format( x, y, maximum_velocity )
      return self.send_command( command )

class _PositiveXDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( rate, 0 )

   def on_release( self ):
      self.move_stop()

class _NegativeXDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( -rate, 0 )

   def on_release( self ):
      self.move_stop()

class _PositiveYDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( 0, rate )

   def on_release( self ):
      self.move_stop()

class _NegativeYDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      rate = self.movement_rate_callback()
      self.move_start( 0, -rate )

   def on_release( self ):
      self.move_stop()

class _XyPositionSeekInput( TextInput ):
   class Keys:
      XValue = "x"
      YValue = "y"

   float_pattern = r"[+-]?(?:\d+(?:\.\d*)?)|(?:\.\d+)"
   valid_pattern = r"\s*(?P<{1}>{0})\s*,\s*(?P<{2}>{0})\s*".format( float_pattern, Keys.XValue, Keys.YValue )
   valid_expression = re.compile( valid_pattern )

   def __init__( self, **kwargs ):
      self._set_seek_x_position( None )
      self._set_seek_y_position( None )

      super( _XyPositionSeekInput, self ).__init__( **DictOps.dict_combine( kwargs, multiline = False ) )

   def _set_validity( self ):
      self.is_valid = self.valid_expression.match( self.text ) is not None
      self.is_invalid = not self.is_valid

   is_valid = BooleanProperty( False )
   is_invalid = BooleanProperty( True )

   def _get_seek_x_position( self ):
      return self._seek_x_pos

   def _set_seek_x_position( self, value ):
      self._seek_x_pos = value

   seek_x_position = property( fget = _get_seek_x_position )

   def _get_seek_y_position( self ):
      return self._seek_y_pos

   def _set_seek_y_position( self, value ):
      self._seek_y_pos = value

   seek_y_position = property( fget = _get_seek_y_position )

   def _process_text( self ):
      self._set_validity()
      if self.is_valid:
         match = self.valid_expression.match( self.text ) # match will not be None
         x_pos_str = match.groupdict()[ _XyPositionSeekInput.Keys.XValue ]
         y_pos_str = match.groupdict()[ _XyPositionSeekInput.Keys.YValue ]

         x_pos = float( x_pos_str )
         y_pos = float( y_pos_str )
      else:
         x_pos = y_pos = None

      self._set_seek_x_position( x_pos )
      self._set_seek_y_position( y_pos )

   def insert_text( self, substring, from_undo = False ):
      result = super( _XyPositionSeekInput, self ).insert_text( substring, from_undo )

      self._process_text()

      return result

   def set_text( self, new_text ):
      self.text = new_text
      self._process_text()

class _XyPositionSeekButton( BackgroundColorMixin, Button, _XyCommands ):
   class Keys:
      InputControl = "input"

   def __init__( self, **kwargs ):
      if _XyPositionSeekButton.Keys.InputControl in kwargs:
         self.input_control = kwargs[ _XyPositionSeekButton.Keys.InputControl ]
         del kwargs[ _XyPositionSeekButton.Keys.InputControl ]
      else:
         raise ValueError( "Missing the input control." )

      super( _XyPositionSeekButton, self ).__init__( **kwargs )

   def on_press( self ):
      if self.input_control.is_valid:
         if self.movement_rate_callback is not None:
            rate = self.movement_rate_callback()
         else:
            rate = None

         self.move_to( self.input_control.seek_x_position, self.input_control.seek_y_position, rate )

class ManualXyStageMovement( SparseGridLayout ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( ManualXyStageMovement, self ).__init__( **DictOps.dict_combine( kwargs, rows = 3, columns = 4 ) )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all, "size_hint" ) )

   def _construct( self, **kwargs ):
      common_kwargs = { MovementCommand.Keys.MovementRateCallback : self._movement_rate_callback }

      negative_x_direction_control = _NegativeXDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 0, source = AppShare.instance().settings.theme.neg_x_arrow ) )
      positive_x_direction_control = _PositiveXDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 2, source = AppShare.instance().settings.theme.pos_x_arrow ) )
      negative_y_direction_control = _NegativeYDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 0, column = 1, source = AppShare.instance().settings.theme.neg_y_arrow ) )
      positive_y_direction_control = _PositiveYDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 2, column = 1, source = AppShare.instance().settings.theme.pos_y_arrow ) )

      negative_x_direction_label = GridLabel( **DictOps.dict_combine( kwargs, row = 0, column = 0, text = "Toward Tail End", color = AppShare.instance().settings.theme.text_color_value ) )
      positive_x_direction_label = GridLabel( **DictOps.dict_combine( kwargs, row = 0, column = 2, text = "Toward Head End", color = AppShare.instance().settings.theme.text_color_value ) )

      self.position_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 1 , text = "--", color = AppShare.instance().settings.theme.text_color_value ) )

      seek_position_layout = GridBoxLayout( **DictOps.dict_combine( kwargs, orientation = "vertical", row = 0, column = 3, column_span = 3 ) )
      self.seek_xy_position_input = _XyPositionSeekInput( size_hint = ( None, 1 ), **kwargs )
      self.seek_xy_position_button = _XyPositionSeekButton( **DictOps.dict_combine( kwargs, common_kwargs, input = self.seek_xy_position_input, text = "Go to Position", color = AppShare.instance().settings.theme.text_color_value, valign = "middle", bg_color = AppShare.instance().settings.theme.control_color_value, size_hint = ( None, 1 ), ) )
#       self.seek_xy_position_button.bind( disabled = self.seek_xy_position_input.is_invalid )

      KivyUtilities.add_children_to_widget( seek_position_layout, [ self.seek_xy_position_input, self.seek_xy_position_button ] )
      KivyUtilities.add_children_to_widget( self, [ negative_x_direction_control, positive_x_direction_control, negative_y_direction_control, positive_y_direction_control, self.position_label, seek_position_layout, negative_x_direction_label, positive_x_direction_label ] )

   def update_xy_position( self, x_pos, y_pos ):
      # If the PLC is unavailable, both x_pos and y_pos are None.
      if x_pos is not None and y_pos is not None:
         text = "{:.2f} mm, {:.2f} mm".format( float( x_pos ), float( y_pos ) )
      else:
         text = "--"

      self.position_label.text = text
