import sys

#------------------------------------------------------------------------------
class Recipe :
  net = []
  nodesA = []
  nodesB = []

  def printRubyCode( self ) :
    sys.stdout.write( "line = Sketchup.active_model.entities.add_line " )
    side = 1
    isFirst = True
    pin = 1
    pins = len( self.nodesA )
    for number in self.net :
      if 0 == side :
        x  = self.nodesA[ number ][ 0 ]
        y  = self.nodesA[ number ][ 1 ]
        z  = self.nodesA[ number ][ 2 ]
        zz = self.nodesB[ number ][ 2 ]
      else:
        x  = self.nodesB[ number ][ 0 ]
        y  = self.nodesB[ number ][ 1 ]
        z  = self.nodesB[ number ][ 2 ]
        zz = self.nodesA[ number ][ 2 ]


      if not isFirst :
        sys.stdout.write( ",\r\n\t" )
      else:
        z = zz

      sys.stdout.write( "[" + str( x ) + "," + str( z ) + "," + str( y ) + "]" )

      if pin < pins :
        sys.stdout.write( ",[" + str( x ) + "," + str( zz ) + "," + str( y ) + "]" )

      side = ( side + 1 ) % 2
      pin += 1
      isFirst = False


#------------------------------------------------------------------------------
class Layer1Recipe( Recipe ) :
  def __init__( self, rows, columns, bottomX, bottomY, deltaX, deltaY, depth ) :
    for row in range( 0, rows ) :
      x = bottomX
      y = bottomY + deltaY * row
      #print x, y
      self.nodesA.append( [ x, y, 0.0 ] )
      self.nodesB.append( [ x, y, depth ] )

    for row in range( rows - 1, -1, -1 ) :
      x = bottomX + deltaX * columns
      y = bottomY + deltaY * row
      #print x, y
      self.nodesA.append( [ x, y, 0.0 ] )
      self.nodesB.append( [ x, y, depth ] )

    #print self.nodesA


    index = 0
    for row in range( 0, rows / 2 ) :
      self.net.append( index                )
      self.net.append( 2 * rows - index - 1 )
      self.net.append( 2 * rows - index - 2 )
      index += 1

    print self.net


#------------------------------------------------------------------------------
class Layer2Recipe( Recipe ) :

  def __init__( self, rows, columns, bottomX, bottomY, deltaX, deltaY, depth ) :
    """
    Construct a layer 2 net list.

      *  *  *  *  *  *  *  *
              / \/ \
    *        /  /\  \      *
           /   /  \  \
    *     /  /      \ \    *
        /   /        \  \
    *  /   /          \  \ *
     /   /              \ \
    *   /                \ *
     \ /                  \
      *  *  *  *  *  *  *  *

    This layer begins in the bottom right corner, runs diagonally to the
    top center, then to the bottom most pin on the far left, the left most
    pin on the bottom, one pin right of center, and the second from the bottom
    """

    # Start in lower left corner.
    for row in range( 0, rows ) :
      x = bottomX
      y = bottomY + deltaY / 2.0 + deltaY * row
      self.nodesA.append( [ x, y, 0 ] )
      self.nodesB.append( [ x, y, depth ] )

    for column in range( 0, columns ) :
      x = bottomX + deltaX / 2.0 + deltaX * column
      y = bottomY                + deltaY * rows
      self.nodesA.append( [ x, y, 0 ] )
      self.nodesB.append( [ x, y, depth ] )

    for row in range( rows, -1, -1 ) :
      x = bottomX + deltaX / 2.0 + deltaX * columns
      y = bottomY                + deltaY * row
      self.nodesA.append( [ x, y, 0 ] )
      self.nodesB.append( [ x, y, depth ] )

    for column in range( columns - 1, -1, -1 ) :
      x = bottomX + deltaX / 2.0 + deltaX * column
      y = bottomY
      self.nodesA.append( [ x, y, 0 ] )
      self.nodesB.append( [ x, y, depth ] )

    # Define the first 6 net locations.
    self.net = \
    [
      2 * rows + columns,
      int( rows + columns / 2 ),
      0,
      2 * rows + 2 * columns,
      int( rows + columns / 2 + 1 ),
      2 * rows + columns - 1
    ]

    #print self.net

    pins = 2 * rows + 2 * columns
    direction = 1

    # All remaining net locations are based off a simple the previous 5.
    #side = 0
    for netNumber in range( 5, pins ) :
      self.net.append( self.net[ netNumber - 5 ] + direction )
      direction = -direction

    #for number in self.net :
    #  print number

#------------------------------------------------------------------------------

rows    = 16
columns = 2 * rows - 1

bottomX = 0
bottomY = 0
deltaX  = 8.0
deltaY  = 5.75
depth   = 15

recipe = Layer1Recipe( rows, columns, bottomX, bottomY, deltaX, deltaY, depth )
recipe.printRubyCode()
print ""
print "line = Sketchup.active_model.entities.add_line [0,0],[0,0]"
recipe = Layer2Recipe( rows, columns, bottomX, bottomY, deltaX, deltaY, depth )
recipe.printRubyCode()
