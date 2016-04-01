from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import BoundedNumericProperty, ListProperty, NumericProperty, OptionProperty
from winder.utility.collections import DictOps

class BackgroundColorMixin( object ):
   class Keys:
      Color = "bg_color"
      Canvas = "bg_canvas"

   bg_color = ListProperty( [ 0, 0, 0, 0 ] )

   def __init__( self, **kwargs ):
      initial_color_value = DictOps.extract_optional_value( kwargs, BackgroundColorMixin.Keys.Color )
      target_canvas_value = DictOps.extract_optional_value( kwargs, BackgroundColorMixin.Keys.Canvas, default_value = "before" )

      self.bind( bg_color = self._set_bg_color )
      super( BackgroundColorMixin, self ).__init__( **kwargs )

      self._initialized = False

      if target_canvas_value is not None:
         self._target_canvas = self._get_canvas( target_canvas_value )

      if initial_color_value is not None:
         self.bg_color = initial_color_value

   def _get_canvas( self, value ):
      if value is None:
         raise ValueError( "Canvas value cannot be None." )
      elif value == "before":
         result = self.canvas.before
      elif value == "normal":
         result = self.canvas
      elif value == "after":
         result = self.canvas.after
      else:
         raise ValueError( "Canvas value '{}' is not valid.".format( value ) )

      return result

   def _get_color( self, value ):
      color_component_count = len( value )

      if color_component_count == 3:
         result = Color( value[ 0 ], value[ 1 ], value[ 2 ] )
      elif color_component_count == 4:
         result = Color( value[ 0 ], value[ 1 ], value[ 2 ], value[ 3 ] )
      else:
         raise Exception( "Invalid color: {}".format( str( value ) ) )

      return result

   def _initialize( self, initial_color ):
      self._color = initial_color
      self._background_rectangle = Rectangle( size = self.size, pos = self.pos )

      self._target_canvas.add( self._color )
      self._target_canvas.add( self._background_rectangle )
      self.bind( size = self._update_bg_color, pos = self._update_bg_color )

      self._initialized = True

   def _set_bg_color( self, instance, value ):
      color = self._get_color( value )

      if not self._initialized:
         self._initialize( color )
      else:
         self._target_canvas.clear()

         self._color = color
         self._background_rectangle = Rectangle( size = self.size, pos = self.pos )

         self._target_canvas.add( self._color )
         self._target_canvas.add( self._background_rectangle )

   def _update_bg_color( self, instance, value ):
      self._background_rectangle.pos = instance.pos
      self._background_rectangle.size = instance.size

class BackgroundShapeMixin( BackgroundColorMixin ):
   class Keys:
      Canvas = "target_canvas"
      Color = "shape_color"
      VerticalOrientation = "vertical_orientation"
      HorizontalOrientation = "horizontal_orientation"
      Size = "shape_size"

   shape_color = ListProperty( [ 0, 0, 0, 1 ] )
   shape_vertical_orientation = OptionProperty( "center", options = [ "top", "center", "bottom" ] )
   shape_horizontal_orientation = OptionProperty( "center", options = [ "left", "center", "right" ] )
   shape_size = ListProperty( [ None, None ] )

   def _get_shape_size( self ):
      return ( self.shape_size[ 0 ], self.shape_size[ 1 ] )

   def _get_shape_orientation_excess( self ):
      if self.shape_size[ 0 ] is not None:
         horizontal_excess = self.width * ( 1 - self.shape_size[ 0 ] )
      else:
         horizontal_excess = 0

      if self.shape_size[ 1 ] is not None:
         vertical_excess = self.height * ( 1 - self.shape_size[ 1 ] )
      else:
         vertical_excess = 0

      return ( horizontal_excess, vertical_excess )

   def _get_shape_location( self ):
      size_hint = self._get_shape_size()
      horizontal_excess, vertical_excess = self._get_shape_orientation_excess()

      if horizontal_excess > 0:
         if self.shape_horizontal_orientation == "left":
            x_pos = self.x
         elif self.shape_horizontal_orientation == "right":
            x_pos = self.x + horizontal_excess
         else: # if self.shape_horizontal_orientation == "center"
            x_pos = self.x + horizontal_excess / 2
      else:
         x_pos = self.x

      if vertical_excess > 0:
         if self.shape_vertical_orientation == "top":
            y_pos = self.y + vertical_excess
         elif self.shape_vertical_orientation == "bottom":
            y_pos = self.y
         else: # if self.shape_vertical_orientation == "center"
            y_pos = self.y + vertical_excess / 2
      else:
         y_pos = self.y

      result = ( size_hint, { 'x' : x_pos, 'y' : y_pos } )
      return result

   def __init__( self, **kwargs ):
      target_canvas_value = DictOps.extract_optional_value( kwargs, BackgroundShapeMixin.Keys.Canvas, default_value = "normal" )
      initial_shape_color = DictOps.extract_optional_value( kwargs, BackgroundShapeMixin.Keys.Color )
      vertical_orientation = DictOps.extract_optional_value( kwargs, BackgroundShapeMixin.Keys.VerticalOrientation )
      horizontal_orientation = DictOps.extract_optional_value( kwargs, BackgroundShapeMixin.Keys.HorizontalOrientation )
      shape_size = DictOps.extract_optional_value( kwargs, BackgroundShapeMixin.Keys.Size )

      self.bind( shape_color = self._update_shape_properties, shape_vertical_orientation = self._update_shape_location, shape_horizontal_orientation = self._update_shape_location, shape_size = self._update_shape_properties )
      super( BackgroundShapeMixin, self ).__init__( **kwargs )

      self._target_canvas = self._get_canvas( target_canvas_value )

      self._initialized = False

      if initial_shape_color is not None:
         self.shape_color = initial_shape_color

      if vertical_orientation is not None:
         self.vertical_orientation = vertical_orientation

      if horizontal_orientation is not None:
         self.horizontal_orientation = horizontal_orientation

      if shape_size is not None:
         self.shape_size = shape_size

   def _get_shape( self, *args, **kwargs ):
      raise NotImplementedError( "Child must implement." )

   def _initialize_shape( self, initial_color, **kwargs ):
      self._color = initial_color

      self._shape = self._get_shape( **kwargs )
      self._target_canvas.add( self._color )
      self._target_canvas.add( self._shape )
      self.bind( size = self._update_shape_location, pos = self._update_shape_location )

      self._initialized = True

   def _render_canvas( self ):
      color = self._get_color( self.shape_color )

      if not self._initialized:
         self._initialize_shape( color )
      else:
         self._target_canvas.clear()

         self._color = color
         self._shape = self._get_shape()
         self._target_canvas.add( self._color )
         self._target_canvas.add( self._shape )

   def _update_shape_properties( self, instance, value ):
      self._render_canvas()

   def _update_shape_location( self, instance, value ):
      self._shape.pos = instance.pos
      self._shape.size = instance.size

class BackgroundEllipseMixin( BackgroundShapeMixin ):
   class Keys:
      Segments = "segments"
      AngleStart = "angle_start"
      AngleEnd = "angle_end"

   ellipse_segments = NumericProperty( 180 )
   ellipse_angle_start = NumericProperty( 0 )
   ellipse_angle_end = NumericProperty( 360 )

   def __init__( self, **kwargs ):
      segments = DictOps.extract_optional_value( kwargs, BackgroundEllipseMixin.Keys.Segments, int )
      angle_start = DictOps.extract_optional_value( kwargs, BackgroundEllipseMixin.Keys.AngleStart, int )
      angle_end = DictOps.extract_optional_value( kwargs, BackgroundEllipseMixin.Keys.AngleEnd, int )

      self.bind( ellipse_segments = self._update_shape_properties, ellipse_angle_start = self._update_shape_properties, ellipse_angle_end = self._update_shape_properties )
      super( BackgroundEllipseMixin, self ).__init__( **kwargs )

      if segments is not None:
         self.ellipse_segments = segments

      if angle_start is not None:
         self.ellipse_angle_start = angle_start

      if angle_end is not None:
         self.ellipse_angle_end = angle_end

   def _get_shape( self, *args, **kwargs ):
      size_hint, pos_hint = self._get_shape_location()

      result = Ellipse( size_hint = size_hint, pos_hint = pos_hint, segments = self.ellipse_segments, angle_start = self.ellipse_angle_start, angle_end = self.ellipse_angle_end, **kwargs )

      return result

class BackgroundCircleMixin( BackgroundEllipseMixin ):
   class Keys:
      Radius = "radius"

   circle_radius = BoundedNumericProperty( 1, min = 0., max = 1. )

   def __init__( self, **kwargs ):
      radius = DictOps.extract_optional_value( kwargs, BackgroundCircleMixin.Keys.Radius, float )

      self.bind( circle_radius = self._update_shape_properties )
      super( BackgroundCircleMixin, self ).__init__( **kwargs )

      if radius is not None:
         self.circle_radius = radius

   def _get_shape_size( self ):
      smaller_axis = min( self.width, self.height )
      radius = self.circle_radius * smaller_axis
      result = ( radius, radius )

      return result

   def _get_shape( self, *args, **kwargs ):
      size_hint, pos_hint = self._get_shape_location()

      result = Ellipse( size_hint = size_hint, pos_hint = pos_hint, **kwargs )

      return result

class BackgroundRectangleMixin( BackgroundShapeMixin ):
   def _get_shape( self, *args, **kwargs ):
      size_hint, pos_hint = self._get_shape_location()

      result = Rectangle( size_hint = size_hint, pos_hint = pos_hint, **kwargs )

      return result
