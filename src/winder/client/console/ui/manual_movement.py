from kivy.uix.boxlayout import BoxLayout

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .xy_manual_stage import XyStage
from .z_manual_stage import ZStage

class ManualMovementControl( BackgroundColorMixin, BoxLayout ):
   def __init__( self, **kwargs ):
      super( ManualMovementControl, self ).__init__( **kwargs )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.bg_color = AppShare.instance().settings.theme.control_color_value

      self.xy_movement = XyStage( **kwargs )
      self.z_movement = ZStage( **kwargs )

      self.add_widget( self.xy_movement )
      self.add_widget( self.z_movement )
