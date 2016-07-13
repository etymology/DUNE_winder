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

  var gCodeLine = {}

  var G_CODE_ROWS = 14

  var LOG_ENTIRES = 6

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

  var currentAPA = ""

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
        currentAPA = $( "#apaSelection" ).val()
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
  //   Callback to advance G-Code by one line.
  //-----------------------------------------------------------------------------
  this.nextLine = function()
  {
    if ( null != gCodeLine[ "currentLine" ] )
    {
      // Next line is the current line because the current line has been incremented
      // by 1.
      var nextLine = gCodeLine[ "currentLine" ]
      if ( nextLine < ( gCodeLine[ "totalLines" ] - 1 ) )
        winder.remoteAction( 'process.setG_CodeLine( ' + nextLine + ' )' )
    }
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback to retard G-Code by one line.
  //-----------------------------------------------------------------------------
  this.previousLine = function()
  {
    if ( null != gCodeLine[ "currentLine" ] )
    {
      var nextLine = gCodeLine[ "currentLine" ] - 2
      if ( nextLine >= -1 )
        winder.remoteAction( 'process.setG_CodeLine( ' + nextLine + ' )' )
    }
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for setting next active G-Code line.
  //-----------------------------------------------------------------------------
  this.gotoLine = function()
  {
    var line = $( "#apaLine" ).val() - 1
    var isForward = $( "#reverseButton" ).val()

    if ( "1" == isForward )
      line -= 1
    else
      line += 1

    winder.remoteAction( 'process.setG_CodeLine( ' + line + ' )' )
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
    // Get the values and convert to millimeters.
    var value = $( "#setSpool" ).val() * 1000
    winder.remoteAction( "process.spool.setWire( " + value + " )" )
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
  winder.addPeriodicCallback
  (
    "process.gCodeHandler.getLine()",
    function( data )
    {
      if ( null !== data )
      {
        data = data + 1
        gCodeLine[ "currentLine" ] = data
      }
      else
      {
        data = "-"
        gCodeLine[ "currentLine" ] = null
      }

      $( "#currentLine" ).text( data )
    }
  )

  winder.addPeriodicDisplay
  (
    "process.gCodeHandler.getTotalLines()",
    "#totalLines",
    gCodeLine,
    "totalLines"
  )

  winder.addPeriodicCallback
  (
    'process.spool.getWire()',
    function( data )
    {
      if ( data )
      {
        data /= 1000
        data = data.toLocaleString() + " meters"
      }
      else
        data = "-"

      $( "#spoolAmount" ).text( data )
    }
  )

  // Special periodic for current APA stage.
  winder.addPeriodicCallback
  (
    "process.getStage()",
    function( value )
    {
      var STAGES =
      [
        "Uninitialized",
        "X first",
        "X second",
        "V first",
        "V second",
        "U first",
        "U second",
        "G first",
        "G second",
        "Sign off",
        "Complete",
      ]

      // If there is no APA loaded, the value will be an empty string and
      // the options to change the stage need to be disabled.
      var isDisabled = false
      if ( "" === value )
      {
        stage = "(no APA loaded)"
        isDisabled = true
      }
      else
        // Translate the stage name.
        stage = STAGES[ value ]

      // Enable/disable APA stage control interface.
      $( "#apaStageSelect" ).prop( "disabled", isDisabled )
      $( "#apaStageReason" ).prop( "disabled", isDisabled )
      $( "#apaStageButton" ).prop( "disabled", isDisabled )

      // Display the current stage.
      $( "#apaStage" ).html( stage )
    }
  )

  // Callback function to initialize position graphic.
  // Called twice--once when the position graphic page is loaded, and again
  // when the motor status page is loaded.  Both must be loaded before
  // initialization can take place, and either could load first.
  var positionGraphicCount = 2
  positionGraphicInitialize = function()
  {
    positionGraphicCount -= 1
    if ( 0 == positionGraphicCount )
      positionGraphic.initialize( 0.465 )
  }

  winder.loadSubPage
  (
    "/Desktop/Modules/positionGraphic",
    "#positionGraphicDiv",
    positionGraphicInitialize
  )

  winder.loadSubPage
  (
    "/Desktop/Modules/motorStatus",
    "#motorStatusDiv",
    positionGraphicInitialize
  )

  // Callback run after period updates happen to enable/disable APA controls
  // depending on machine state.
  winder.addPeriodicEndCallback
  (
    function()
    {
      // Display control state.
      var controlState = states[ "controlState" ]
      $( "#controlState" ).text( controlState )

      // Start button enable.
      var startDisable = ( "StopMode" != controlState ) || apaEnabledInhabit
      $( "#startButton" ).prop( "disabled", startDisable )

      var isCloseDisabled = ( "" == currentAPA ) || isRunning()
      $( "#apaCloseButton" ).prop( "disabled", isCloseDisabled )

      //$( "#apaCloseButton" ).prop( "disabled", startDisable )

      // Stop button enable.
      var stopDisable = ( "WindMode" != controlState )
      $( "#stopButton" ).prop( "disabled", stopDisable )

      // If the winder was stopped and is now running disable APA selection.
      if ( ( ! stopDisable )
        && ( apaEnabled )
        && ( ! apaEnabledInhabit ) )
      {
        self.disableAPA_Interface( "Running." )
      }
      else
      // If the winder was running but is now stopped enable APA selection.
      if ( ( stopDisable )
        && ( ! apaEnabled )
        && ( ! apaEnabledInhabit ) )
      {
        self.enableAPA_Interface()
      }
    }

  )

  winder.addPeriodicEndCallback


  var totalRows = G_CODE_ROWS * 2 + 1
  $( "#gCodeTable" ).empty()
  var gGodeBody = $( "<tbody/>" ).appendTo( "#gCodeTable" )
  var gCodeMid = totalRows / 2
  for ( var rowIndex = 0; rowIndex < totalRows; rowIndex += 1 )
  {
    var newRow = $( "<tr/>" ).appendTo( gGodeBody )

    if ( G_CODE_ROWS == rowIndex )
      newRow.attr( "class", "gCodeCurrentLine" )
    else
    if ( G_CODE_ROWS - 1 == rowIndex )
      newRow.attr( "id", "gCodeReverseRow" )
    else
    if ( G_CODE_ROWS + 1 == rowIndex )
      newRow.attr( "id", "gCodeForwardRow" )

    var newCell = $( "<td/>" ).appendTo( newRow ).html( "&nbsp;" )
  }

  // Setup G-Code table.
  winder.addPeriodicCallback
  (
    "process.getG_CodeList( None, " + G_CODE_ROWS + " )",
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

  createSlider = function( slider, getString, setString )
  {
    var isLoad = true
    velocitySliderFunction =
      function( event, ui )
      {
        $( "#" + slider + "Value" ).html( ui.value + "%" )
      }

    $( "#" + slider + "Slider" )
      .slider
      (
        {
          min: 5,
          max: 100,
          value: 100,
          step: 5,

          change: function( event, ui )
          {
            if ( ! isLoad )
            {
              var value = ui.value / 100.0
              winder.remoteAction( setString + "( " + value + " )" )
            }
            velocitySliderFunction( event, ui )
            isLoad = false
          },

          slide: velocitySliderFunction
        }
      )

      var readSlider = function()
      {
        winder.remoteAction
        (
          getString + "()",
          function( value )
          {
            isLoad = true
            value *= 100
            $( "#" + slider + "Slider" ).slider( "value", value )
          }
        )
      }

      readSlider()
      winder.addErrorClearCallback( readSlider )
  }

  createSlider( "velocity", "process.gCodeHandler.getVelocityScale", "process.setG_CodeVelocityScale" )
  //createSlider( "acceleration" )
  //createSlider( "deceleration" )

  var table = $( "<table />" ).appendTo( "#recentLog" )
  var row = $( "<tr />" ).appendTo( table )
  $( "<th />" ).appendTo( row ).text( "Time" )
  $( "<th />" ).appendTo( row ).text( "Description" )
  for ( var index = 0; index < LOG_ENTIRES; index += 1 )
  {
    var row = $( "<tr />" ).appendTo( table )
    $( "<td />" )
      .appendTo( row )
      .attr( "id", "logTable" + index + "Time" )
      .text( "-" )

    $( "<td />" )
      .appendTo( row )
      .attr( "id", "logTable" + index + "Description" )
      .text( "-" )
  }

  winder.addPeriodicCallback
  (
    "log.getRecent()",
    function( data )
    {
      for ( var index = 0; index < LOG_ENTIRES; index += 1 )
      {
        var dataIndex = -1

        if ( data )
        {
          dataIndex = data.length - index - 1

          var row = [ "-", "-", "-", "-" ]
          if ( dataIndex >= 0 )
            row = data[ data.length - index - 1 ].split( "\t" )

          // Get the time/date of occurrence and format it for local time.
          var time = new Date( row[ 0 ] + 'Z' )
          var timeString = $.format.date( time, "yyyy-MM-dd HH:mm:ss.SSS")

          var description = row[ 3 ]
          $( "#logTable" + index + "Time" ).text( timeString )
          $( "#logTable" + index + "Description" ).text( description )
        }
        else
        {
          $( "#logTable" + index + "Time" ).text( "--" )
          $( "#logTable" + index + "Description" ).text( "--" )
        }
      }
    }
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

