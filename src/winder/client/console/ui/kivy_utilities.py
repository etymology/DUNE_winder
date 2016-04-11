from kivy.graphics import Color

class KivyUtilities( object ):
   @staticmethod
   def add_children_to_widget( widget, children = None, *args ):
      new_children = []
      if children is not None:
         new_children.extend( children )

      if args is not None:
         new_children.extend( args )

      for child in new_children:
         widget.add_widget( child )

   @staticmethod
   def get_color_from_value( value ):
      color_component_count = len( value )

      if color_component_count == 3:
         result = Color( value[ 0 ], value[ 1 ], value[ 2 ] )
      elif color_component_count == 4:
         result = Color( value[ 0 ], value[ 1 ], value[ 2 ], value[ 3 ] )
      else:
         raise Exception( "Invalid color: {}".format( str( value ) ) )

      return result
