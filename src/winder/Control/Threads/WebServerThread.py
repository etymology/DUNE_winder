###############################################################################
# Name: WebServerThread.py
# Uses: Web based user interface server thread.
# Date: 2016-05-02
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
import httplib
import os

from Threads.PrimaryThread import PrimaryThread
from Machine.Settings import Settings
from Library.WebServerInterface import WebServerInterface

class WebServerThread( PrimaryThread ):
  #---------------------------------------------------------------------
  def __init__( self, commandCallback, log ):
    """
    Constructor.

    Args:
      callback: Function to send data from client.
    """

    os.chdir( Settings.WEB_DIRECTORY )

    PrimaryThread.__init__( self, "WebServerThread", log )
    self._callback = commandCallback
    self._log = log

  #---------------------------------------------------------------------
  def body( self ) :
    """
    Body of thread. Accepts client connections and swans threads to deal with client requests.
    """

    class ThreadedHTTPServer( ThreadingMixIn, HTTPServer ):
      """Handle requests in a separate thread."""
      pass

    WebServerInterface.callback = self._callback
    server_address = ( '', Settings.WEB_SERVER_PORT )
    httpd = ThreadedHTTPServer( server_address, WebServerInterface )

    while PrimaryThread.isRunning :
      httpd.handle_request()

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Send a dummy request to server to cause connection to close.
    """

    try :
      # HEAD request just so thread unblocks.  This will throw an exception.
      connection = httplib.HTTPConnection( "127.0.0.1" )
      connection.request( "HEAD","/" )
    except :
      pass

# end class
