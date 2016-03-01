from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from winder.utility.collections import DictOps

from ..application_shared import AppShare
from .kivy_labelled_checkbox import LabelledCheckbox

class ZFixedDisplay( BoxLayout ):
   def __init__( self, **kwargs ):
      super( ZFixedDisplay, self ).__init__( **DictOps.dict_combine( kwargs, orientation = "vertical" ) )
      self._construct( **kwargs )

   def _construct( self, **kwargs ):
      self.contact_display = LabelledCheckbox( **DictOps.dict_combine( kwargs, text = "Contact", color = AppShare.instance().settings.theme.text_color ) )
      self.spring_display = LabelledCheckbox( **DictOps.dict_combine( kwargs, text = "Spring", color = AppShare.instance().settings.theme.text_color ) )
      fixed_title = Label( **DictOps.dict_combine( kwargs, text = "Fixed", color = AppShare.instance().settings.theme.text_color ) )

      self.add_widget( self.contact_display )
      self.add_widget( fixed_title )
      self.add_widget( self.spring_display )
