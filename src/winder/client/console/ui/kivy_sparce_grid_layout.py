from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from .kivy_image_button import ImageButton
from .kivy_labelled_checkbox import LabelledCheckbox

class SparseGridLayout( FloatLayout ):
   rows = NumericProperty( 1 )
   columns = NumericProperty( 1 )
   shape = ReferenceListProperty( rows, columns )

   def __init__( self, **kwargs ):
      super( SparseGridLayout, self ).__init__( **kwargs )

   def do_layout( self, *args ):
      shape_hint = ( 1. / self.columns, 1. / self.rows )
      for child in self.children:
         child_size_hint = ( shape_hint[ 0 ] * child.column_span, shape_hint[ 1 ] * child.row_span )

         child.size_hint = child_size_hint
         if not hasattr( child, 'row' ):
            child.row = 0
         if not hasattr( child, 'column' ):
            child.column = 0

         child.pos_hint = { 'x': shape_hint[ 0 ] * child.column, 'y': shape_hint[ 1 ] * child.row }

      super( SparseGridLayout, self ).do_layout( *args )

class GridEntry( EventDispatcher ):
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

class GridLabel( Label, GridEntry ):
   pass

class GridButton( Button, GridEntry ):
   pass

class GridImage( Image, GridEntry ):
   pass

class GridImageButton( ImageButton, GridEntry ):
   pass

class GridCheckbox( CheckBox, GridEntry ):
   pass

class GridLabelledCheckbox( LabelledCheckbox, GridEntry ):
   pass
