from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty

class BackgroundColorMixin( object ):
   def __init__( self, *args, **kwargs ):
      self.bind( bg_color = self._set_bg_color )
      super( BackgroundColorMixin, self ).__init__( *args, **kwargs )

   def _set_bg_color( self, instance, value ):
      self._background_rectangle = Rectangle( size = self.size, pos = self.pos )

      self.canvas.before.add( value )
      self.canvas.before.add( self._background_rectangle )

      self.bind( size = self._update_bg_color, pos = self._update_bg_color )

   def _update_bg_color( self, instance, value ):
      self._background_rectangle.pos = instance.pos
      self._background_rectangle.size = instance.size

   bg_color = ObjectProperty( Color( 0, 0, 0, 1. ) )
