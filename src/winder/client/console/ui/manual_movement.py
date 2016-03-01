from kivy.uix.boxlayout import BoxLayout

from .kivy_mixins import BackgroundColorMixin
from .xy_manual_stage import XyStage
from .z_manual_stage import ZStage

class ManualMovementControl( BoxLayout, BackgroundColorMixin ):
   def __init__( self, **kwargs ):
      super( ManualMovementControl, self ).__init__( **kwargs )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.xy_movement = XyStage( **kwargs )
      self.z_movement = ZStage( **kwargs )

      self.add_widget( self.xy_movement )
      self.add_widget( self.z_movement )
