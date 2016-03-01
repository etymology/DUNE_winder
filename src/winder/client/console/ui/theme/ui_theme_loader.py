import os.path
import re

from .base.theme_loader import ThemeLoader
from .ui_theme import UiTheme

class UiThemeLoader( ThemeLoader ):
   def __init__( self, file_path, relative_to = None, *args, **kwargs ):
      super( UiThemeLoader, self ).__init__( file_path, relative_to, *args, **kwargs )

   def _register_handlers( self ):
      super( UiThemeLoader, self )._register_handlers()

      self._key_handlers[ "name" ] = self._name_key_handler
      self._key_handlers[ "text_color" ] = self._text_color_key_handler
      self._key_handlers[ "control_color" ] = self._control_color_key_handler
      self._key_handlers[ "stage_color" ] = self._stage_color_key_handler
      self._key_handlers[ "pos_x_arrow" ] = self._pos_x_arrow_key_handler
      self._key_handlers[ "neg_x_arrow" ] = self._neg_x_arrow_key_handler
      self._key_handlers[ "pos_y_arrow" ] = self._pos_y_arrow_key_handler
      self._key_handlers[ "neg_y_arrow" ] = self._neg_y_arrow_key_handler
      self._key_handlers[ "pos_z_arrow" ] = self._pos_z_arrow_key_handler
      self._key_handlers[ "neg_z_arrow" ] = self._neg_z_arrow_key_handler

   def _make_loader( self, target_path, *args, **kwargs ):
      return UiThemeLoader( target_path, self, *args, **kwargs )

   def _copy_from_loader( self, loader ):
      self.name = loader.name
      self.text_color = loader.text_color
      self.control_color = loader.control_color
      self.stage_color = loader.stage_color
      self.pos_x_arrow = loader.pos_x_arrow
      self.neg_x_arrow = loader.neg_x_arrow
      self.pos_y_arrow = loader.pos_y_arrow
      self.neg_y_arrow = loader.neg_y_arrow
      self.pos_z_arrow = loader.pos_z_arrow
      self.neg_z_arrow = loader.neg_z_arrow

   def _validate( self ):
      return self._does_attr_have_value( "name" ) and self._does_attr_have_value( "text_color" )and self._does_attr_have_value( "control_color" )and self._does_attr_have_value( "stage_color" )and self._does_attr_have_value( "pos_x_arrow" )and self._does_attr_have_value( "neg_x_arrow" )and self._does_attr_have_value( "pos_y_arrow" )and self._does_attr_have_value( "neg_y_arrow" )and self._does_attr_have_value( "pos_z_arrow" )and self._does_attr_have_value( "neg_z_arrow" )

   def _does_attr_have_value( self, attr_name ):
      return hasattr( self, attr_name ) and eval( "self.%s is not None" % attr_name )

   def _make_theme( self, *args, **kwargs ):
      result = UiTheme( self.file_path, self.name, self.control_color, self.text_color, self.stage_color, self.pos_x_arrow, self.neg_x_arrow, self.pos_y_arrow, self.neg_y_arrow, self.pos_z_arrow, self.neg_z_arrow )

      return result

   _float_pattern = "(?:\d+(?:\.\d*)?)|(?:\.\d+)"

   _color_pattern = r"\s*\(?\s*(?P<red>%s)\s*,\s*(?P<green>%s)\s*,\s*(?P<blue>%s)\s*(?:,\s*(?:(?P<opacity>%s)\s*)?)?(?:\)\s*)?" % ( _float_pattern, _float_pattern, _float_pattern, _float_pattern )

   _color_expression = None

   def _get_color_expression( self ):
      if self._color_expression is None:
         self._color_expression = re.compile( self._color_pattern )

      return self._color_expression

   def _get_color_component_value( self, line_number, value, tolerance = 0.001 ):
      lower_bound = 0
      upper_bound = 1

      result = float( value )

      if result < ( lower_bound - tolerance ) or result > ( upper_bound + tolerance ):
         raise ValueError( "Color component value %f on line %d is out of range." % ( result, line_number ) )
      elif result < lower_bound:
         result = lower_bound
      elif result > upper_bound:
         result = upper_bound

      return result

   def _get_color_value( self, line_number, color_string ):
      match = self._get_color_expression().match( color_string )

      if match is not None:
         matches = match.groupdict()

         red = self._get_color_component_value( line_number, matches[ "red" ] )
         green = self._get_color_component_value( line_number, matches[ "green" ] )
         blue = self._get_color_component_value( line_number, matches[ "blue" ] )

         opacity_string = matches[ "opacity" ]
         if opacity_string is None:
            opacity = 1.0
         else:
            opacity = self._get_color_component_value( line_number, opacity_string )

         result = ( red, green, blue, opacity )

         return result
      else:
         raise ValueError( "Invalid color string '%s' on line %d." % ( color_string.strip(), line_number ) )

   def _get_image_path( self, line_number, path ):
      match = self._RegularExpressions.get_path_string_expression().match( path )
      if match is not None:
         path = os.path.normcase( os.path.normpath( ThemeLoader.unquote_path( match.group( "path" ) ) ) )

         if not os.path.isabs( path ):
            path = os.path.normcase( os.path.normpath( os.path.join( self.current_directory, path ) ) )

         if not os.path.exists( path ):
            raise ValueError( "Image path '%s' on line %d does not exist." % ( path, line_number ) )
         else:
            return path
      else:
         raise ValueError( "Malformed image path '%s' on line %d." % ( path, line_number ) )

   def _name_key_handler( self, line_number, key, value ):
      self.name = value.strip()

   def _text_color_key_handler( self, line_number, key, value ):
      self.text_color = self._get_color_value( line_number, value )

   def _control_color_key_handler( self, line_number, key, value ):
      self.control_color = self._get_color_value( line_number, value )

   def _stage_color_key_handler( self, line_number, key, value ):
      self.stage_color = self._get_color_value( line_number, value )

   def _pos_x_arrow_key_handler( self, line_number, key, value ):
      self.pos_x_arrow = self._get_image_path( line_number, value )

   def _neg_x_arrow_key_handler( self, line_number, key, value ):
      self.neg_x_arrow = self._get_image_path( line_number, value )

   def _pos_y_arrow_key_handler( self, line_number, key, value ):
      self.pos_y_arrow = self._get_image_path( line_number, value )

   def _neg_y_arrow_key_handler( self, line_number, key, value ):
      self.neg_y_arrow = self._get_image_path( line_number, value )

   def _pos_z_arrow_key_handler( self, line_number, key, value ):
      self.pos_z_arrow = self._get_image_path( line_number, value )

   def _neg_z_arrow_key_handler( self, line_number, key, value ):
      self.neg_z_arrow = self._get_image_path( line_number, value )
