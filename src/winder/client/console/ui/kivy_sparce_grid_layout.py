from kivy.event import EventDispatcher
from kivy.properties import ListProperty, NumericProperty, ReferenceListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from .kivy_image_button import ImageButton
from .kivy_labelled_checkbox import LabelledCheckbox
from .kivy_mixins import BackgroundColorMixin
from .kivy_shape_widgets import EllipseWidget, RectangleWidget


class SparseGridLayout( BackgroundColorMixin, FloatLayout ):
   """
   Cell Properties:
   Cell properties are properties which describe a property which affects the sides of the grid layout. It is a list property which can have 1, 2, or 4 values:
      1: value will be used as spacing for all sides
      2: first value is horizontal spacing, second value is vertical spacing
      4: [ left spacing, top spacing, right spacing, bottom spacing ]
   Each value component has a range of [0, 1].

   Properties:
   'rows': number of rows in the grid, defaults to 1
   'columns': number of columns in the grid, defaults to 1
   'grid_size': ( 'rows', 'columns' )
   'spacing': spacing between the children, it is a cell property
   'padding': the grid's spacing in relation to its external components
   """

   rows = NumericProperty( 1 )
   columns = NumericProperty( 1 )
   grid_size = ReferenceListProperty( rows, columns )
   spacing = ListProperty( [ 0 ] )
   padding = ListProperty( [ 0 ] )

   def __init__( self, **kwargs ):
      super( SparseGridLayout, self ).__init__( **kwargs )

   def _get_cell_property_values( self, prop ):
      property_length = len( prop )
      if property_length == 1:
         value = prop[ 0 ]

         result = [ value ] * 4
      elif property_length == 2:
         horizontal_value = prop[ 0 ]
         vertical_value = prop[ 1 ]

         result = [ horizontal_value, vertical_value ] * 2
      elif property_length == 4:
         left_value = prop[ 0 ]
         top_value = prop[ 1 ]
         right_value = prop[ 2 ]
         bottom_value = prop[ 3 ]

         result = [ left_value, top_value, right_value, bottom_value ]
      else:
         raise ValueError( "Property length is invalid." )

      return result

   def do_layout( self, *args, **kwargs ):
      grid_padding = self._get_cell_property_values( self.padding )

      left_padding = grid_padding[ 0 ]
      top_padding = grid_padding[ 1 ]
      right_padding = grid_padding[ 2 ]
      bottom_padding = grid_padding[ 3 ]

      horizontal_padding = left_padding + right_padding
      vertical_padding = top_padding + bottom_padding

      inner_width = 1. - horizontal_padding
      inner_height = 1. - vertical_padding

      grid_spacing = self._get_cell_property_values( self.spacing )

      left_spacing = grid_spacing[ 0 ]
      top_spacing = grid_spacing[ 1 ]
      right_spacing = grid_spacing[ 2 ]
      bottom_spacing = grid_spacing[ 3 ]

      vertical_spacing = top_spacing + bottom_spacing
      horizontal_spacing = left_spacing + right_spacing

      cell_width = 1. / self.columns
      cell_height = 1. / self.rows

      for child in self.children:
         if not hasattr( child, GridEntry.FieldNames.Row ):
            child.row = 0
         if not hasattr( child, GridEntry.FieldNames.Column ):
            child.column = 0
         if not hasattr( child, GridEntry.FieldNames.ColumnSpan ):
            child.column_span = 1
         if not hasattr( child, GridEntry.FieldNames.RowSpan ):
            child.row_span = 1

         # The children sizes are scaled by the inner width and inner height as influenced by the padding.
         width = ( cell_width * child.column_span - horizontal_spacing ) * inner_width
         height = ( cell_height * child.row_span - vertical_spacing ) * inner_height
         child_size_hint = ( width, height )

         child.size_hint = child_size_hint

         # The row and column indicies are zero-based.
         x_pos = ( cell_width * child.column + left_spacing ) * inner_width + left_padding
         y_pos = ( cell_height * child.row + bottom_spacing ) * inner_height + bottom_padding
         child.pos_hint = { 'x': x_pos, 'y': y_pos }

      super( SparseGridLayout, self ).do_layout( *args, **kwargs )

class GridEntry( BackgroundColorMixin, EventDispatcher ):
   class FieldNames:
      Row = "row"
      Column = "column"
      RowSpan = "row_span"
      ColumnSpan = "column_span"

      all = [ Row, Column, RowSpan, ColumnSpan ]

   row = NumericProperty( 0 )
   column = NumericProperty( 0 )
   row_span = NumericProperty( 1 )
   column_span = NumericProperty( 1 )

class GridLabel( GridEntry, Label ):
   pass

class GridButton( GridEntry, Button ):
   pass

class GridImage( GridEntry, Image ):
   pass

class GridImageButton( GridEntry, ImageButton ):
   pass

class GridCheckbox( GridEntry, CheckBox ):
   pass

class GridLabelledCheckbox( GridEntry, LabelledCheckbox ):
   pass

class GridBoxLayout( GridEntry, BoxLayout ):
   pass

class GridRectangle( GridEntry, RectangleWidget ):
   pass

class GridEllipse( GridEntry, EllipseWidget ):
   pass

class GridTextInput( GridEntry, TextInput ):
   pass
