###############################################################################
# Name: Log.py
# Uses: Class for creating log files.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import threading
import os.path
import collections

class Log:

  #---------------------------------------------------------------------
  def getTimestamp( self ):
    """
    Get a timestamp.

    Returns:
      String of current system time.
    """

    return str( self._systemTime.get() )

  #---------------------------------------------------------------------
  def __init__( self, systemTime, outputFileName = None, localEcho = True ) :
    """
    Constructor.

    Args:
      outputFileName: Name of file to log messages.
      localEcho: True if message is also printed to stdout.

    """

    self._systemTime = systemTime
    self._lock = threading.Lock()
    self._outputFiles = []
    self._outputFileList = {}
    if outputFileName :
      self.attach( outputFileName )

    self._localEcho = localEcho
    if self._localEcho :
      print "Time                       Message"

  #---------------------------------------------------------------------
  def attach( self, outputFileName ):
    """
    Add an other file to log messages.

    Args:
      outputFileName: File to append.

    """
    self._lock.acquire()

    # Create the path if it does not exist.
    path = os.path.dirname( outputFileName )
    if not os.path.exists( path ) :
      os.makedirs( path )

    needsHeader = not os.path.isfile( outputFileName )
    outputFile = open( outputFileName, 'a' )

    if needsHeader :
      outputFile.write( "Time\tModule\tType\tMessage\n" )

    self._outputFileList[ outputFileName ] = outputFile
    self._outputFiles.append( outputFile )
    self._lock.release()

  #---------------------------------------------------------------------
  def detach( self, outputFileName ):
    """
    Remove log file from getting log messages.

    Args:
      outputFileName: Log file previously attached.

    """
    self._lock.acquire()
    outputFile = self._outputFileList[ outputFileName ]
    self._outputFileList.pop( outputFileName )
    outputFile.close()
    self._lock.release()

  #---------------------------------------------------------------------
  def add( self, module, typeName, message, parameters = [] ) :
    """
    Add a message to log file.

    Args:
      module: Which module. Use "self.__class__.__name__".
      typeName: Message type.
      message: Human readable message.
      parameters: A list of all data associated with entry.

    """

    currentTime = self.getTimestamp()
    line =                   \
      str( currentTime )     \
      + "\t"                 \
      + str( module )        \
      + "\t"                 \
      + str( typeName )      \
      + "\t"                 \
      + message

    for parameter in parameters:
      line += "\t" + str( parameter )

    # Write the message to each open log file.
    self._lock.acquire()
    for _, outputFile in self._outputFileList.iteritems():
      outputFile.write( line + "\n" )
    self._lock.release()

    # Local echo if requested.
    if self._localEcho :
      line = str( currentTime ) + " " + message
      isFirst = True
      parameterLine = ""
      for parameter in parameters:
        if not isFirst :
          parameterLine += ", "
        isFirst = False
        parameterLine += str( parameter )

      if "" != parameterLine :
        parameterLine = " [" + parameterLine + "]"

      line += parameterLine

      print line
