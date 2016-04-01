from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from winder.utility.collections import DictOps

from .ui.kivy_mixins import BackgroundColorMixin
from .ui.manual_movement import ManualMovementControl
from .ui.operation_bar import OperationBar

class RootWidget( BackgroundColorMixin, BoxLayout ):
   def __init__( self, **kwargs ):
      super( RootWidget, self ).__init__( **DictOps.dict_combine( kwargs, orientation = "vertical" ) )
      self._construct()

   def _construct( self, **kwargs ):
      self.operation_bar = OperationBar( **DictOps.dict_combine( kwargs, size_hint = ( 1, .25 ) ) )
      self.tabbed_layout = self._construct_tabbed_layout( **kwargs )

      for widget in [ self.operation_bar, self.tabbed_layout ]:
         self.add_widget( widget )

   def _construct_tabbed_layout( self, **kwargs ):
      self.main_tab = TabbedPanelItem( **DictOps.dict_combine( kwargs, text = "Main" ) )
      self.apa_tab = TabbedPanelItem( **DictOps.dict_combine( kwargs, text = "APA" ) )
      self.manual_movement_control = ManualMovementControl( **kwargs )
      self.manual_movement_tab = TabbedPanelItem( **DictOps.dict_combine( kwargs, text = "Manual", content = self.manual_movement_control ) )

      result = TabbedPanel( **DictOps.dict_combine( kwargs, do_default_tab = False ) )

      for widget in [ self.main_tab, self.apa_tab, self.manual_movement_tab ]:
         result.add_widget( widget )

      return result

class ConsoleClientApplication( App ):
   def build( self, **kwargs ):
      result = RootWidget( **kwargs )
      return result
