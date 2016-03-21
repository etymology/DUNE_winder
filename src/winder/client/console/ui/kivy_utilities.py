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
