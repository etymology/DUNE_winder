from .base.theme import Theme

class UiTheme( Theme ):
   def __init__( self, file_location, theme_name, control_color, text_color, stage_color, pos_x_arrow, neg_x_arrow, pos_y_arrow, neg_y_arrow, pos_z_arrow, neg_z_arrow, *args, **kwargs ):
      super( UiTheme, self ).__init__( file_location, *args, **kwargs )

      self._set_name( theme_name )
      self._set_control_color( control_color )
      self._set_text_color( text_color )
      self._set_stage_color( stage_color )
      self._set_pos_x_arrow( pos_x_arrow )
      self._set_neg_x_arrow( neg_x_arrow )
      self._set_pos_y_arrow( pos_y_arrow )
      self._set_neg_y_arrow( neg_y_arrow )
      self._set_pos_z_arrow( pos_z_arrow )
      self._set_neg_z_arrow( neg_z_arrow )

   def _get_name( self ):
      return self._name

   def _set_name( self, value ):
      self._name = value

   name = property( fget = _get_name )

   def _get_control_color( self ):
      return self._control_color

   def _set_control_color( self, value ):
      self._control_color = value

   control_color = property( fget = _get_control_color )

   def _get_text_color( self ):
      return self._text_color

   def _set_text_color( self, value ):
      self._text_color = value

   text_color = property( fget = _get_text_color )

   def _set_stage_color( self, value ):
      self._stage_color = value

   def _get_pos_x_arrow( self ):
      return self._pos_x_arrow

   def _set_pos_x_arrow( self, value ):
      self._pos_x_arrow = value

   pos_x_arrow = property( fget = _get_pos_x_arrow )

   def _get_neg_x_arrow( self ):
      return self._neg_x_arrow

   def _set_neg_x_arrow( self, value ):
      self._neg_x_arrow = value

   neg_x_arrow = property( fget = _get_neg_x_arrow )

   def _get_pos_y_arrow( self ):
      return self._pos_y_arrow

   def _set_pos_y_arrow( self, value ):
      self._pos_y_arrow = value

   pos_y_arrow = property( fget = _get_pos_y_arrow )

   def _get_neg_y_arrow( self ):
      return self._neg_y_arrow

   def _set_neg_y_arrow( self, value ):
      self._neg_y_arrow = value

   neg_y_arrow = property( fget = _get_neg_y_arrow )

   def _get_pos_z_arrow( self ):
      return self._pos_z_arrow

   def _set_pos_z_arrow( self, value ):
      self._pos_z_arrow = value

   pos_z_arrow = property( fget = _get_pos_z_arrow )

   def _get_neg_z_arrow( self ):
      return self._neg_z_arrow

   def _set_neg_z_arrow( self, value ):
      self._neg_z_arrow = value

   neg_z_arrow = property( fget = _get_neg_z_arrow )
