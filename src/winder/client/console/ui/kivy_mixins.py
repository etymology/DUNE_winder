from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty

class BackgroundColorMixin( object ):
   def __init__( self, **kwargs ):
      if "bg_color" in kwargs:
         initial_color_value = kwargs[ "bg_color" ]
         del kwargs[ "bg_color" ]
      else:
         initial_color_value = None

      self.bind( bg_color = self._set_bg_color )
      super( BackgroundColorMixin, self ).__init__( **kwargs )

      self._initialized = False

      if initial_color_value is not None:
         self.bg_color = initial_color_value

   def _initialize( self, initial_color ):
      self._color = initial_color
      self._background_rectangle = Rectangle( size = self.size, pos = self.pos )

      self.canvas.before.add( self._color )
      self.canvas.before.add( self._background_rectangle )
      self.bind( size = self._update_bg_color, pos = self._update_bg_color )

      self._initialized = True

   def _set_bg_color( self, instance, value ):
      color_components = len( value )

      if color_components == 3:
         color = Color( value[ 0 ], value[ 1 ], value[ 2 ] )
      elif color_components == 4:
         color = Color( value[ 0 ], value[ 1 ], value[ 2 ], value[ 3 ] )
      else:
         raise Exception( "Invalid color: {}".format( str( value ) ) )

      if not self._initialized:
         self._initialize( color )
      else:
         self.canvas.before.clear()

         self._color = color
         self._background_rectangle = Rectangle( size = self.size, pos = self.pos )

         self.canvas.before.add( self._color )
         self.canvas.before.add( self._background_rectangle )

   def _update_bg_color( self, instance, value ):
      self._background_rectangle.pos = instance.pos
      self._background_rectangle.size = instance.size

   bg_color = ListProperty( [ 0, 0, 0, 0 ] )
