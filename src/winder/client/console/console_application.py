from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from .ui.kivy_mixins import BackgroundColorMixin

Builder.load_file( r"console_application.kv" )

class RootWidget( BackgroundColorMixin, FloatLayout ):
   pass

class ConsoleClientApplication( App ):
   def build( self ):
      result = RootWidget()
      return result
