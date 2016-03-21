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
   def __init__( self, **kwargs ):
      super( ManualMovementControl, self ).__init__( orientation = "horizontal", **kwargs )

      self.minimum_rate_value = 0
      self.maximum_rate_value = 100
      self._slider_scale_values = [ .1, .25, .33, .5, .66, .75, 1. ]
      self._slider_scale_value_labels = [ "Slowest", "Slower", "Slow", "Medium", "Fast", "Faster", "Fastest" ]

      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.bg_color = AppShare.instance().settings.theme.control_color_value

      slider_layout = BoxLayout( orientation = "vertical", **kwargs )
      self.rate_slider = Slider( min = 0, max = len( self._slider_scale_values ) - 1, orientation = "horizontal" )
      self.rate_slider_value_label = Label( color = AppShare.instance().settings.theme.text_color_value )
      self.rate_slider.bind( value = self._update_slider_label )
      self.rate_slider.value = len( self._slider_scale_values ) / 2
      KivyUtilities.add_children_to_widget( slider_layout, [ self.rate_slider, self.rate_slider_value_label ] )

      self.xy_movement = ManualXyStageMovement( self._get_current_rate, **kwargs )
      self.z_movement = ManualZStageMovement( self._get_current_rate, **kwargs )

      global_control_layout = BoxLayout( orientation = "vertical", **kwargs )
      control_layout = BoxLayout( orientation = "vertical", **kwargs )
      output_layout = BoxLayout( orientation = "vertical", **kwargs )

      KivyUtilities.add_children_to_widget( global_control_layout, [ slider_layout ] )
      KivyUtilities.add_children_to_widget( control_layout, [ self.xy_movement, self.z_movement, global_control_layout ] )
      KivyUtilities.add_children_to_widget( output_layout, [ ZStageDisplay(), ZFixedDisplay() ] )
      KivyUtilities.add_children_to_widget( self, [ control_layout, output_layout ] )

   def _get_current_rate( self ):
      rate_scale = self._slider_scale_values[ int( self.rate_slider.value ) ]
      rate_range = self.maximum_rate_value - self.minimum_rate_value

      result = rate_range * rate_scale + self.minimum_rate_value

      return result

   def _update_slider_label( self, instance, value ):
      self.rate_slider_value_label.text = "{} ({:d})".format( self._get_current_rate_value(), int( self._get_current_rate() ) )

   def _get_current_rate_value( self ):
      index = int( self.rate_slider.value )
      return self._slider_scale_value_labels[ index ]
