###############################################################################
# Name: WebServerInterface.py
# Uses: Web interface to remote system.
# Date: 2016-04-29
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import http.cookies
import xml.sax.saxutils
import urllib.request, urllib.parse, urllib.error
import uuid
import json
import re

from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from Library.RemoteSession import RemoteSession

class WebServerInterface( SimpleHTTPRequestHandler ):

  # $$$FUTURE - If we decide to use authentication, this must change.
  BYPASS_AUTHENTICATION = True

  # Queries an unauthenticated client can issue.
  # Regular expression.  Includes "get", "is", and none-functional
  # queries only--queries that change nothing but just return data.
  BASIC_QUERIES = \
     r"(\.get[A-Za-z0-9_]*\(.*\)$)" \
   + "|(\.is[A-Za-z0-9_]*\(.*\)$)"  \
   + "|(^[A-Za-z0-9_.]+)$"

  # Global callback to run requested action.
  callback = None

  #---------------------------------------------------------------------
  def log_message( self, *_ ) :
    """
    Empty function to disable log messages.
    """
    pass

  #---------------------------------------------------------------------
  def _send( self, tag, data ) :
    """
    Send an XML field back to client.  Private.

    Args:
      tag: Name of tag to encapsulate data.
      data: Data associated with tag.
    """
    try:
        data = xml.sax.saxutils.escape(str(data))
        data = "<" + tag + ">" + str(data) + "</" + tag + ">"
        self.wfile.write(data)
    except Exception as e:
        print("Error occurred while sending data:", e)

  #---------------------------------------------------------------------
  def _JSON_send( self, tag, data ) :
    """
    Encode data in JSON string and send to client.  Private.

    Args:
      tag: Name of tag to encapsulate data.
      data: Data associated with tag.
    """
    data = json.dumps( data )
    self._send( tag, data )

  #---------------------------------------------------------------------
  def do_POST( self ) :
    """
    Callback for an HTTP POST request.
    This will process all requests for data.
    """

    result = None

    # Get post data length.
    length = int(self.headers.get('content-length'))
    # Get cookie data.
    cookies = {}
    if "Cookie" in self.headers :
      cookieData = self.headers[ "Cookie" ]
      cookieData = cookieData.split( "; " )
      for cookie in cookieData :
        cookieName, cookieValue = cookie.split( "=" )
        cookies[ cookieName ] = cookieValue

    # Get session identification.
    sessionId = None
    if "sessionId" in cookies :
      sessionId = cookies[ "sessionId" ]

    # Find or create session.
    session = RemoteSession.sessionSetup( sessionId )
    sessionId = session.getId()
    cookies[ "sessionId" ] = sessionId

    # If the client address is a loop-back (i.e. the local machine) then
    # it by default is authenticated.
    clientAddress = self.client_address[ 0 ]
    if re.search( "127\.[0-9]+\.[0-9]+\.[0-9]+", clientAddress ) \
      or WebServerInterface.BYPASS_AUTHENTICATION :
      session.setAuthenticated( True )

    # Check to see if session is authenticated.
    isAuthenticated = session.getAuthenticated()

    # Start XML result.
    self.send_response( 200 )

    # Construct cookie data to send back.
    for cookieName in cookies :
      cookieValue = str( cookies[ cookieName ] )

      cookieData = cookieName + "=" + cookieValue
      self.send_header( 'Set-Cookie', cookieData )

    self.send_header( 'Content-type', 'text/xml' )
    self.end_headers()
    self.wfile.write( '<?xml version="1.0" ?>' )
    self.wfile.write( '<ResultData>' )

    # Send login status.
    self._JSON_send( "loginStatus", isAuthenticated )

    # If session has not been authenticated, send the session id and password
    # salt value.  This can be used by the login process on the client.
    if not isAuthenticated :
      self._JSON_send( "sessionId", session.getId() )
      self._JSON_send( "salt", session.getSalt() )

    # Does request have parameters?
    if length > 0 :
      # Get post data.
      postData = self.rfile.read( length )

      # Split the data by commands.
      commands = postData.decode().split("&")
      # For each command...
      for command in commands :

        # Break up the command.
        id, query = command.split( "=" )

        # Unquote the command.
        query = urllib.parse.unquote_plus( query )

        # See if this is a basic query (i.e. changes nothing).
        isBasicQuery = re.search( WebServerInterface.BASIC_QUERIES, query )

        if "passwordHash" == id :
          passwordResult = session.checkPassword( query )
          self._JSON_send( "loginResult", passwordResult )
        elif isAuthenticated or isBasicQuery :
          callbackResult = WebServerInterface.callback( self, query )
          self._send( id, callbackResult )

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

  print('Starting httpd...')
  while True :
    httpd.handle_request()
