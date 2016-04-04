from sets import Set

class DictOps:
   @staticmethod
   def dict_combine( original, additional = None, **kwargs ):
      """
      Combines all of the key-value pairs in all dictionaries into a single, new dictionary.

      The order of combination is: original, additional, kwargs. Any key collisions result in the latter-processed pair taking precedence.
      """

      result = {}

      sources = [ source for source in [ original, additional, kwargs ] if source is not None ]
      for source in sources:
         for key in source:
            result[ key ] = source[ key ]

      return result

   @staticmethod
   def dict_filter( source, filter_keys = None, *args ):
      keys = Set()

      filter_key_lists = [ l for l in [ filter_keys, args ] if l is not None ]
      for l in filter_key_lists:
         for item in l:
            keys.add( item )

      result = { key: source[ key ] for key in source if key not in keys }

      return result

   @staticmethod
   def extract_necessary_value( dictionary, key, conversion_function = None, remove_value = True ):
      return DictOps.extract_dictionary_value( dictionary, key, True, conversion_function, remove_value )

   @staticmethod
   def extract_optional_value( dictionary, key, conversion_function = None, default_value = None, remove_value = True ):
      return DictOps.extract_dictionary_value( dictionary, key, False, conversion_function, default_value, remove_value )

   @staticmethod
   def extract_dictionary_value( dictionary, key, value_required, conversion_function = None, default_value = None, remove_value = True ):
      if dictionary is not None:
         if key in dictionary:
            base_value = dictionary[ key ]

            if remove_value:
               del dictionary[ key ]

            if conversion_function is not None:
               result = conversion_function( base_value )
            else:
               result = base_value
         else:
            if value_required:
               raise ValueError( "Key '{}' does not exist in dictionary.".format( key ) )
            else:
               result = default_value
      else:
         raise ValueError( "Input dictionary cannot be None." )

      return result
