###############################################################################
# Name: Log.py
# Uses: Class for creating log files.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from __future__ import absolute_import
from __future__ import print_function
import threading
import os.path
import collections
import six

class Log:

  #---------------------------------------------------------------------
  def _getTimestamp( self ):
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
    self._recent = collections.deque( maxlen = 30 )
    self._outputFiles = []
    self._outputFileList = {}
    if outputFileName :
      self.attach( outputFileName )

    self._localEcho = localEcho
    if self._localEcho :
      print("Time                       Message")

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
    if outputFileName in self._outputFileList :
      outputFile = self._outputFileList[ outputFileName ]
      self._outputFileList.pop( outputFileName )
      outputFile.close()
    self._lock.release()

  #---------------------------------------------------------------------
  def getRecent( self ) :
    """
    Return the most recent lines of the log file.

    Returns:
      The most recent lines of the log file.
    """
    self._lock.acquire()
    result = list( self._recent )
    self._lock.release()
    return result

  #---------------------------------------------------------------------
  def _tail( self, inputFile, lines ) :
    """
    Return the last n lines from an open file.

    Args:
      inputFile - File to read from.  Must be open and readable.
      lines - Number of lines to read.
    Returns:
      Array of lines.
    Notes:
      Function copied from comment at stackoverflow.com.
    """
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    inputFile.seek( 0, 2 )
    block_end_byte = inputFile.tell()
    lines_to_go = total_lines_wanted
    block_number = -1

    # Blocks of size BLOCK_SIZE, in reverse order starting
    # from the end of the file.
    blocks = []

    while lines_to_go > 0 and block_end_byte > 0:
      if ( block_end_byte - BLOCK_SIZE > 0 ):
        # Read the last block we haven't yet read
        inputFile.seek( block_number * BLOCK_SIZE, 2 )
        blocks.append( inputFile.read( BLOCK_SIZE ) )
      else:
        # File too small, start from beginning.
        inputFile.seek( 0, 0 )

        # Only read what was not read
        blocks.append( inputFile.read( block_end_byte ) )
      lines_found = blocks[ -1 ].count( '\n' )
      lines_to_go -= lines_found
      block_end_byte -= BLOCK_SIZE
      block_number -= 1
    all_read_text = ''.join( reversed( blocks ) )
    return all_read_text.splitlines()[ -total_lines_wanted: ]
    #return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

  #---------------------------------------------------------------------
  def getAll( self, numberOfLines=-1 ) :
    """
    Get the entire log file.

    Return:
      An array of each line of the log file.
    """

    fileName = list(self._outputFileList.keys())[ 0 ]

    if -1 == numberOfLines :
      with open( fileName ) as inputFile :
        # Red and ignore header.
        inputFile.readline()

        # Read remaining lines.
        lines = inputFile.readlines()

      # Remove line feeds.
      for index, line in enumerate( lines ) :
        lines[ index ] = line.replace( "\n", "" )
    else:
      with open( fileName ) as inputFile :
        lines = self._tail( inputFile, numberOfLines )

    return lines

  #---------------------------------------------------------------------
  def add( self, module, typeName, message, parameters = None ) :
    """
    Add a message to log file.

    Args:
      module: Which module. Use "self.__class__.__name__".
      typeName: Message type.
      message: Human readable message.
      parameters: A list of all data associated with entry.
    """

    currentTime = self._getTimestamp()
    line =                   \
      str( currentTime )     \
      + "\t"                 \
      + str( module )        \
      + "\t"                 \
      + str( typeName )      \
      + "\t"                 \
      + message

    if None == parameters :
      parameters = []

    for parameter in parameters:
      line += "\t" + str( parameter )

    # Write the message to each open log file.
    self._lock.acquire()
    self._recent.append( line )
    for _, outputFile in six.iteritems(self._outputFileList):
      outputFile.write( line + "\n" )
      outputFile.flush()
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

      print(line)
