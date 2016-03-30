###############################################################################
# Name: DebugGUI.py
# Uses: Debug user interface.
# Date: 2016-02-08
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import wx
import datetime
import ast
import math

from Library.UI_ClientConnection import UI_ClientConnection

#==============================================================================
class ActivatedTab :

  #---------------------------------------------------------------------
  def __init__( self, panel, notebook ) :
    self.notebook = notebook
    self.timer = wx.Timer(self)
    panel.Bind( wx.EVT_TIMER, self.update, self.timer )
    notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.activate )

  def update( self, event ) :
    pass

  #---------------------------------------------------------------------
  def activate( self, event ) :
    try:
      if self.notebook.GetCurrentPage() == self :
        self.timer.Start( 100 )
      else :
        self.timer.Stop()
    except:
      pass

    event.Skip()

#==============================================================================
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

class SystemTime( Remote ) :

  #---------------------------------------------------------------------
  def convertTimeString( self, currentTime ) :
    #currentTime = self.remote( "io.simulationTime.get()" )
    try:
      currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
    except ValueError:
      if "None" != currentTime :
        # Work around.  On some system (Windows) if the time 0 for microseconds,
        # it does not append the ".0" at the end.  So on a value error, just
        # try again with the .0 appended.
        currentTime += ".0"
        currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )

    return currentTime

  #---------------------------------------------------------------------
  def readTime( self ) :
    self.remote( "io.simulationTime.setLocal()" )
    currentTime = self.remote( "io.simulationTime.get()" )
    #try:
    #  currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
    #except ValueError:
    #  if "None" != currentTime :
    #    # Work around.  On some system (Windows) if the time 0 for microseconds,
    #    # it does not append the ".0" at the end.  So on a value error, just
    #    # try again with the .0 appended.
    #    currentTime += ".0"
    #    currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
    currentTime = self.convertTimeString( currentTime )

    return currentTime

  #---------------------------------------------------------------------
  def __init__( self, remote, panel, vbox ) :

    Remote.__init__( self, remote )

    #grideSizer = wx.FlexGridSizer( 1, 3, 5, 5 )
    grideSizer = wx.BoxSizer()
    self.time  = wx.StaticText( panel, label='2000-01-01 12:00:00.000000' )
    self.timeDelta  = wx.StaticText( panel, label='00000.000' )
    grideSizer.AddMany(
      [
        ( wx.StaticText( panel, label='Time'  ) ), ( self.time  ), ( self.timeDelta  )
      ]
    )

    self.startTime = self.readTime()

    vbox.Add( grideSizer )

  #---------------------------------------------------------------------
  def deltaString( self, endTime ) :
    delta = endTime - self.startTime
    delta = delta.total_seconds()

    deltaString = ""
    days = int( delta / ( 60 * 60 * 24 ) )
    delta -= days * ( 60 * 60 * 24 )

    hours = int( delta / ( 60 * 60 ) )
    delta -= hours * ( 60 * 60 )

    minutes = int( delta / ( 60 ) )
    delta -= minutes * ( 60 )

    if days > 0 :
      deltaString += str( days ) + "d "

    if hours > 0 :
      deltaString += str( hours ) + "h "

    if minutes > 0 :
      deltaString += str( minutes ) + "m "

    deltaString += "{:2.3f}s".format( delta )

    return deltaString

  #---------------------------------------------------------------------
  def update( self ) :
    currentTime = self.readTime()

    #delta = currentTime - self.startTime
    #delta = delta.total_seconds()

    #self.time.SetLabel( "{:6.3f}".format( delta.total_seconds() ) )
    self.time.SetLabel( str( currentTime ) )

    #deltaString = ""
    #days = int( delta / ( 60 * 60 * 24 ) )
    #delta -= days * ( 60 * 60 * 24 )
    #
    #hours = int( delta / ( 60 * 60 ) )
    #delta -= hours * ( 60 * 60 )
    #
    #minutes = int( delta / ( 60 ) )
    #delta -= minutes * ( 60 )
    #
    #if days > 0 :
    #  deltaString += str( days ) + "d "
    #
    #if hours > 0 :
    #  deltaString += str( hours ) + "h "
    #
    #if minutes > 0 :
    #  deltaString += str( minutes ) + "m "
    #
    #deltaString += "{:2.3f}s".format( delta )
    #

    deltaString = self.deltaString( currentTime )
    self.timeDelta.SetLabel( deltaString )


class MotorStatus( Remote ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel, vbox ) :

    Remote.__init__( self, remote )

    #
    # Motor status.
    #
    grideSizer = wx.FlexGridSizer( 4, 6, 5, 5 )

    self.empty = wx.StaticText( panel, -1, '')
    self.xAxis = wx.StaticText( panel, label='x:' )
    self.yAxis = wx.StaticText( panel, label='y:' )
    self.zAxis = wx.StaticText( panel, label='z:' )
    self.xAxisML = wx.StaticText( panel, label='Moving' )
    self.xAxisSL = wx.StaticText( panel, label='Seek' )
    self.xAxisPL = wx.StaticText( panel, label='Position' )
    self.xAxisVL = wx.StaticText( panel, label='Velocity' )
    self.xAxisAL = wx.StaticText( panel, label='Acceleration' )
    self.xAxisM = wx.StaticText( panel, label='False' )
    self.yAxisM = wx.StaticText( panel, label='False'  )
    self.zAxisM = wx.StaticText( panel, label='False'  )
    self.xAxisS = wx.StaticText( panel, label='+0000.00' )
    self.yAxisS = wx.StaticText( panel, label='+000.00'  )
    self.zAxisS = wx.StaticText( panel, label='+000.00'  )
    self.xAxisP = wx.StaticText( panel, label='+0000.00' )
    self.yAxisP = wx.StaticText( panel, label='+000.00'  )
    self.zAxisP = wx.StaticText( panel, label='+000.00'  )
    self.xAxisV = wx.StaticText( panel, label='+0000.00' )
    self.yAxisV = wx.StaticText( panel, label='+000.00'  )
    self.zAxisV = wx.StaticText( panel, label='+000.00'  )
    self.xAxisA = wx.StaticText( panel, label='+0000.00' )
    self.yAxisA = wx.StaticText( panel, label='+000.00'  )
    self.zAxisA = wx.StaticText( panel, label='+000.00'  )

    grideSizer.AddMany(
      [
        ( self.empty ), ( self.xAxisML ), ( self.xAxisSL ), ( self.xAxisPL ), ( self.xAxisVL ), ( self.xAxisAL ),
        ( self.xAxis ), ( self.xAxisM  ), ( self.xAxisS  ), ( self.xAxisP  ), ( self.xAxisV  ), ( self.xAxisA  ),
        ( self.yAxis ), ( self.yAxisM  ), ( self.yAxisS  ), ( self.yAxisP  ), ( self.yAxisV  ), ( self.yAxisA  ),
        ( self.zAxis ), ( self.zAxisM  ), ( self.zAxisS  ), ( self.zAxisP  ), ( self.zAxisV  ), ( self.zAxisA  ),
      ]
     )

    vbox.Add( grideSizer )

  #---------------------------------------------------------------------
  def update( self ) :

    xAxisMotion       = self.remote.get( "io.xAxis.isSeeking()" )
    yAxisMotion       = self.remote.get( "io.yAxis.isSeeking()" )
    zAxisMotion       = self.remote.get( "io.zAxis.isSeeking()" )

    xAxisSeek         = self.remoteFloat( "io.xAxis.getDesiredPosition()", "{0:>1.3f}" )
    yAxisSeek         = self.remoteFloat( "io.yAxis.getDesiredPosition()", "{0:>1.3f}" )
    zAxisSeek         = self.remoteFloat( "io.zAxis.getDesiredPosition()", "{0:>1.3f}" )

    xAxisPosition     = self.remoteFloat( "io.xAxis.getPosition()"    , "{0:>1.3f}" )
    xAxisVelocity     = self.remoteFloat( "io.xAxis.getVelocity()"    , "{0:>1.2f}" )
    xAxisAcceleration = self.remoteFloat( "io.xAxis.getAcceleration()", "{0:>1.0f}" )


    yAxisPosition     = self.remoteFloat( "io.yAxis.getPosition()"    , "{0:>1.3f}" )
    yAxisVelocity     = self.remoteFloat( "io.yAxis.getVelocity()"    , "{0:>1.2f}" )
    yAxisAcceleration = self.remoteFloat( "io.yAxis.getAcceleration()", "{0:>1.0f}" )

    zAxisPosition     = self.remoteFloat( "io.zAxis.getPosition()"    , "{0:>1.2f}" )
    zAxisVelocity     = self.remoteFloat( "io.zAxis.getVelocity()"    , "{0:>1.2f}" )
    zAxisAcceleration = self.remoteFloat( "io.zAxis.getAcceleration()", "{0:>1.0f}" )

    self.xAxisS.SetLabel( xAxisSeek )
    self.yAxisS.SetLabel( yAxisSeek )
    self.zAxisS.SetLabel( zAxisSeek )

    self.xAxisM.SetLabel( xAxisMotion )
    self.yAxisM.SetLabel( yAxisMotion )
    self.zAxisM.SetLabel( zAxisMotion )

    self.xAxisP.SetLabel( xAxisPosition     )
    self.xAxisV.SetLabel( xAxisVelocity     )
    self.xAxisA.SetLabel( xAxisAcceleration )

    self.yAxisP.SetLabel( yAxisPosition     )
    self.yAxisV.SetLabel( yAxisVelocity     )
    self.yAxisA.SetLabel( yAxisAcceleration )

    self.zAxisP.SetLabel( zAxisPosition     )
    self.zAxisV.SetLabel( zAxisVelocity     )
    self.zAxisA.SetLabel( zAxisAcceleration )
# end class

#==============================================================================
class JogTab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def jogStart( self, x, y ) :

    velocity = self.slider.GetValue() / 100.0
    x *= velocity
    y *= velocity

    # When both velocities are the same, calculate the maximum linear velocity
    # and use that.
    if 0 != x and 0 != y and abs( x ) == abs( y ) :
      velocity = math.sqrt( x * x / 2.0 )
      if x < 0 :
        x = -velocity
      else :
        x = velocity

      if y < 0 :
        y = -velocity
      else :
        y = velocity

    self.remote( "process.jogXY(" + str( x ) + "," + str( y ) + ")" )

  #---------------------------------------------------------------------
  def jogStop( self ) :
    self.remote( "io.plcLogic.jogXY( 0, 0 )" )
    self.remote( "process.jogXY( 0, 0 )" )

  #---------------------------------------------------------------------
  def setPosition( self, event ) :
    event = event
    velocity = self.slider.GetValue() / 100.0
    self.remote( "process.manualSeekXY( 0, 0, " + str( velocity ) + " )" )

  #---------------------------------------------------------------------
  def __init__( self, remote, panel ):

    wx.Panel.__init__( self, panel )
    ActivatedTab.__init__( self, self, panel )
    Remote.__init__( self, remote )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    self.systemTime = SystemTime( remote, self, vbox )

    outer = wx.FlexGridSizer( 1, 1, 0, 0 )
    #
    # Jog buttons.
    #
    grideSizer = wx.GridSizer( 3, 3, 5, 5 )

    jogXY_RU = wx.Button( self, label='\\' )
    jogXY_RZ = wx.Button( self, label='<-' )
    jogXY_RD = wx.Button( self, label='/' )

    jogXY_ZU = wx.Button( self, label='^' )
    jogXY_ZZ = wx.Button( self, label='*' )
    jogXY_ZD = wx.Button( self, label='v' )

    jogXY_FU = wx.Button( self, label='/' )
    jogXY_FZ = wx.Button( self, label='->' )
    jogXY_FD = wx.Button( self, label='\\' )

    jogXY_RU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  1 ) )
    jogXY_RZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  0 ) )
    jogXY_RD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1, -1 ) )

    jogXY_ZU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0,  1 ) )
    jogXY_ZD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0, -1 ) )

    jogXY_FU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  1 ) )
    jogXY_FZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  0 ) )
    jogXY_FD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1, -1 ) )


    jogXY_RU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_RZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_RD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_ZU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_ZD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_FU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_FZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_FD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_ZZ.Bind( wx.EVT_LEFT_DOWN, self.setPosition )

    grideSizer.AddMany(
      [
        ( jogXY_RU ), ( jogXY_ZU ), ( jogXY_FU ),
        ( jogXY_RZ ), ( jogXY_ZZ ), ( jogXY_FZ ),
        ( jogXY_RD ), ( jogXY_ZD ), ( jogXY_FD )
      ]
    )
    outer.Add( grideSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

    vbox.Add( outer )

    #
    # Velocity bar.
    #
    grideSizer = wx.GridSizer( 1, 1, 5, 5 )
    self.slider = \
      wx.Slider(
        self,
        -1,
        100,
        1, 500,
        wx.DefaultPosition,
        (500, -1),
        wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS
      )
    self.slider.Bind( wx.EVT_SCROLL, lambda e: self.remote( "process.gCodeHandler.setLimitVelocity( " + str( self.slider.GetValue() / 100.0 ) + ")" ) )

    grideSizer.AddMany(
      [
        ( self.slider )
      ]
    )
    vbox.Add( grideSizer )
    self.SetSizer( vbox )

    self.motorStatus = MotorStatus( remote, self, vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()
    self.motorStatus.update()

# end class

#==============================================================================
class APA_Tab( wx.Panel, Remote, ActivatedTab ) :

  #---------------------------------------------------------------------
  def gCodeSelect( self, event ):
    layer = self.layerSelection.GetValue()
    self.remote( "process.apa.loadRecipe( \"" + layer + "\", \"" + event.GetString() + "\", -1 )" )

  #---------------------------------------------------------------------
  def apaSelect( self, event ):
    self.remote( "process.switchAPA( \"" + event.GetString() + "\" )" )

  #---------------------------------------------------------------------
  def newAPA( self ) :
    self.remote( "process.createAPA( \"" + self.apaText.GetValue() + "\" )" )

    apaList = self.remote.get( "process.getAPA_List()" )
    apaList = ast.literal_eval( apaList )

    self.apaSelection.Clear()
    for apa in apaList :
      self.apaSelection.Append( apa )

  #---------------------------------------------------------------------
  def gotoLine( self ) :
    value = int( self.gotoText.GetValue() ) - 1
    self.remote.get( "process.setG_CodeLine( " + str( value ) + ")" )

  #---------------------------------------------------------------------
  def reverse( self, event ) :
    isReverse = not event.IsChecked()
    self.remote.get( "process.setG_CodeDirection( " + str( isReverse ) + " )" )

  #---------------------------------------------------------------------
  def loopMode( self, event ) :
    isLoop = event.IsChecked()
    self.remote.get( "process.setG_CodeLoop( " + str( isLoop ) + " )" )

  #---------------------------------------------------------------------
  def runToLine( self, event ) :
    event = event
    value = int( self.runToText.GetValue() )
    self.remote.get( "process.setG_CodeRunToLine( " + str( value ) + " )" )

  #---------------------------------------------------------------------
  def __init__( self, remote, panel ):

    wx.Panel.__init__( self, panel )
    Remote.__init__( self, remote )
    ActivatedTab.__init__( self, self, panel )
    self.remote = remote

    vbox = wx.BoxSizer( wx.VERTICAL )

    self.systemTime = SystemTime( remote, self, vbox )

    grideSizer = wx.BoxSizer( wx.HORIZONTAL )

    startButton = wx.Button( self, label='Start' )
    startButton.Bind( wx.EVT_BUTTON, lambda e: self.remote( "process.start()" ) )
    grideSizer.Add( startButton )

    stopButton = wx.Button( self, label='Stop' )
    stopButton.Bind( wx.EVT_BUTTON, lambda e: self.remote( "process.stop()" ) )
    grideSizer.Add( stopButton )

    self.reverseCheck = wx.CheckBox( self, -1, 'Reverse' )
    self.reverseCheck.Bind( wx.EVT_CHECKBOX, self.reverse )
    grideSizer.Add( self.reverseCheck )

    self.loopCheck = wx.CheckBox( self, -1, 'Loop' )
    self.loopCheck.Bind( wx.EVT_CHECKBOX, self.loopMode )
    grideSizer.Add( self.loopCheck )

    vbox.Add( grideSizer )

    #
    # G-Code execution status.
    #
    grideSizer = wx.FlexGridSizer( 3, 2, 5, 5 )
    self.lineText  = wx.StaticText( self, label='G-Code line:' )
    self.lineValue = wx.StaticText( self, label='0000' )

    self.stateText  = wx.StaticText( self, label='State:' )
    self.stateValue = wx.StaticText( self, label='<unknown>' )

    self.wireText  = wx.StaticText( self, label='Wire:' )
    self.wireValue = wx.StaticText( self, label='00000' )

    grideSizer.AddMany(
      [
        ( self.lineText ),  ( self.lineValue ),
        ( self.stateText ), ( self.stateValue ),
        ( self.wireText ),  ( self.wireValue )
      ]
     )

    vbox.Add( grideSizer )

    #
    # APA, layer, and recipe selection.
    #
    grideSizer = wx.FlexGridSizer( 3, 2, 5, 5 )

    recipes = self.remote.get( "process.getRecipes()" )
    recipes = ast.literal_eval( recipes )
    self.gCodeSelection = wx.ComboBox( self, -1, choices=recipes )
    self.gCodeSelection.Bind( wx.EVT_COMBOBOX, self.gCodeSelect )

    apaList = self.remote.get( "process.getAPA_List()" )
    apaList = ast.literal_eval( apaList )
    self.apaSelection = wx.ComboBox( self, -1, choices=apaList )
    self.apaSelection.Bind( wx.EVT_COMBOBOX, self.apaSelect )

    self.layerSelection = wx.ComboBox( self, -1, "G", choices=[ "G", "U", "V", "X" ] )

    grideSizer.AddMany(
      [
        wx.StaticText( self, label='APA'  ), ( self.apaSelection ),
        wx.StaticText( self, label='Layer'  ), ( self.layerSelection ),
        wx.StaticText( self, label='Recipe'  ), ( self.gCodeSelection )
      ]
     )

    vbox.Add( grideSizer )


    #
    # Add APA.
    #
    grideSizer = wx.FlexGridSizer( 1, 3, 5, 5 )

    self.apaText = wx.TextCtrl( self, -1, "", size=(175, -1) )

    apaAddButton = wx.Button( self, label='Add' )
    apaAddButton.Bind( wx.EVT_BUTTON, lambda e: self.newAPA() )

    grideSizer.AddMany(
      [
        wx.StaticText(self, -1, "APA name:"), ( self.apaText ), ( apaAddButton )
      ]
     )

    vbox.Add( grideSizer )

    #
    # Goto line.
    #
    grideSizer = wx.FlexGridSizer( 1, 3, 5, 5 )

    self.gotoText = wx.TextCtrl( self, -1, "" )
    gotoButton = wx.Button( self, label='Go' )
    gotoButton.Bind( wx.EVT_BUTTON, lambda e: self.gotoLine() )

    grideSizer.AddMany(
      [
        wx.StaticText(self, -1, "Goto line:"), ( self.gotoText ), ( gotoButton )
      ]
     )

    vbox.Add( grideSizer )

    #
    # Run to line.
    #
    grideSizer = wx.FlexGridSizer( 1, 3, 5, 5 )

    self.runToText = wx.TextCtrl( self, -1, "-1" )
    runToButton = wx.Button( self, label='Set' )
    runToButton.Bind( wx.EVT_BUTTON, self.runToLine )

    grideSizer.AddMany(
      [
        wx.StaticText(self, -1, "Run to line:"), ( self.runToText ), ( runToButton )
      ]
     )

    vbox.Add( grideSizer )

    #
    # Add G-Code following.
    # Use a ListBox and force a selection in order to highlight the active line.
    #
    grideSizer = wx.FlexGridSizer( 1, 1, 5, 5 )
    self.gCodeList = wx.ListCtrl( self, -1, size=(500, 125) )
    self.gCodeList.InsertColumn( 0, "", width=500 )
    self.gCodeList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.clearSelection )

    emptyString = ' ' * 125
    for index in range( 0, 5 ) :
      self.gCodeList.InsertStringItem( index, emptyString )

    grideSizer.Add( self.gCodeList )
    vbox.Add( grideSizer )

    self.motorStatus = MotorStatus( remote, self, vbox )

    self.SetSizer( vbox )

    self.timer = wx.Timer(self)
    self.Bind( wx.EVT_TIMER, self.update, self.timer )
    self.timer.Start( 100 )

  #---------------------------------------------------------------------
  def clearSelection( self, event ) :
    index = event.GetIndex()
    self.gCodeList.Select( index, False )
    self.gCodeList.Focus( -1 )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()
    self.motorStatus.update()

    currentLine = self.remote.get( "process.gCodeHandler.getLine()" )
    if "None" != currentLine :
      currentLine = int( currentLine ) + 1

    self.lineValue.SetLabel(
      str( currentLine )
       + "/"
       + self.remote.get( "process.gCodeHandler.getTotalLines()" )
    )

    currentLine = self.remote.get( "process.gCodeHandler.getLine()" )

    gCode = self.remote.get( "process.getG_CodeList( " + str( currentLine ) + ", 2 )" )
    gCode = ast.literal_eval( gCode )

    index = 0
    for item in gCode :
      self.gCodeList.SetStringItem( index, 0, item )
      index += 1

    self.gCodeList.SetColumnWidth( 0, 500 )
    self.gCodeList.SetItemBackgroundColour( 2, "CYAN" )

    isForward = self.remote.get( "process.gCodeHandler.getDirection()" )
    isForward = "True" == isForward

    if isForward :
      self.gCodeList.SetItemBackgroundColour( 3, "GREEN" )
      self.gCodeList.SetItemBackgroundColour( 1, "WHITE" )
    else :
      self.gCodeList.SetItemBackgroundColour( 1, "GREEN" )
      self.gCodeList.SetItemBackgroundColour( 3, "WHITE" )

    #self.gCodeList.SetSelection( 2 )

    self.stateValue.SetLabel( self.remote.get( "process.controlStateMachine.state.__class__.__name__" ) )
    self.wireValue.SetLabel( self.remote.get( "process.spool.getWire()" ) )


#==============================================================================
class IO_Tab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel ) :

    wx.Panel.__init__( self, panel )
    Remote.__init__( self, remote )
    ActivatedTab.__init__( self, self, panel )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    #
    # Time.
    #
    self.systemTime = SystemTime( remote, self, vbox )

    outerGrid = wx.FlexGridSizer( 1, 2, 10, 50 )

    #
    # Inputs.
    #
    grideSizer = wx.FlexGridSizer( 1, 2, 0, 20 )

    self._inputList = self.remote.get( "LowLevelIO.getInputs()" )
    self._inputList = ast.literal_eval( self._inputList )

    self._inputLabels = {}
    for instance in self._inputList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._inputLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    outerGrid.Add( grideSizer )

    #
    # Outputs.
    #
    grideSizer = wx.FlexGridSizer( 1, 2, 0, 20 )

    self._outputList = self.remote.get( "LowLevelIO.getOutputs()" )
    self._outputList = ast.literal_eval( self._outputList )

    self._outputLabels = {}
    for instance in self._outputList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._outputLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    outerGrid.Add( grideSizer, wx.EXPAND )

    vbox.Add( outerGrid )

    #
    # Motor status.
    #
    self.motorStatus = MotorStatus( remote, self, vbox )

    self.SetSizer( vbox )

    self.timer = wx.Timer(self)
    self.Bind( wx.EVT_TIMER, self.update, self.timer )
    self.timer.Start( 100 )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    for instance in self._inputList :
      inputName = instance[ 0 ]
      inputValue = self.remote.get( "LowLevelIO.getInput( \"" + inputName + "\")" )
      self._inputLabels[ inputName ].SetLabel( inputValue )

    for instance in self._outputList :
      outputName = instance[ 0 ]
      outputValue = self.remote.get( "LowLevelIO.getOutput( \"" + outputName + "\")" )
      self._outputLabels[ outputName ].SetLabel( outputValue )

    self.motorStatus.update()


#==============================================================================
class PLC_Tab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel ) :

    wx.Panel.__init__( self, panel )
    ActivatedTab.__init__( self, self, panel )
    Remote.__init__( self, remote )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    #
    # Time.
    #
    self.systemTime = SystemTime( remote, self, vbox )

    #
    # Tags.
    #
    grideSizer = wx.FlexGridSizer( 1, 2, 0, 40 )

    self._tagList = self.remote.get( "LowLevelIO.getTags()" )
    self._tagList = ast.literal_eval( self._tagList )

    self._tagLabels = {}
    for instance in self._tagList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._tagLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    vbox.Add( grideSizer )

    self.SetSizer( vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    for instance in self._tagList :
      tagName = instance[ 0 ]
      tagValue = self.remote.get( "LowLevelIO.getTag( \"" + tagName + "\")" )
      self._tagLabels[ tagName ].SetLabel( tagValue )

#==============================================================================
class LogTab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel ) :

    wx.Panel.__init__( self, panel )
    ActivatedTab.__init__( self, self, panel )
    Remote.__init__( self, remote )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    #
    # Time.
    #
    self.systemTime = SystemTime( remote, self, vbox )

    grideSizer = wx.FlexGridSizer( 1, 1, 5, 5 )
    self.log = wx.TextCtrl( self, -1, size = (500, 530), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL )

    grideSizer.Add( self.log )

    vbox.Add( grideSizer )

    self.SetSizer( vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    log = self.remote.get( "log.getRecent()" )
    log = ast.literal_eval( log )
    result = ""
    for line in log :
      sections = line.split( "\t" )

      eventTime = self.systemTime.convertTimeString( sections[ 0 ] )
      eventTime = self.systemTime.deltaString( eventTime )

      result += eventTime + " " + sections[ 3 ] + "\n"

    log = result

    self.log.SetValue( log )

#==============================================================================
class DebugGUI( wx.Frame, Remote ):

  #---------------------------------------------------------------------
  def __init__( self, parent, address, port, maxReceiveSize ) :
    wx.Frame.__init__( self, None )

    #time.sleep( 0.2 )

    self.remote = UI_ClientConnection( address, port, maxReceiveSize )

    Remote.__init__( self, self.remote )

    self._parent = parent
    panel = wx.Panel( self )

    notebook = wx.Notebook( panel )

    tab1 = JogTab( self.remote, notebook )
    tab2 = APA_Tab( self.remote, notebook )
    tab3 = IO_Tab( self.remote, notebook )
    tab4 = PLC_Tab( self.remote, notebook )
    tab5 = LogTab( self.remote, notebook )

    notebook.AddPage( tab1, "Jog" )
    notebook.AddPage( tab2, "APA" )
    notebook.AddPage( tab3, "I/O" )
    notebook.AddPage( tab4, "PLC" )
    notebook.AddPage( tab5, "Log" )

    sizer = wx.BoxSizer()
    sizer.Add( notebook, 1, wx.EXPAND )
    panel.SetSizer( sizer )

    self.timer = wx.Timer(self)
    self.Bind( wx.EVT_TIMER, self.update, self.timer )
    self.timer.Start( 100 )

    self.SetSize( (520, 600) )
    self.SetTitle( 'DUNE Winder Simulator' )
    self.Show( True )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    isRunning = ( "True" == self.remote.get( "PrimaryThread.isRunning" ) )

    # If primary threads are shutting down, close the window.
    if not isRunning :
      self.Close()

# end class


#def test() :
if __name__ == "__main__":
  wxApplication = wx.App()
  DebugGUI( None, "192.168.56.102", 6626, 1024 )
  #DebugGUI( None, "172.16.21.47", 6626 )
  wxApplication.MainLoop()
