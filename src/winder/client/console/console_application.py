from kivy.app import App
from kivy.graphics import Color

from .application_shared import AppShare
from .ui.manual_movement import ManualMovementControl


class TestApp( App ):
   def __init__( self, *args, **kwargs ):
      super( TestApp, self ).__init__( *args, **kwargs )

   def build( self ):
      result = ManualMovementControl()
      background_color = Color( AppShare.instance().settings.theme.control_color )
      result.bg_color = background_color

      return result
