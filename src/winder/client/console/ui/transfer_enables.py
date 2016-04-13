from kivy.clock import Clock
from kivy.graphics import Ellipse, Rectangle
from kivy.uix.widget import Widget
from threading import Lock

from winder.client.console.ui.kivy_mixins import BackgroundColorMixin
from winder.utility.collections import DictOps
from winder.utility.machine_dimensions import WinderMachineDimensions, WinderMachinePositions

from .kivy_utilities import KivyUtilities

class _Positions( object ):
   _DomainStart_x = 0
   _DomainStart_y = 0
   _DomainEnd_x = 1
   _DomainEnd_y = 1

   _SideArea_width = .1
   _SideArea_height = .4
   _TopBottom_height = .1

   TransferBottom_start = ( _DomainStart_x, _DomainStart_y )
   TransferBottom_end = ( _DomainEnd_x, _TopBottom_height )
   TransferTop_start = ( TransferBottom_start[ 0 ], _DomainEnd_y - TransferBottom_end[ 1 ] )
   TransferTop_end = ( TransferBottom_end[ 0 ], _DomainEnd_y )
   TransferLeft_start = ( TransferBottom_start[ 0 ], TransferBottom_end[ 1 ] )
   TransferLeft_end = ( _SideArea_width, _SideArea_height + TransferLeft_start[ 1 ] )
   TransferRight_start = ( _DomainEnd_x - _SideArea_width, TransferLeft_start[ 1 ] )
   TransferRight_end = ( _DomainEnd_x, TransferLeft_end[ 1 ] )
   MountLeft_start = ( TransferLeft_start[ 0 ], TransferLeft_end[ 1 ] )
   MountLeft_end = ( TransferLeft_end[ 0 ], TransferTop_start[ 1 ] )
   MountRight_start = ( TransferRight_start[ 0 ], MountLeft_start[ 1 ] )
   MountRight_end = ( TransferRight_end[ 0 ], MountLeft_end[ 1 ] )
   Apa_start = ( TransferLeft_end[ 0 ], TransferBottom_end[ 1 ] )
   Apa_end = ( MountRight_start[ 0 ], MountRight_end[ 1 ] )

   _DomainStart = ( _DomainStart_x, _DomainStart_y )
   _DomainEnd = ( _DomainEnd_x, _DomainEnd_y )

   @staticmethod
   def get_size( start_pos, end_pos ):
      return ( end_pos[ 0 ] - start_pos[ 0 ], end_pos[ 1 ] - start_pos[ 1 ] )

class _Sizes( object ):
   TransferBottom = _Positions.get_size( _Positions.TransferBottom_start, _Positions.TransferBottom_end )
   TransferTop = _Positions.get_size( _Positions.TransferTop_start, _Positions.TransferTop_end )
   TransferLeft = _Positions.get_size( _Positions.TransferLeft_start, _Positions.TransferLeft_end )
   TransferRight = _Positions.get_size( _Positions.TransferRight_start, _Positions.TransferRight_end )
   MountLeft = _Positions.get_size( _Positions.MountLeft_start, _Positions.MountLeft_end )
   MountRight = _Positions.get_size( _Positions.MountRight_start, _Positions.MountRight_end )
   Apa = _Positions.get_size( _Positions.Apa_start, _Positions.Apa_end )

   Location = ( .1, .1 )

   _Domain = _Positions.get_size( _Positions._DomainStart, _Positions._DomainEnd )

class _Colors( object ):
   LocationColor = [ 0, 0, 1 ]
   ApaColor = [ .75, 0, .75, .5 ]
   TransferAllowed = [ 0, .75, 0, .5 ]
   TransferDisallowed = [ .5, .5, .5, .5 ]

   @staticmethod
   def apply_opacity( color, opacity ):
      red = color[ 0 ]
      green = color[ 1 ]
      blue = color[ 2 ]

      if len( color ) >= 4:
         alpha = color[ 3 ] * opacity
      else:
         alpha = opacity

      return [ red, green, blue, alpha ]

class _TransferRegionRectangle( object ):
   def __init__( self, displayed_position, displayed_size, represented_position, represented_size, region_name = None, **kwargs ):
      self.name = region_name
      self.displayed_position = displayed_position
      self.displayed_size = displayed_size

      self.represented_position = represented_position
      self.represented_size = represented_size

      super( _TransferRegionRectangle, self ).__init__( **kwargs )

   def get_color_value( self, current_location ):
      """
      The current location is in represented coordinates.
      """

      raise NotImplementedError( "Child must implement." )

   def get_color( self, current_location ):
      """
      The current location is in represented coordinates.
      """

      return KivyUtilities.get_color_from_value( self.get_color_value( current_location ) )

   def draw( self, canvas, canvas_offset, canvas_size, current_location ):
      canvas_width = canvas_size[ 0 ]
      canvas_height = canvas_size[ 1 ]

      position = [ self.displayed_start_x * canvas_width + canvas_offset[ 0 ], self.displayed_start_y * canvas_height + canvas_offset[ 1 ] ]
      size = [ self.displayed_width * canvas_width, self.displayed_height * canvas_height ]

      with canvas:
         self.get_color( current_location )
         Rectangle( pos = position, size = size )

   def draw_location( self, canvas, canvas_offset, canvas_size, represented_position, indicator_color, shape_class = None, **kwargs ):
      indicator_radius = min( [ _Sizes.Location[ 0 ] * canvas_size[ 0 ], _Sizes.Location[ 1 ] * canvas_size[ 1 ] ] )

      global_represented_position_ratio = ( float( represented_position[ 0 ] ) / WinderMachineDimensions.Width_abs_mm, float( represented_position[ 1 ] ) / WinderMachineDimensions.VerticalHeadSpace_abs_mm )
      canvas_position = ( global_represented_position_ratio[ 0 ] * canvas_size[ 0 ], global_represented_position_ratio[ 1 ] * canvas_size[ 1 ] )
      display_canvas_size = ( canvas_size[ 0 ] + 2 * indicator_radius, canvas_size[ 1 ] + 2 * indicator_radius )
      if self.is_point_in_rectangle( canvas_position, self.get_rectangle( display_canvas_size, ( -indicator_radius, -indicator_radius ) ) ):
         if shape_class is None:
            shape_class = Ellipse

         local_display_position = ( ( global_represented_position_ratio[ 0 ] - self.displayed_start_x ) / self.displayed_width, ( global_represented_position_ratio[ 1 ] - self.displayed_start_y ) / self.displayed_height )
         global_display_position = ( local_display_position[ 0 ] * self.displayed_width + self.displayed_start_x, local_display_position[ 1 ] * self.displayed_height + self.displayed_start_y )
         global_canvas_position = ( global_display_position[ 0 ] * canvas_size[ 0 ] + canvas_offset[ 0 ], global_display_position[ 1 ] * canvas_size[ 1 ] + canvas_offset[ 1 ] )

         indicator_canvas_size = [ indicator_radius ] * 2
         position = [ global_canvas_position[ 0 ] - indicator_canvas_size[ 0 ] / 2, global_canvas_position[ 1 ] - indicator_canvas_size[ 1 ] / 2 ]

         with canvas:
            KivyUtilities.get_color_from_value( indicator_color )
            shape_class( size = indicator_canvas_size, pos = position )

   def _get_displayed_width( self ):
      return self.displayed_size[ 0 ]

   displayed_width = property( fget = _get_displayed_width )

   def _get_displayed_height( self ):
      return self.displayed_size[ 1 ]

   displayed_height = property( fget = _get_displayed_height )

   def _get_displayed_start_point( self ):
      return self.displayed_position

   displayed_start_point = property( fget = _get_displayed_start_point )

   def _get_displayed_start_x( self ):
      return self.displayed_start_point[ 0 ]

   displayed_start_x = property( fget = _get_displayed_start_x )

   def _get_displayed_start_y( self ):
      return self.displayed_start_point[ 1 ]

   displayed_start_y = property( fget = _get_displayed_start_y )

   def _get_displayed_end_point( self ):
      x = self.displayed_start_x + self.displayed_width
      y = self.displayed_start_y + self.displayed_height

      return ( x, y )

   displayed_end_point = property( fget = _get_displayed_end_point )

   def _get_displayed_end_x( self ):
      return self.displayed_end_point[ 0 ]

   displayed_end_x = property( fget = _get_displayed_end_x )

   def _get_displayed_end_y( self ):
      return self.displayed_end_point[ 1 ]

   displayed_end_y = property( fget = _get_displayed_end_y )

   def get_rectangle( self, size, position = None ):
      if position is None:
         position = ( 0, 0 )

      return [ position[ 0 ], position[ 1 ], position[ 0 ] + size[ 0 ], position[ 1 ] + size[ 1 ] ]

   def is_point_in_rectangle( self, point, rectangle ):
      point_x = point[ 0 ]
      point_y = point[ 1 ]

      return point_x >= rectangle[ 0 ] and point_x <= rectangle[ 2 ] and point_y >= rectangle[ 1 ] and point_y <= rectangle[ 3 ]

   def contains_displayed_point( self, point ):
      x = point[ 0 ]
      y = point[ 1 ]

      result = x >= self.displayed_start_x and x <= self.displayed_end_x and y >= self.displayed_start_y and y <= self.displayed_end_y

      return result

   def _get_represented_width( self ):
      return self.represented_size[ 0 ]

   represented_width = property( fget = _get_represented_width )

   def _get_represented_height( self ):
      return self.represented_size[ 1 ]

   represented_height = property( fget = _get_represented_height )

   def _get_represented_start_point( self ):
      return self.represented_position

   represented_start_point = property( fget = _get_represented_start_point )

   def _get_represented_start_x( self ):
      return self.represented_position[ 0 ]

   represented_start_x = property( fget = _get_represented_start_x )

   def _get_represented_start_y( self ):
      return self.represented_position[ 1 ]

   represented_start_y = property( fget = _get_represented_start_y )

   def _get_represented_end_point( self ):
      x = self.represented_start_x + self.represented_width
      y = self.represented_start_y + self.represented_height

      return ( x, y )

   represented_end_point = property( fget = _get_represented_end_point )

   def _get_represented_end_x( self ):
      return self.represented_end_point[ 0 ]

   represented_end_x = property( fget = _get_represented_end_x )

   def _get_represented_end_y( self ):
      return self.represented_end_point[ 1 ]

   represented_end_y = property( fget = _get_represented_end_y )

   def contains_represented_point( self, point ):
      x = point[ 0 ]
      y = point[ 1 ]

      result = x >= self.represented_start_x and x <= self.represented_end_x and y >= self.represented_start_y and y <= self.represented_end_y

      return result

class _ImmutableTransferRegionRectangle( _TransferRegionRectangle ):
   def __init__( self, color, displayed_position, displayed_size, represented_position, represented_size, region_name = None, **kwargs ):
      self.color = color
      super( _ImmutableTransferRegionRectangle, self ).__init__( displayed_position, displayed_size, represented_position, represented_size, region_name, **kwargs )

   def get_color_value( self, current_location ):
      """
      The current location is in represented coordinates.
      """

      return self.color

class _MutableTransferRegionRectangle( _TransferRegionRectangle ):
   def __init__( self, in_color, out_color, displayed_position, displayed_size, represented_position, represented_size, region_name = None, **kwargs ):
      self.location_in_color = in_color
      self.location_out_color = out_color

      super( _MutableTransferRegionRectangle, self ).__init__( displayed_position, displayed_size, represented_position, represented_size, region_name, **kwargs )

   def get_color_value( self, current_location ):
      """
      The current location is in represented coordinates.
      """

      if current_location is not None and self.contains_represented_point( current_location ):
         result = self.location_in_color
      else:
         result = self.location_out_color

      return result

class TransferEnables( BackgroundColorMixin, Widget ):
   LocationBufferSize = 5

   def __init__( self, **kwargs ):
      self.bind( size = self._update_display, pos = self._update_display )

      super( TransferEnables, self ).__init__( **DictOps.dict_combine( kwargs, bg_color = [ 0, 0, 0 ] ) )

      self._construct( **kwargs )
      self._construct_locations( **kwargs )

      self._draw()

      self._schedule_polling( **kwargs )

   def _construct( self, **kwargs ):
      self.apa_area = _ImmutableTransferRegionRectangle( _Colors.ApaColor, _Positions.Apa_start, _Sizes.Apa, WinderMachinePositions.Apa_start_abs_mm, WinderMachineDimensions.ApaSpace_abs_mm, "APA" )
      self.transfer_bottom = _MutableTransferRegionRectangle( _Colors.TransferAllowed, _Colors.TransferDisallowed, _Positions.TransferBottom_start, _Sizes.TransferBottom, WinderMachinePositions.BottomTransfer_start_abs_mm, WinderMachineDimensions.BottomTransferSize_abs_mm, "Bottom Transfer" )
      self.transfer_top = _MutableTransferRegionRectangle( _Colors.TransferAllowed, _Colors.TransferDisallowed, _Positions.TransferTop_start, _Sizes.TransferTop, WinderMachinePositions.TopTransfer_start_abs_mm, WinderMachineDimensions.TopTransferSize_abs_mm, "Top Transfer" )
      self.transfer_left = _MutableTransferRegionRectangle( _Colors.TransferAllowed, _Colors.TransferDisallowed, _Positions.TransferLeft_start, _Sizes.TransferLeft, WinderMachinePositions.LeftTransfer_start_abs_mm, WinderMachineDimensions.SideTransferSize_abs_mm, "Left Transfer" )
      self.transfer_right = _MutableTransferRegionRectangle( _Colors.TransferAllowed, _Colors.TransferDisallowed, _Positions.TransferRight_start, _Sizes.TransferRight, WinderMachinePositions.RightTransfer_start_abs_mm, WinderMachineDimensions.SideTransferSize_abs_mm, "Right Transfer" )
      self.mount_left = _ImmutableTransferRegionRectangle( _Colors.TransferDisallowed, _Positions.MountLeft_start, _Sizes.MountLeft, WinderMachinePositions.LeftBracket_start_abs_mm, WinderMachineDimensions.BracketSize_abs_mm, "Left Bracket" )
      self.mount_right = _ImmutableTransferRegionRectangle( _Colors.TransferDisallowed, _Positions.MountRight_start, _Sizes.MountRight, WinderMachinePositions.RightBracket_start_abs_mm, WinderMachineDimensions.BracketSize_abs_mm, "Right Bracket" )

      self.regions = [ self.apa_area, self.transfer_left, self.transfer_right, self.transfer_top, self.transfer_bottom, self.mount_left, self.mount_right ]

   def _construct_locations( self, **kwargs ):
      self._locations_lock = Lock()
      self._locations = []
      self._locations_changed = False

   def _schedule_polling( self, **kwargs ):
      polling_period_sec = DictOps.extract_optional_value( kwargs, "polling_period", float, .75 )

      Clock.schedule_interval( self._clock_interval_expiration, polling_period_sec )

   def _clock_interval_expiration( self, dt ):
      self._update_display( None, None )

      return True # reschedule the timer event

   def _get_current_location( self ):
      with self._locations_lock:
         if len( self._locations ) > 0:
            result = self._locations[ -1 ]
         else:
            result = None

      return result

   current_location = property( fget = _get_current_location )

   def _draw( self, clear = True ):
      target_canvas = self.canvas

      if clear:
         target_canvas.clear()

      current_location = self.current_location
      for region in self.regions:
         region.draw( target_canvas, self.pos, self.size, current_location )

      with self._locations_lock:
         current_locations = self._locations
      self._draw_locations( current_locations, target_canvas, self.pos, self.size )

      self._locations_changed = False

   def _locate_region( self, machine_location, regions = None ):
      if regions is None:
         regions = self.regions

      result = None
      for region in regions:
         if region.contains_represented_point( machine_location ):
            result = region
            break

      return result

   def _draw_locations( self, locations, canvas, canvas_offset, canvas_size ):
      if len( locations ) > 0:
         opacity_increment = 1. / len( locations )

         current_opacity = opacity_increment
         for location in locations:
            region = self._locate_region( location )
            if region is not None:
               location_color_value = _Colors.apply_opacity( _Colors.LocationColor, current_opacity )
               region.draw_location( canvas, canvas_offset, canvas_size, location, location_color_value )

            current_opacity += opacity_increment

   def update_position( self, position ):
      # If the PLC is unavailable, the position is None.
      if position is not None:
         with self._locations_lock:
            if len( self._locations ) == 0 or position != self._locations[ -1 ]: # `self._locations[ -1 ]` is used instead of `self.current_location` to avoid deadlock.
               while len( self._locations ) >= self.LocationBufferSize:
                  self._locations.pop( 0 )

               self._locations.append( position )
               self._locations_changed = True
            elif len( self._locations ) > 1: # and position == self._locations[ -1 ]: # `self._locations[ -1 ]` is used instead of `self.current_location` to avoid deadlock.
               self._locations.pop( 0 ) # Incrementally expire the point history.

   def _update_display( self, instance, value ):
      self._draw()
