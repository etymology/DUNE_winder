function APA()
{
  var self = this

  // True when the APA settings can be modified.  Used to prevent modifications
  // to the APA while the machine is running.
  var apaEnabled = true

  // True when
  var apaEnabledInhabit = false

  var loopButtonUpdate
  var reverseButtonUpdate

  // Tags to disable during APA loading.
  var apaInterfaceTags =
  [
    "#apaSelection",
    "#layerSelection",
    "#gCodeSelection",
    "#apaName",
    "#apaNewButton",
    "#apaStageSelect",
    "#apaStageReason",
    "#apaStageButton"
  ]

  var stage = null

  //-----------------------------------------------------------------------------
  // Uses:
  //   Enable all APA interface controls.
  //-----------------------------------------------------------------------------
  this.enableAPA_Interface = function()
  {
    apaEnabled = true
    for ( var index in apaInterfaceTags )
    {
      var tag = apaInterfaceTags[ index ]
      $( tag ).prop( "disabled", false )
    }

    $( "#loading" ).html( "&nbsp;" )
    this.populateLists()

    if ( this.loopButtonUpdate )
      this.loopButtonUpdate()

    if ( this.reverseButtonUpdate )
      this.reverseButtonUpdate()
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Disable all APA interface controls.
  //-----------------------------------------------------------------------------
  this.disableAPA_Interface = function( message )
  {
    apaEnabled = false
    $( "#loading" ).html( message )

    for ( var index in apaInterfaceTags )
    {
      var tag = apaInterfaceTags[ index ]
      $( tag ).prop( "disabled", true )
    }
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to start/stop recipe execution.
  // Input:
  //   isRunning - True to start, false to stop.
  //-----------------------------------------------------------------------------
  this.setRunningState = function( isRunning )
  {
    if ( isRunning )
      winder.remoteAction( 'process.start()' )
    else
      winder.remoteAction( 'process.stop()' )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Re-enable APA interface.  Callback function.
  //-----------------------------------------------------------------------------
  this.reenableAPA = function()
  {
    self.enableAPA_Interface()
    apaEnabledInhabit = false
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   APA selection callback.
  //-----------------------------------------------------------------------------
  this.selectAPA = function()
  {
    // Get the new APA selection.
    var apa = $( "#apaSelection" ).val()

    // If not the null selection...
    if ( "" != apa )
    {
      // Disable the APA interface during loading process.
      apaEnabledInhabit = true
      this.disableAPA_Interface( "Loading APA" )

      // Start loading new APA.
      winder.remoteAction
      (
        'process.switchAPA( "' + apa + '" )',
        this.reenableAPA
      )
    }
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   G-Code selection callback.
  //-----------------------------------------------------------------------------
  this.selectG_Code = function()
  {
    // Get the layer and G-Code recipe.
    var layer = $( "#layerSelection" ).val()
    var gCode = $( "#gCodeSelection" ).val()

    // If not the null selection...
    if ( "" != gCode )
    {
      // Disable APA interface during loading process.
      apaEnabledInhabit = true
      this.disableAPA_Interface( "Loading G-Code" )

      // Begin loading G-Code.
      winder.remoteAction
      (
        'process.apa.loadRecipe( "' + layer + '", "' + gCode + '", -1 )',
        self.reenableAPA
      )
    }
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Load values for and repopulate all lists.
  //-----------------------------------------------------------------------------
  this.populateLists = function()
  {
    winder.populateComboBox
    (
      "#apaSelection",
      "process.getAPA_List()",
      "process.getLoadedAPA_Name()",
      function()
      {
        var selection = $( "#apaSelection" ).val()
        var isDisabled = ( "" == selection ) || isRunning()
        $( "#apaCloseButton" ).prop( "disabled", isDisabled )
      }
    )

    winder.populateComboBox
    (
      "#gCodeSelection",
      "process.getRecipes()",
      "process.getRecipeName()"
    )

    // Get the current layer.
    winder.remoteAction
    (
      'process.getRecipeLayer()',
      function( data )
      {
        $( "#layerSelection" ).val( data )
      }
    )

  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for generating new APA.
  //-----------------------------------------------------------------------------
  this.newAPA = function()
  {
    winder.remoteAction
    (
      'process.createAPA( "' + $( "#apaName" ).val() + '" )',
       this.populateLists
    )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for setting next active G-Code line.
  //-----------------------------------------------------------------------------
  this.gotoLine = function()
  {
    winder.remoteAction( 'process.setG_CodeLine( ' + $( "#apaLine" ).val() + ' )' )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for setting G-Code breakpoint.
  //-----------------------------------------------------------------------------
  this.runToLine = function()
  {
    winder.remoteAction( "process.setG_CodeRunToLine( " + $( "#apaBreakLine" ).val() + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for setting spool wire amount.
  //-----------------------------------------------------------------------------
  this.setSpool = function()
  {
    winder.remoteAction( "process.spool.setWire( " + $( "#setSpool" ).val() + " )" )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Close the current APA.
  //-----------------------------------------------------------------------------
  this.closeAPA = function()
  {
    winder.remoteAction
    (
      "process.closeAPA()",
      this.populateLists
    )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Change the APA stage of progress.
  //-----------------------------------------------------------------------------
  this.changeStage = function()
  {
    var newStage = $( "#apaStageSelect" ).val()
    var reasonForChange = $( "#apaStageReason" ).val()
    winder.remoteAction
    (
      'process.apa.setStage( ' + newStage + ', "' + reasonForChange + '" )',
      function()
      {
        $( "#apaStageReason" ).val( "" )
        self.populateLists()
      }
    )
  }

  // Populate lists and have this function run after error recovery.
  this.populateLists()
  winder.addErrorClearCallback( this.populateLists )

  // Set updates of current line and total lines.
  winder.addPeriodicRemoteDisplay( "process.gCodeHandler.getLine()", "#currentLine" )
  winder.addPeriodicRemoteDisplay( "process.gCodeHandler.getTotalLines()", "#totalLines" )
  winder.addPeriodicRemoteDisplay( "process.spool.getWire()", "#spoolAmount" )

  //winder.addPeriodicRemoteDisplay( "process.getStage()", "#apaStage" )
  winder.addPeriodicRemoteCallback
  (
    "process.getStage()",
    function( value )
    {
      stage = value
      var isDisabled = false
      if ( "" == stage )
      {
        stage = "(no APA loaded)"
        isDisabled = true
      }

      $( "#apaStageSelect" ).prop( "disabled", isDisabled )
      $( "#apaStageReason" ).prop( "disabled", isDisabled )
      $( "#apaStageButton" ).prop( "disabled", isDisabled )

      $( "#apaStage" ).html( stage )
    }
  )

  // Load the motor status module.
  winder.loadSubPage( "/Desktop/Modules/motorStatus", "#motorStatusDiv" )

  // Callback run after period updates happen to enable/disable APA controls
  // depending on machine state.
  winder.addPeriodicEndCallback
  (
    function()
    {
      var controlState = states[ "controlState" ]

      $( "#controlState" ).text( controlState )

      var startDisable = ( "StopMode" != controlState ) || apaEnabledInhabit
      $( "#startButton" ).prop( "disabled", startDisable )

      var stopDisable = ( "WindMode" != controlState )
      $( "#stopButton" ).prop( "disabled", stopDisable )

      if ( ( ! stopDisable )
        && ( apaEnabled )
        && ( ! apaEnabledInhabit ) )
      {
        self.disableAPA_Interface( "Running." )
      }
      else
      if ( ( stopDisable )
        && ( ! apaEnabled )
        && ( ! apaEnabledInhabit ) )
      {
        self.enableAPA_Interface()
      }
    }

  )

  // Setup G-Code table.
  winder.addPeriodicRemoteCallback
  (
    "process.getG_CodeList( None, 3 )",
    function( data )
    {
      // If there is any data.
      if ( data )
      {
        var index = 0
        // For each row of table...
        $( "#gCodeTable td" )
          .each
          (
            function()
            {
              var isForward = $( "#reverseButton" ).val()

              if ( "1" == isForward )
              {
                $( "#gCodeForwardRow" ).attr( 'class', 'gCodeNextLine')
                $( "#gCodeReverseRow" ).attr( 'class', '' )
              }
              else
              {
                $( "#gCodeForwardRow" ).attr( 'class', '')
                $( "#gCodeReverseRow" ).attr( 'class', 'gCodeNextLine' )
              }

              // Get text for this row.
              var text = data[ index ]

              // If there isn't any text, put in a non-breaking space to
              // preserve the cell.
              if ( ! text )
                text = "&nbsp;"

              $( this ).html( text )
              index += 1
            }
          )
      }
    }
  )

  reverseButtonUpdate = winder.addToggleButton
  (
    "#reverseButton",
    "process.getG_CodeDirection()",
    "process.setG_CodeDirection( $ )"
  )

  loopButtonUpdate = winder.addToggleButton
  (
    "#loopButton",
    "process.getG_CodeLoop()",
    "process.setG_CodeLoop( $ )"
  )


}

//-----------------------------------------------------------------------------
// Uses:
//   Call when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    //winder.inhibitUpdates()
    apa = new APA()
  }
)

