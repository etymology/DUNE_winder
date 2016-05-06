###############################################################################
# Name: WebServerInterface.py
# Uses: Web interface to remote system.
# Date: 2016-04-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import Cookie
import xml.sax.saxutils
import urllib
import uuid

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class WebServerInterface( SimpleHTTPRequestHandler ):

  # Global callback to run requested action.
  callback = None

  #---------------------------------------------------------------------
  def log_message( self, *_ ) :
    """
    Empty function to disable log messages.
    """
    pass

  #---------------------------------------------------------------------
  def do_POST( self ) :
    """
    Callback for an HTTP POST request.
    This will process all requests for data.
    """
    result = None

    sessionId = None

    # Get post data length.
    length = int( self.headers.getheader( 'content-length' ) )

    # Get cookie data.
    cookies = {}
    if "Cookie" in self.headers :
      cookieData = self.headers[ "Cookie" ]
      cookieData = cookieData.split( "&" )
      for cookie in cookieData :
        cookieName, cookieValue = cookie.split( "=" )
        cookies[ cookieName ] = cookieValue

    if "sessionId" in cookies :
      sessionId = cookies[ "sessionId" ]
    else :
      # If there isn't a session id, then make one.
      # $$$FUTURE: Initialize new session.
      sessionId = uuid.uuid1()
      cookies[ "sessionId" ] = sessionId

    # $$$FUTURE: Authenticate session before executing any commands.

    # Start XML result.
    self.send_response( 200 )

    cookieData = ""
    for cookieName in cookies :
      cookieValue = str( cookies[ cookieName ] )

      if "" != cookieData :
        cookieData += "&"

      cookieData = cookieName + "=" + cookieValue

    self.send_header( 'Set-Cookie', cookieData )
    self.send_header( 'Content-type', 'text/xml' )
    self.end_headers()
    self.wfile.write( '<?xml version="1.0" ?>' )
    self.wfile.write( '<ResultData>' )

    # Does request have parameters?
    if length > 0 :

      # Get post data.
      postData = self.rfile.read( length )

      #print postData

      # Split the data by commands.
      commands = postData.split( "&" )

      # For each command...
      for command in commands :

        # Break up the command.
        action, value = command.split( "=" )

        # Unquote the command.
        value = urllib.unquote_plus( value )

        callbackResult = WebServerInterface.callback( self, value )
        callbackResult = xml.sax.saxutils.escape( str( callbackResult ) )

        # Send results.
        self.wfile.write( "<" + action + ">" + str( callbackResult ) + "</" + action + ">" )

    # Close XML.
    self.wfile.write( '</ResultData>' )

    return result

# end class

if __name__ == "__main__":

  def callback( _, command ) :
    # Attempt to run command.
    result = None
    try :
      result = eval( command )
    except Exception :
      result = "Exception"

    return result

  WebServerInterface.callback = callback
  server_address = ( '', 80 )
  httpd = HTTPServer( server_address, WebServerInterface )

  print 'Starting httpd...'
  while True :
    httpd.handle_request()
