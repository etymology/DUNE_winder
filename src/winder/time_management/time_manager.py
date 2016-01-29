from datetime import datetime

class TimeManager( object ):
   def get_current_time_utc( self ):
      return datetime.utcnow()

   current_time_utc = property( fget = get_current_time_utc )

   def get_time_format( self ):
      return "%Y-%m-%d %H:%M:%S.%f"

   time_format = property( fget = get_time_format )

   def format_time( self, time ):
      return time.strftime( self.time_format )

   def get_formatted_current_time_utc( self ):
      return self.format_time( self.current_time_utc )

   formatted_current_time_utc = property( fget = get_formatted_current_time_utc )
