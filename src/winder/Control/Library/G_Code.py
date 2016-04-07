###############################################################################
# Name: G_Code.py
# Uses: A class for reading and following G-Code.
# Date: 2016-02-09
# Author(s):
#   Andrew Que <aque@bb7.com>
#
# $$$FUTURE - Is unit too big?  Consider breaking classes into separate files.
#
###############################################################################

import re

#=============================================================================
#
#=============================================================================
class G_CodeClass :
  #---------------------------------------------------------------------
  def __init__( self, parentLine ) :
    """
    Constructor.

    Args:
      parentLine: Parent line that generated this code.

    """

    self.parentLine = parentLine
    self.parameters = []
    self.callback = None

  #---------------------------------------------------------------------
  def addParameter( self, parameter ) :
    """
    Add a parameter to this code. Useful for some commands.

    Args:
      parameter: Data to add.

    """

    self.parameters.append( float( parameter ) )

  #---------------------------------------------------------------------
  def setCallback( self, callback ) :
    """
    Assign a callback when this command is executed.

    Args:
      callback: A function that takes a single parameter.

    """

    self.callback = callback

  #---------------------------------------------------------------------
  def execute( self ) :
    """
    Execute this command. Runs command callback with code parameters.

    """

    if None != self.callback :
      self.callback( self.get() )

  #---------------------------------------------------------------------
  def get( self ) :
    """
    Get the parameter(s) for this code.

    Returns:
      Parameter(s) for this code.
    """

    result = self.parameters
    if 1 == len( self.parameters ) :
      result = self.parameters[ 0 ]
    return result

  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Get a string representation of code.

    Returns:
      String representation of code.
    """

    return self.__class__.__name__ + ": " + str( self.get() )

#=============================================================================
# Implementations of the various G-Codes.
# These are all simple children of 'G_CodeClass' setup to handle information
# specific to them.
#=============================================================================

#======================================
# Feed rate (F)
#======================================
class G_CodeFeedRate( G_CodeClass ) :
  pass

#======================================
# Command (G)
#======================================
class G_CodeCommand( G_CodeClass ) :
  def addParameter( self, parameter ) :
    self.parameters.append( parameter )

  def get( self ) :
    return self.parameters

#======================================
# Function (M)
#======================================
class G_CodeFunction( G_CodeClass ) :
  def addParameter( self, parameter ) :
    self.parameters.append( int( parameter ) )

#======================================
# Line number (N)
#======================================
class G_CodeLineNumber( G_CodeClass ) :
  def addParameter( self, parameter ) :
    self.parameters.append( int( parameter ) )

#======================================
# Program name (O)
#======================================
class G_CodeProgramName( G_CodeClass ) :
  def addParameter( self, parameter ) :
    self.parameters.append( parameter )

#======================================
# Parameter (P)
# (Not actually used.)
#======================================
class G_CodeParameter( G_CodeClass ) :
  pass

#======================================
# X position (X)
#======================================
class G_CodeSetX( G_CodeClass ) :
  pass

#======================================
# Y position (Y)
#======================================
class G_CodeSetY( G_CodeClass ) :
  pass

#======================================
# Z position (Z)
#======================================
class G_CodeSetZ( G_CodeClass ) :
  pass

#=============================================================================
# Table for holding callback functions run for each G-Code.
#=============================================================================
class G_CodeCallbacks :
  callbacks = \
  {
    'F' : None,
    'G' : None,
    'M' : None,
    'N' : None,
    'O' : None,
    'P' : None,
    'X' : None,
    'Y' : None,
    'Z' : None,
  }

  #---------------------------------------------------------------------
  def getCallback( self, code ) :
    """
    Return the callback for specified G-code.

    Returns:
      Callback function for code. None if there is no callback.
    """

    return self.callbacks[ code ]

  #---------------------------------------------------------------------
  def registerCallback( self, code, callback ) :
    """
    Set the callback for a G-code.

    Args:
      code: Which G-code.
      callback: Callback to be run.

    """

    self.callbacks[ code ] = callback

#=============================================================================
# Breakdown of a single line of G-code.
#=============================================================================
class G_CodeLine :

  # A lookup table that will translate a code to a G-code object.
  FUNCTION_TABLE = \
  {
    'F' : lambda parent: G_CodeFeedRate(    parent ),
    'G' : lambda parent: G_CodeCommand(     parent ),
    'M' : lambda parent: G_CodeFunction(    parent ),
    'N' : lambda parent: G_CodeLineNumber(  parent ),
    'O' : lambda parent: G_CodeProgramName( parent ),
    'P' : lambda parent: G_CodeParameter(   parent ),
    'X' : lambda parent: G_CodeSetX(        parent ),
    'Y' : lambda parent: G_CodeSetY(        parent ),
    'Z' : lambda parent: G_CodeSetZ(        parent )
  }

  #---------------------------------------------------------------------
  def __init__( self, callbacks, line ) :
    """
    Constructor.

    Args:
      callbacks: Instance of G_CodeCallbacks.
      line: G-code text.

    """

    # List of commands on this line.
    self.commands = []

    # Remove multiple spaces.
    line = re.sub( " +", " ", line )

    # Split the line into individual commands.
    commands = line.split( ' ' )

    # Last G-code object created.
    lastClass = None

    # For each command on the line...
    for command in commands :
      # Get the code (first character) and parameter (everything after the code).
      code = command[ :1 ]
      parameter = command[ 1: ]

      # If this is a parameter, pass it to the last class.
      if 'P' == code :
        if None != lastClass :
          lastClass.addParameter( parameter )
        else:
          raise Exception( 'Unassigned parameter', parameter )
      else:
        # Create an object to hold this command.
        lastClass = G_CodeLine.FUNCTION_TABLE[ code ]( self )

        # Add first parameter (everything after the code).
        lastClass.addParameter( parameter )

        # Assign the callback function.
        lastClass.setCallback( callbacks.getCallback( code ) )

        # Add this command to list.
        self.commands.append( lastClass )

  #---------------------------------------------------------------------
  def execute( self ) :
    """
    Run callbacks for G-code line.

    """

    for command in self.commands :
      if None != command.callback :
        command.execute()


  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Turn decoded line back into G-code.

    Returns:
      G-code for this line.
    """

    result = ""
    for command in self.commands :
      result += str( command ) + "\n"

    return result

#=============================================================================
# Interpreter for a G-code file.
#=============================================================================
class G_Code :

  #---------------------------------------------------------------------
  def __init__( self, lines, callbacks ) :
    """
    Constructor.

    Args:
      lines: List of G-Code lines.
      callbacks: Instance of G_CodeCallbacks.

    Raises:
      Exception: Malformed header in G-Code file.
      IOError: Problems reading specified G-Code file.
    """

    # Strip off line feeds and other white space from end of line.
    self.lines = map( str.strip, lines )

    self.index = 0
    self.callbacks = callbacks

  #---------------------------------------------------------------------
  def fetchLines( self, center, delta ) :
    """
    Fetch a sub-set of the G-Code self.lines.  Useful for showing what has
    recently executed, and what is to come.

    Args:
      center: Where to center the list.
      delta: Number of entries to read +/- center.

    Returns:
      List of G-Code lines, padded with empty lines if needed.
    """
    bottom = center - delta
    top = center + delta + 1
    start = max( bottom, 0 )
    end = min( top, len( self.lines ) )
    result = self.lines[ start:end ]

    if delta > center :
      result = [ "" ] * ( delta - center ) + result

    if top > len( self.lines ) :
      spaces = top - len( self.lines )
      result = result + [ "" ] * spaces

    return result

  #---------------------------------------------------------------------
  def getLineCount( self ) :
    """
    Get the number of lines of G_Code.

    Returns:
      Number of lines.
    """

    return len( self.lines )

  #---------------------------------------------------------------------
  def executeNextLine( self, lineNumber ) :
    """
    Run a line of G-code.

    """
    if lineNumber < len( self.lines ) :
      gCodeLine = G_CodeLine( self.callbacks, self.lines[ lineNumber ] )
      gCodeLine.execute()

#------------------------------------------------------------------------------
# Unit test.
#------------------------------------------------------------------------------
if __name__ == "__main__":

  def printf( text ):
    print text

  callbacks = G_CodeCallbacks()
  callbacks.registerCallback( 'G', lambda parameter: printf( "Command: " + str( parameter ) ) )
  callbacks.registerCallback( 'M', lambda parameter: printf( "Function: " + str( parameter ) ) )
  callbacks.registerCallback( 'X', lambda parameter: printf( "Set X: " + str( parameter ) ) )
  callbacks.registerCallback( 'Y', lambda parameter: printf( "Set Y: " + str( parameter ) ) )
  callbacks.registerCallback( 'Z', lambda parameter: printf( "Set Z: " + str( parameter ) ) )

  gCode = G_Code( 'G_CodeTest.txt', callbacks )

  #while not gCode.executeNextLine() :
  #  pass

  #print gGoceLine