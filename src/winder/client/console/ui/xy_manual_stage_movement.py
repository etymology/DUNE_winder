from kivy.clock import Clock

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from ..command import Command
from .kivy_sparce_grid_layout import SparseGridLayout, GridEntry, GridImageButton, GridLabel
from .kivy_utilities import KivyUtilities

class _XyCommands( Command ):
   class Keys:
      MovementRateCallback = "movement_rate_callback"

   def __init__( self, **kwargs ):
      if _XyCommands.Keys.MovementRateCallback in kwargs:
         self.movement_rate_callback = kwargs[ _XyCommands.Keys.MovementRateCallback ]
         del kwargs[ _XyCommands.Keys.MovementRateCallback ]
      else:
         self.movement_rate_callback = None

   def move_start( self, x, y ):
      command = "process.jogXY( %s, %s )" % ( x, y )
      return self.send_command( command )

   def move_stop( self ):
      return self.move_start( 0, 0 )

class _XyCurrentPositionCommand( Command ):
   def get_current_position( self ):
      commands = [ "io.simulationTime.setLocal()", "io.xAxis.getPosition()", "io.yAxis.getPosition()" ]
      return self.send_commands( commands )[ 1 : ]

class _PositiveXDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      self.move_start( self.movement_rate_callback(), 0 )

   def on_release( self ):
      self.move_stop()

class _NegativeXDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      self.move_start( -self.movement_rate_callback(), 0 )

   def on_release( self ):
      self.move_stop()

class _PositiveYDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      self.move_start( 0, self.movement_rate_callback() )

   def on_release( self ):
      self.move_stop()

class _NegativeYDirectionControl( GridImageButton, _XyCommands ):
   def on_press( self ):
      self.move_start( 0, -self.movement_rate_callback() )

   def on_release( self ):
      self.move_stop()

class ManualXyStageMovement( SparseGridLayout ):
   def __init__( self, movement_rate_callback, **kwargs ):
      super( ManualXyStageMovement, self ).__init__( rows = 3, columns = 3, **kwargs )

      self._movement_rate_callback = movement_rate_callback

      self._construct( **DictOps.dict_filter( kwargs, GridEntry.FieldNames.all ) )
      self._schedule_polling()

   def _construct( self, **kwargs ):
      common_kwargs = { _XyCommands.Keys.MovementRateCallback : self._movement_rate_callback }

      negative_x_direction_control = _NegativeXDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 0, source = AppShare.instance().settings.theme.neg_x_arrow ) )
      positive_x_direction_control = _PositiveXDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 1, column = 2, source = AppShare.instance().settings.theme.pos_x_arrow ) )
      negative_y_direction_control = _NegativeYDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 0, column = 1, source = AppShare.instance().settings.theme.neg_y_arrow ) )
      positive_y_direction_control = _PositiveYDirectionControl( **DictOps.dict_combine( kwargs, common_kwargs, row = 2, column = 1, source = AppShare.instance().settings.theme.pos_y_arrow ) )

      self.position_label = GridLabel( **DictOps.dict_combine( kwargs, row = 1, column = 1 , text = "--", color = AppShare.instance().settings.theme.text_color_value ) )

      KivyUtilities.add_children_to_widget( self, [ negative_x_direction_control, positive_x_direction_control, negative_y_direction_control, positive_y_direction_control, self.position_label ] )

   def _schedule_polling( self ):
      self.current_position_command = _XyCurrentPositionCommand()

      Clock.schedule_interval( self._clock_interval_expiration, .25 )

   def _clock_interval_expiration( self, dt ):
      positions = self.current_position_command.get_current_position()
      self._update_xy_position( positions[ 0 ], positions[ 1 ] )

      return True

   def _update_xy_position( self, x_pos, y_pos ):
      if x_pos is not None and y_pos is not None:
         text = "{:.2f}, {:.2f}".format( float( x_pos ), float( y_pos ) )
      else:
         text = "--"

      self.position_label.text = text
