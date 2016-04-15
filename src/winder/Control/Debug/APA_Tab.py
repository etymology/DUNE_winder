###############################################################################
# Name: APA_Tab.py
# Uses: APA setup and operation tab.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import ast
import wx
from .Remote import Remote
from .ActivatedTab import ActivatedTab
from .SystemTime import SystemTime
from .MotorStatus import MotorStatus

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

