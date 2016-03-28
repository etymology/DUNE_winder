import os.path
import re

class ThemeLoader( object ):
   """
   Reads a theme from file and constructs the corresponding Theme file.

   Child must implement:
   def _copy_from_loader( self, loader )
   def _validate( self )
   def _make_theme( self, *args, **kwargs )

   Child may implement:
   def _register_handlers( self )
   def _make_loader( self, target_path : str, *args, **kwargs )

   Handler Signatures:
   Directive: def _directive_handler( self, line_number : int, directive_id : str, directive_data : str ) -> None
   Key-Value Pair: def _key_handler( self, line_number : int, key : str, value : str ) -> None
   Comment: def _comment_handler( self, line_number : int, comment : str ) -> None

   Handler Registration:
   A handler with the key of None is the general handler.
   """

   class _RegularExpressions( object ):
      unquoted_path_string = r"\S*"
      single_quoted_path_string = r"'[^']*'"
      double_quoted_path_string = r'"[^"]*"'
      path_string_pattern = r"\s*(?P<path>(?:%s)|(?:%s)|(?:%s))\s*" % ( single_quoted_path_string, double_quoted_path_string, unquoted_path_string )

      directive_line_pattern = r"^\s*@(?P<id>[a-zA-Z_][a-zA-Z0-9_]*)\s*:(?P<data>.*)"
      key_value_pair_line_pattern = r"^\s*(?P<key>[a-zA-Z0-9_]+)\s*[=:](?P<value>.*)" # TODO: It would be nice to handle keys with spaces
      comment_line_pattern = r"^\s*(?P<token>[#;]+)(?P<value>.*)"

      _path_string_expression = None

      @staticmethod
      def get_path_string_expression():
         if ThemeLoader._RegularExpressions._path_string_expression is None:
            _path_string_expression = re.compile( ThemeLoader._RegularExpressions.path_string_pattern )

         return _path_string_expression

      _directive_line_expression = None

      @staticmethod
      def get_directive_line_expression():
         if ThemeLoader._RegularExpressions._directive_line_expression is None:
            _directive_line_expression = re.compile( ThemeLoader._RegularExpressions.directive_line_pattern )

         return _directive_line_expression

      _key_value_pair_line_expression = None

      @staticmethod
      def get_key_value_pair_line_expression():
         if ThemeLoader._RegularExpressions._key_value_pair_line_expression is None:
            _key_value_pair_line_expression = re.compile( ThemeLoader._RegularExpressions.key_value_pair_line_pattern )

         return _key_value_pair_line_expression

      _comment_line_expression = None

      @staticmethod
      def get_comment_line_expression():
         if ThemeLoader._RegularExpressions._comment_line_expression is None:
            _comment_line_expression = re.compile( ThemeLoader._RegularExpressions.comment_line_pattern )

         return _comment_line_expression

   _dq = '"'
   _sq = "'"

   @staticmethod
   def unquote_path( path ):
      if len( path ) >= 2 and path[ 0 ] == ThemeLoader._dq and path[ -1 ] == ThemeLoader._dq or path[ 0 ] == ThemeLoader._sq and path[ -1 ] == ThemeLoader._sq:
         result = path[ 1 :-1 ]
      else:
         result = path

      return result

   class Directives( object ):
      Import = "import"
      PushDirectory = "push_directory"
      PopDirectory = "pop_directory"

   def __init__( self, file_path, relative_to = None, *args, **kwargs ):
      super( ThemeLoader, self ).__init__( *args, **kwargs )
      self.clear()

      self._set_file_path( file_path )

      if isinstance( relative_to, ThemeLoader ):
         parent = relative_to
         relative_to = os.path.dirname( parent.file_path )
      else:
         parent = None

      self._set_relative_to_path( relative_to )
      self._set_parent_loader( parent )

      self._register_handlers()

   def _register_handlers( self ):
      self._directive_handlers = { None : self._general_directive_handler, ThemeLoader.Directives.Import : self._import_directive_handler, ThemeLoader.Directives.PushDirectory : self._push_dir_directive_handler, ThemeLoader.Directives.PopDirectory : self._pop_dir_directive_handler }
      self._key_handlers = { None : self._general_key_handler }
      self._comment_handlers = { None : self._general_comment_handler }

   def _get_file_path( self ):
      return self._file_path

   def _set_file_path( self, value ):
      self._file_path = value

   file_path = property( fget = _get_file_path )

   def _get_relative_to_path( self ):
      return self._relative_to_path

   def _set_relative_to_path( self, value ):
      self._relative_to_path = value

   relative_to_path = property( fget = _get_relative_to_path )

   def _get_parent_loader( self ):
      return self._parent_loader

   def _set_parent_loader( self, value ):
      self._parent_loader = value

   parent = property( fget = _get_parent_loader )

   def _get_has_parent( self ):
      return self.parent is not None

   has_parent = property( fget = _get_has_parent )

   def _get_import_chain( self ):
      result = []

      loader = self
      # May be more performant if the parents were appended to a list, then after the loop `result = reversed( <list> )`.
      while loader.has_parent:
         result.insert( 0, loader.file_path )
         loader = loader.parent

      return result

   import_chain = property( fget = _get_import_chain )

   def _get_loaded_theme( self ):
      if not self.has_loaded:
         self.load()

      return self._loaded_theme

   def _set_loaded_theme( self, value ):
      self._loaded_theme = value

   theme = property( fget = _get_loaded_theme )

   def _get_has_loaded( self ):
      return self._loaded_theme is not None

   has_loaded = property( fget = _get_has_loaded )

   def _get_directory_stack( self ):
      return self._directory_stack

   def _set_directory_stack( self, value ):
      self._directory_stack = value

   directory_stack = property( fget = _get_directory_stack )

   def _get_current_directory( self ):
      return self.directory_stack[ -1 ]

   current_directory = property( fget = _get_current_directory )

   def _import_directive_handler( self, line_number, directive_id, directive_data ):
      target_path = directive_data.strip()

      match = ThemeLoader.RegularExpressions.get_path_string_expression().match( target_path )
      if match is not None:
         target_path = os.path.normcase( os.path.normpath( ThemeLoader._unquote_path( match.group( "path" ) ) ) )

         if not os.path.isabs( target_path ):
            target_path = os.path.normcase( os.path.normpath( os.path.join( self.current_directory, target_path ) ) )

         imported_theme_loader = self._make_loader( target_path )
         self._copy_from_loader( imported_theme_loader.theme )
      else:
         raise ValueError( "Malformed import path '%s' on line %d." % ( target_path, line_number ) )

   def _push_dir_directive_handler( self, line_number, directive_id, directive_data ):
      target_path = directive_data.strip()

      match = ThemeLoader._RegularExpressions.get_path_string_expression().match( target_path )
      if match is not None:
         target_path = os.path.normcase( os.path.normpath( ThemeLoader.unquote_path( match.group( "path" ) ) ) )

         if not os.path.isabs( target_path ):
            target_path = os.path.normcase( os.path.normpath( os.path.join( self.current_directory, target_path ) ) )

         self.directory_stack.append( target_path )
      else:
         raise ValueError( "Malformed push directive '%s' on line %d." % ( target_path, line_number ) )

   def _pop_dir_directive_handler( self, line_number, directive_id, directive_data ):
      if len( self.directory_stack ) > 1:
         self.directory_stack.pop()
      else:
         raise ValueError( "Unable to process pop directory directive on line '%d'." % line_number )

   def _make_loader( self, target_path, *args, **kwargs ):
      return ThemeLoader( target_path, self, *args, **kwargs )

   def _general_directive_handler( self, line_number, directive_id, directive_data ):
      raise ValueError( "Directive '%s' on line %d is not supported." % ( directive_id, line_number ) )

   def _general_key_handler( self, line_number, key, value ):
      raise ValueError( "Key '%s' on line %d is not supported." % ( key, line_number ) )

   def _general_comment_handler( self, line_number, comment ):
      pass # Comments are by default ignored.

   def _get_directive_handler( self, directive = None, general_fallback = True ):
      return self._get_handler( self._directive_handlers, directive, general_fallback )

   def _get_key_handler( self, key = None, general_fallback = True ):
      return self._get_handler( self._key_handlers, key, general_fallback )

   def _get_comment_handler( self, comment_id = None, general_fallback = True ):
      return self._get_handler( self._comment_handlers, comment_id, general_fallback )

   def _get_handler( self, handler_map, handler_key, general_fallback = True ):
      result = None

      if handler_key in handler_map:
         result = handler_map[ handler_key ]
      elif general_fallback and handler_key is not None and None in handler_map: # check for the general handler
         result = handler_map[ None ]

      return result

   def _copy_from_loader( self, loader ):
      """
      Copies the relevant values from the given loader into the current instance.

      Returns: <None>
      """

      raise NotImplementedError( "Child is required to implement." )

   def load( self, reload_theme = False ):
      """
      Parses the given theme file and loads the data into memory.

      Returns: True if the file was loaded, False otherwise.
      """

      result = False

      if reload_theme:
         self.clear()

      if self.file_path is None:
         raise ValueError( "Theme file path cannot be None." )
      elif not self.has_loaded:
         path = os.path.normcase( os.path.normpath( self.file_path ) )

         if not os.path.isabs( path ):
            if self.relative_to_path is None:
               relative_to_path = os.getcwd()
            else:
               relative_to_path = self.relative_to_path
            path = os.path.join( relative_to_path, path )

         if os.path.exists( path ):
            if os.path.isfile( path ):
               if path not in self.import_chain:
                  self._set_file_path( path )
                  self._process_file()

                  result = self._validate()
                  if result:
                     self._set_loaded_theme( self._make_theme() )
               else:
                  raise ValueError( "Circular import chain detected: %s" % " -> ".join( map( lambda s: "'%s'" % s, self.import_chain + [ path ] ) ) )
            else:
               raise IOError( "Theme file path '%s' is not a file." % path )
         else:
            raise IOError( "Theme file path '%s' does not exist." % path )

      return result

   def _validate( self ):
      """
      Validates the data after processing the file.

      Returns: True if the data is valid, False otherwise.
      """

      raise NotImplementedError( "Child is required to implement." )

   def _process_file( self ):
      with open( self.file_path, "r" ) as f:
         self._set_directory_stack( [ os.path.dirname( self.file_path ) ] )

         line_number = 0
         for line in f:
            line = line.rstrip( '\n' )

            line_number += 1

            match = ThemeLoader._RegularExpressions.get_directive_line_expression().match( line )
            if match is not None:
               directive_id = match.group( "id" )
               directive_data = match.group( "data" )

               handler = self._get_directive_handler( directive_id )
               if handler is not None:
                  handler( line_number, directive_id, directive_data )
            else:
               match = ThemeLoader._RegularExpressions.get_key_value_pair_line_expression().match( line )
               if match is not None:
                  key = match.group( "key" )
                  value = match.group( "value" )

                  handler = self._get_key_handler( key )
                  if handler is not None:
                     handler( line_number, key, value )
               else:
                  match = ThemeLoader._RegularExpressions.get_comment_line_expression().match( line )
                  if match is not None:
                     comment = match.group( "value" )

                     handler = self._get_comment_handler( comment )
                     if handler is not None:
                        handler( line_number, comment )
                  elif len( line.strip() ) > 0: # ignore empty lines
                     raise ValueError( "Malformed line in theme file at line %d." % line_number )

   def reload( self ):
      return self.load( True )

   def clear( self ):
      self._set_loaded_theme( None )

   def _make_theme( self, *args, **kwargs ):
      """
      Constructs the loaded Theme object.

      Returns: the constructed Theme object.
      """

      raise NotImplementedError( "Child is required to implement." )
