###############################################################################
# Name: Recipe.py
# Uses: G-Code recipe file loader.
# Date: 2016-03-04
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#     A recipe is for the most part a G-Code file, but with a standard header.
#   This header is a single line--a G-Code comment--that contains a description
#   and one or two hashes.  The first hash is an ID to identify this file.  The
#   second is an optional parent hash that can be used to identify the parent
#   object the file was derived.
#     Hash calculation is done automatically as long as the header line exists.
#   If the hash doesn't match, the existing hash (if there is one) is assumed
#   to be the parent from which the file was derived.  If there is no hash at
#   all, there is no parent.  The file is rewritten with the new heading.
#     Any time a file is loaded, correct hash or not, the archive is checked
#   for a file with by the name of the hash.  If it does not exist, a copy of
#   this file is made in the archive.  This way any recipe that is used is
#   archived.
#     The hash is used as an ID and can be read externally.  The G-Code from
#   the file is also loaded and can be pass to something that can work with
#   the G-Code.
###############################################################################
from __future__ import absolute_import
import re
import os.path
import shutil

from .Hash import Hash

class Recipe :
  #---------------------------------------------------------------------
  def __init__( self, fileName, archiveDirectory ) :
    """
    Constructor.

    Args:
      fileName: File name of recipe to load.
      archiveDirectory: Path to archive directory.
    """
    # Read input file.
    with open( fileName ) as inputFile :
      # Read file header.
      header = inputFile.readline()

      # Get the rest of the lines.
      self._lines = inputFile.readlines()

    # Regular expression for header.  Headings must be in the following format:
    #   ( Description hash parentHash )
    # Where the description is a text field ending with a comma, and the hash
    # fields.
    headerCheck = '\( (.+?)[ ]+(?:' \
      + Hash.HASH_PATTERN + '[ ]+)?(?:' + Hash.HASH_PATTERN + '[ ]+)?\)'

    expression = re.search( headerCheck, header, re.IGNORECASE )
    if not expression :
      raise Exception( "Recipe contains no heading." )

    self._description = expression.group( 1 )
    self._headerHash  = expression.group( 2 )
    self._parentHash  = expression.group( 3 )

    # Create hash of G-Code, including description.
    bodyHash = Hash()
    bodyHash += self._description
    for line in self._lines :
      bodyHash += line

    # Turn hash into base 32 encoding.
    bodyHash = str( bodyHash )

    # Does the caclulated hash not match the hash from the header?
    if bodyHash != self._headerHash :

      # If there was a hash, it is the parent hash.
      if None == self._headerHash :
        self._headerHash = ""
      else:
        self._headerHash += " "

      # Rewrite the recipe file with the correct header.
      with open( fileName, "w" ) as outputFile :
        outputFile.write( "( " + self._description + " " + bodyHash + " " + self._headerHash + ")\n" )
        outputFile.writelines( self._lines )

      # Setup correct current and parent hash.
      self._parentHash = self._headerHash
      self._headerHash = bodyHash

    if archiveDirectory :
      # If this file does not exist in the archive, copy it there.
      archiveFile = archiveDirectory + "/" + bodyHash
      if not os.path.isfile( archiveFile ) :
        # Make an archive copy of the file.
        shutil.copy2( fileName, archiveFile )

  #---------------------------------------------------------------------
  def getLines( self ) :
    """
    Return all recipe G-Code lines.

    Returns:
      All recipe G-Code lines.
    """
    return self._lines

  #---------------------------------------------------------------------
  def getDescription( self ) :
    """
    Return the description of this recipe.  Comes from header of G-Code.

    Returns:
      Description of G-Code file.
    """
    return self._description

  #---------------------------------------------------------------------
  def getID( self ) :
    """
    Return the unique ID of this recipe.

    Returns:
      ID of G-Code file.

    Notes:
      The ID is a hash that correlates the file to a file in the archive.
    """
    return self._headerHash

  #---------------------------------------------------------------------
  def getParentID( self ) :
    """
    Return the unique parent ID of this recipe.

    Returns:
      ID of parent G-Code file.

    Notes:
      Modified G-Code can have a parent which can be traced from this ID.
    """
    return self._parentHash
