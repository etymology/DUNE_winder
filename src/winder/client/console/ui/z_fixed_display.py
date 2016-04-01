from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_mixins import BackgroundColorMixin
from .kivy_utilities import KivyUtilities
from .labelled_switch import LabelledWinderSwitch
from .switch import WinderSwitchStates

class ZFixedDisplay( BackgroundColorMixin, BoxLayout ):
   def __init__( self, **kwargs ):
      super( ZFixedDisplay, self ).__init__( **DictOps.dict_combine( kwargs, size_hint = ( .25, None ), orientation = "vertical", bg_color = AppShare.instance().settings.theme.control_color_value ) )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.contact_display = LabelledWinderSwitch( **DictOps.dict_combine( kwargs, text = "Contact", color = AppShare.instance().settings.theme.text_color_value, state = WinderSwitchStates.Off ) )
      self.spring_display = LabelledWinderSwitch( **DictOps.dict_combine( kwargs, text = "Spring", color = AppShare.instance().settings.theme.text_color_value, state = WinderSwitchStates.On ) )
      fixed_title = Label( **DictOps.dict_combine( kwargs, text = "Fixed", color = AppShare.instance().settings.theme.text_color_value ) )

      KivyUtilities.add_children_to_widget( self, [ self.contact_display, fixed_title, self.spring_display ] )
