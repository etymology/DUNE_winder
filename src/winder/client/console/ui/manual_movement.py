from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from ..command import Command
from .kivy_mixins import BackgroundColorMixin
from .kivy_utilities import KivyUtilities
from .transfer_enables import TransferEnables
from .xy_manual_stage_movement import ManualXyStageMovement
from .z_manual_stage_movement import ManualZStageMovement
from .z_stage_display import ZStageDisplay

class _CurrentPositionCommand( Command ):
   def _position_value_conversion( self, value ):
      if value == "None":
         result = None
      else:
         result = float( value )

      return result

   def get_current_position( self ):
      commands = [ "io.simulationTime.setLocal()", "io.xAxis.getPosition()", "io.yAxis.getPosition()", "io.zAxis.getPosition()" ]
      values = self.send_commands( commands )[ 1 : ]

      result = map( self._position_value_conversion, values )

      return result

class ManualMovementControl( BackgroundColorMixin, BoxLayout ):
   MaximumRate__mmps = 406

   def __init__( self, **kwargs ):
      super( ManualMovementControl, self ).__init__( **DictOps.dict_combine( kwargs, orientation = "vertical", bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self.bind( size = self._update_ui )

      self._construct( **kwargs )
      self._schedule_polling()

   def _construct( self, **kwargs ):
      global_control_layout = self._construct_global_layout()
      xy_layout = self._construct_xy_layout()
      z_layout = self._construct_z_layout()

      movement_layout = BoxLayout( **DictOps.dict_combine( kwargs, orientation = "horizontal" ) )
      KivyUtilities.add_children_to_widget( movement_layout, [ xy_layout, z_layout ] )

      KivyUtilities.add_children_to_widget( self, [ global_control_layout, movement_layout ] )

   def _construct_rate_selection( self, **kwargs ):
      self._slider_scale_values = [ .125, .25, .5, 1. ]
      self._slider_scale_value_labels = [ "Very Slow", "Slow", "Moderate", "Normal" ]

      result = BoxLayout( **DictOps.dict_combine( kwargs, orientation = "vertical" ) )
      rate_slider_title = Label( **DictOps.dict_combine( kwargs, text = "Movement Velocity", color = AppShare.instance().settings.theme.text_color_value ) )
      self.rate_slider = Slider( min = 0, max = len( self._slider_scale_values ) - 1, orientation = "horizontal" )
      self.rate_slider_value_label = Label( **DictOps.dict_combine( kwargs, color = AppShare.instance().settings.theme.text_color_value ) )
      self.rate_slider.bind( value = self._update_slider_label )
      self.rate_slider.value = len( self._slider_scale_values ) / 2

      KivyUtilities.add_children_to_widget( result, [ rate_slider_title, self.rate_slider, self.rate_slider_value_label ] )

      return result

   def _construct_global_layout( self, **kwargs ):
      slider_layout = self._construct_rate_selection()

      result = BoxLayout( **DictOps.dict_combine( kwargs, orientation = "horizontal", size_hint = ( 1, .2 ) ) )

      KivyUtilities.add_children_to_widget( result, [ Label( **DictOps.dict_combine( kwargs, text = "Mode selection" ) ), slider_layout, Label( **DictOps.dict_combine( kwargs, text = "Placeholder" ) ) ] )

      return result

   def _construct_xy_layout( self, **kwargs ):
      self.xy_movement = ManualXyStageMovement( self._get_current_rate__mmps, **kwargs )
      self.transfer_enables = TransferEnables()

      result = BoxLayout( **DictOps.dict_combine( kwargs, orientation = "vertical" ) )

      KivyUtilities.add_children_to_widget( result, [ self.xy_movement, self.transfer_enables ] )

      return result

   def _construct_z_layout( self, **kwargs ):
      self.z_movement = ManualZStageMovement( self._get_current_rate__mmps, **kwargs )
      self.z_display = ZStageDisplay( **kwargs )

      result = GridLayout( **DictOps.dict_combine( kwargs, cols = 1 ) )

      KivyUtilities.add_children_to_widget( result, [ self.z_movement, self.z_display ] )

      return result

   def _get_current_rate__mmps( self ):
      rate_scale = self._slider_scale_values[ int( self.rate_slider.value ) ]

      result = rate_scale * ManualMovementControl.MaximumRate__mmps

      return result

   def _update_slider_label( self, instance, value ):
      self.rate_slider_value_label.text = "{} ({:d} mm/s)".format( self._get_current_rate_value(), int( self._get_current_rate__mmps() ) )

   def _get_current_rate_value( self ):
      index = int( self.rate_slider.value )
      return self._slider_scale_value_labels[ index ]

   def _update_ui( self, instance, value ):
      self.spacing = self.width / 20

   def _control_layout_update( self, instance, value ):
      self.control_layout.spacing = self.control_layout.height / 20

   def _output_layoutupdate( self, instance, value ):
      self.output_layout.spacing = self.output_layout.height / 20

   def _schedule_polling( self ):
      self.current_position_command = _CurrentPositionCommand()

      Clock.schedule_interval( self._clock_interval_expiration, .25 )

   def _clock_interval_expiration( self, dt ):
      positions = self.current_position_command.get_current_position()
      self.xy_movement.update_xy_position( positions[ 0 ], positions[ 1 ] )
      self.z_movement.update_z_position( positions[ 2 ] )
      self.transfer_enables.update_position( positions[ 0 : 2 ] )

      return True
