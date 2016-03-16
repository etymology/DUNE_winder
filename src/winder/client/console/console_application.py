from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

# from .application_shared import AppShare
from .ui.kivy_mixins import BackgroundColorMixin
from .ui.manual_movement import ManualMovementControl
from .ui.operation_bar import OperationBar

class RootWidget( BackgroundColorMixin, BoxLayout ):
   def __init__( self, **kwargs ):
      super( RootWidget, self ).__init__( orientation = "vertical", **kwargs )
      self._construct()

   def _construct( self, **kwargs ):
#       self.bg_color = AppShare.instance().settings.theme.control_color_value

      self.operation_bar = OperationBar( size_hint = ( 1, .25 ) )
      self.tabbed_layout = self._construct_tabbed_layout()

      for widget in [self.operation_bar, self.tabbed_layout]:
         self.add_widget( widget )

   def _construct_tabbed_layout( self, **kwargs ):
      self.main_tab = TabbedPanelItem( text = "Main", **kwargs )
      self.apa_tab = TabbedPanelItem( text = "APA", **kwargs )
      self.manual_movement_control = ManualMovementControl()
      self.manual_movement_tab = TabbedPanelItem( text = "Manual", content = self.manual_movement_control, **kwargs )

      result = TabbedPanel( do_default_tab = False, **kwargs )

      for widget in [ self.main_tab, self.apa_tab, self.manual_movement_tab ]:
         result.add_widget( widget )

      return result

class ConsoleClientApplication( App ):
   def build( self ):
      result = RootWidget()
      return result
