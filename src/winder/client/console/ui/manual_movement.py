from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .kivy_utilities import KivyUtilities
from .xy_manual_stage_movement import ManualXyStageMovement
from .z_fixed_display import ZFixedDisplay
from .z_manual_stage_movement import ManualZStageMovement
from .z_stage_display import ZStageDisplay


class ManualMovementControl( BackgroundColorMixin, BoxLayout ):
   MaximumRate__mmps = 406

   def __init__( self, **kwargs ):
      super( ManualMovementControl, self ).__init__( orientation = "horizontal", bg_color = AppShare.instance().settings.theme.control_color_value, **kwargs )
      self.bind( size = self._update_ui )

      self._slider_scale_values = [ .1, .25, .33, .5, .66, .75, 1. ]
      self._slider_scale_value_labels = [ "Slowest", "Slower", "Slow", "Medium", "Fast", "Faster", "Fastest" ]

      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      slider_layout = BoxLayout( orientation = "vertical", **kwargs )
      rate_slider_title = Label( text = "Movement Velocity", color = AppShare.instance().settings.theme.text_color_value, **kwargs )
      self.rate_slider = Slider( min = 0, max = len( self._slider_scale_values ) - 1, orientation = "horizontal" )
      self.rate_slider_value_label = Label( color = AppShare.instance().settings.theme.text_color_value )
      self.rate_slider.bind( value = self._update_slider_label )
      self.rate_slider.value = len( self._slider_scale_values ) / 2
      KivyUtilities.add_children_to_widget( slider_layout, [ rate_slider_title, self.rate_slider, self.rate_slider_value_label ] )

      stages_size_hint = ( 1, .33 )

      self.xy_movement = ManualXyStageMovement( self._get_current_rate__mmps, size_hint = stages_size_hint, **kwargs )
      self.z_movement = ManualZStageMovement( self._get_current_rate__mmps, size_hint = stages_size_hint, **kwargs )

      global_control_layout = BoxLayout( orientation = "vertical", size_hint = stages_size_hint, **kwargs )

      self.control_layout = BoxLayout( orientation = "vertical", **kwargs )
      self.control_layout.bind( size = self._control_layout_update )
      self.output_layout = BoxLayout( orientation = "vertical", **kwargs )
      self.output_layout.bind( size = self._output_layoutupdate )

      KivyUtilities.add_children_to_widget( global_control_layout, [ slider_layout ] )
      KivyUtilities.add_children_to_widget( self.control_layout, [ self.xy_movement, self.z_movement, global_control_layout ] )
      KivyUtilities.add_children_to_widget( self.output_layout, [ ZStageDisplay(), ZFixedDisplay() ] )
      KivyUtilities.add_children_to_widget( self, [ self.control_layout, self.output_layout ] )

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
