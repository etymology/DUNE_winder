from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout

# KLUDGE: BUG: An error in FloatLayout (patch from in https://github.com/kivy/kivy/pull/4200) prevents using a size_hint of zero to hide an item, so hiding is done by moving the child off of the viewable area.

class DisplaySelectionLayout( RelativeLayout ):
#    _size_hint_zero = 0.00001

   def __init__( self, initial_children = None, **kwargs ):
      self._default_id = 0
      self.children_map = {}

      self.bind( selected_id = self._update_selected_id )
      super( DisplaySelectionLayout, self ).__init__( **kwargs )

      if initial_children is not None:
         for child in initial_children:
            self.add_widget( child )

   selected_id = ObjectProperty( None )

   def _get_selected_child( self ):
      return self.children_map[ self.selected_id]

   selected_item = property( fget = _get_selected_child )

   def _get_next_default_id( self ):
      result = self._default_id

      self._default_id += 1

      return result

   def add_widget( self, widget, widget_id = None, index = 0, suppress_exceptions = False ):
      if widget_id is None:
         new_widget_id = self._get_next_default_id()

         while new_widget_id in self.children_map:
            new_widget_id = self._get_next_default_id()
      else:
         new_widget_id = widget_id

      if new_widget_id in self.children_map:
         if not suppress_exceptions:
            raise ValueError( "Unable to add widget because the given ID already exists." )
         else:
            result = None
      else:
         self.children_map[ new_widget_id ] = widget

         super( DisplaySelectionLayout, self ).add_widget( widget, index = index )

         result = new_widget_id

         if self.selected_id == None:
            self.selected_id = result
         else:
#             widget.size_hint = [ self._size_hint_zero, self._size_hint_zero ]
            self._hide_widget( widget )

      return result

   def clear_widgets( self, children = None ):
      self.children_map.clear()

      super( DisplaySelectionLayout, self ).clear_widgets( self, children = children )

   def _get_widget_ids( self ):
      return sorted( self.children_map.keys() )

   ids = property( fget = _get_widget_ids )

   def _select_adjacent( self, direction_is_next = True, target_id = None ):
      ids = self.ids

      if len( ids ) > 0:
         if target_id is None:
            target_id = self.selected_id

         try:
            index = ids.index( target_id )
         except ValueError:
            raise ValueError( "The target ID '{}' does not exist.".format( str( target_id ) ) )
         else:
            if direction_is_next:
               new_index = ( index + 1 ) % len( ids )
            else:
               new_index = ( index - 1 + len( ids ) ) % len( ids )

            result = ids[ new_index ]
            self.selected_id = result
      else:
         result = None

      return result

   def select_next( self, target_id = None ):
      return self._select_adjacent( True, target_id )

   def select_previous( self, target_id = None ):
      return self._select_adjacent( False, target_id )

   def _update_selected_id( self, instance, value ):
      for key in self.children_map:
         item = self.children_map[ key ]

         if value == key:
#             size_hint = [ 1., 1. ]
            self._show_widget( item )
         else:
#             size_hint = [ self._size_hint_zero, self._size_hint_zero ]
            self._hide_widget( item )

#          item.size_hint = size_hint

   def _show_widget( self, widget ):
      widget.pos_hint = { 'x': 0, 'y': 0 }

   def _hide_widget( self, widget ):
      widget.pos_hint = { 'x':-2 * widget.width, 'y':-2 * widget.height }
