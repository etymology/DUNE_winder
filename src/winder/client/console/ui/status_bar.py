from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .kivy_utilities import KivyUtilities

class StatusBar( BackgroundColorMixin, BoxLayout ):
   def __init__( self, **kwargs ):
      super( StatusBar, self ).__init__( **DictOps.dict_combine( kwargs, orientation = "horizontal", bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      server_label = Label( **DictOps.dict_combine( kwargs, text = "{}:{}".format( AppShare.instance().settings.server_address, AppShare.instance().settings.server_listening_port ), color = AppShare.instance().settings.theme.text_color_value ) )

      KivyUtilities.add_children_to_widget( self, [ server_label ] )
