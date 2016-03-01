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
