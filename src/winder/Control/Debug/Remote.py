###############################################################################
# Name: Remote.py
# Uses: Some remote I/O commands to the control server.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

class Remote :
  #---------------------------------------------------------------------
  def getIO( self, ioPoint ) :
    return self.remote( ioPoint + ".get()" )

  #---------------------------------------------------------------------
  def setIO( self, ioPoint, state, event ) :
    self.remote( ioPoint + ".set( " + str( state ) + " )" )
    event.Skip()

  #---------------------------------------------------------------------
  def __init__( self, remote ) :
    self.remote = remote

  #---------------------------------------------------------------------
  def isFloat( self, value ):
    result = True
    try:
      float( value )
    except ValueError :
      result = False

    return result

  #---------------------------------------------------------------------
  def remoteFloat( self, tag, formating ) :
    result = "--"
    value = self.remote( tag )
    if ( self.isFloat( value ) ) :
      value = float( value )
      result = formating.format( value )

      # Round -0.00 to 0.00.
      if 0 == float( result ) :
        result = formating.format( 0.0 )

    return result

