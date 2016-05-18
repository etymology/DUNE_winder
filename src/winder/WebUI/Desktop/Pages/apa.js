
// True when the APA settings can be modified.  Used to prevent modifications
// to the APA while the machine is running.
var apaEnabled = true

// True when
var apaEnabledInhabit = false

var loopButtonUpdate
var reverseButtonUpdate

//-----------------------------------------------------------------------------
// Uses:
//   Enable all APA interface controls.
//-----------------------------------------------------------------------------
function enableAPA_Interface()
{
  apaEnabled = true
  $( "#apaSelection" ).prop( "disabled", false )
  $( "#layerSelection" ).prop( "disabled", false )
  $( "#gCodeSelection" ).prop( "disabled", false )
  $( "#apaName" ).prop( "disabled", false )
  $( "#apaNewButton" ).prop( "disabled", false )
  $( "#loading" ).html( "&nbsp;" )
  populateLists()

  if ( loopButtonUpdate )
    loopButtonUpdate()

  if ( reverseButtonUpdate )
    reverseButtonUpdate()
}

//-----------------------------------------------------------------------------
// Uses:
//   Disable all APA interface controls.
//-----------------------------------------------------------------------------
function disableAPA_Interface( message )
{
  apaEnabled = false
  $( "#loading" ).html( message )
  $( "#apaSelection" ).prop( "disabled", true )
  $( "#layerSelection" ).prop( "disabled", true )
  $( "#gCodeSelection" ).prop( "disabled", true )
  $( "#apaName" ).prop( "disabled", true )
  $( "#apaNewButton" ).prop( "disabled", true )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback to start/stop recipe execution.
// Input:
//   isRunning - True to start, false to stop.
//-----------------------------------------------------------------------------
function setRunningState( isRunning )
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
function reenableAPA()
{
  enableAPA_Interface()
  apaEnabledInhabit = false
}

//-----------------------------------------------------------------------------
// Uses:
//   APA selection callback.
//-----------------------------------------------------------------------------
function selectAPA()
{
  // Get the new APA selection.
  var apa = $( "#apaSelection" ).val()

  // If not the null selection...
  if ( "" != apa )
  {
    // Disable the APA interface during loading process.
    apaEnabledInhabit = true
    disableAPA_Interface( "Loading APA" )

    // Start loading new APA.
    winder.remoteAction
    (
      'process.switchAPA( "' + apa + '" )',
      reenableAPA
    )
  }
}

//-----------------------------------------------------------------------------
// Uses:
//   G-Code selection callback.
//-----------------------------------------------------------------------------
function selectG_Code()
{
  // Get the layer and G-Code recipe.
  var layer = $( "#layerSelection" ).val()
  var gCode = $( "#gCodeSelection" ).val()

  // If not the null selection...
  if ( "" != gCode )
  {
    // Disable APA interface during loading process.
    disableAPA_Interface( "Loading G-Code" )

    // Begin loading G-Code.
    winder.remoteAction
    (
      'process.apa.loadRecipe( "' + layer + '", "' + gCode + '", -1 )',
      reenableAPA
    )
  }
}

//-----------------------------------------------------------------------------
// Uses:
//   Load values for and repopulate all lists.
//-----------------------------------------------------------------------------
function populateLists()
{
  winder.populateComboBox
  (
    "#apaSelection",
    "process.getAPA_List()",
    "process.getLoadedAPA_Name()",
    function()
    {
      var selection = $( "#apaSelection" ).val()
      var isDisabled = ( "" == selection )
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
function newAPA()
{
  winder.remoteAction
  (
    'process.createAPA( "' + $( "#apaName" ).val() + '" )',
     populateLists
  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for setting next active G-Code line.
//-----------------------------------------------------------------------------
function gotoLine()
{
  winder.remoteAction( 'process.setG_CodeLine( ' + $( "#apaLine" ).val() + ' )' )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for setting G-Code breakpoint.
//-----------------------------------------------------------------------------
function runToLine()
{
  winder.remoteAction( "process.setG_CodeRunToLine( " + $( "#apaBreakLine" ).val() + " )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for setting spool wire amount.
//-----------------------------------------------------------------------------
function setSpool()
{
  winder.remoteAction( "process.spool.setWire( " + $( "#setSpool" ).val() + " )" )
}

//-----------------------------------------------------------------------------
// Uses:
//   Close the current APA.
//-----------------------------------------------------------------------------
function closeAPA()
{
  winder.remoteAction
  (
    "process.closeAPA()",
    populateLists
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
    // Populate lists and have this function run after error recovery.
    populateLists()
    winder.addErrorClearCallback( populateLists )

    // Set updates of current line and total lines.
    winder.addPeriodicRemoteDisplay( "process.gCodeHandler.getLine()", "#currentLine" )
    winder.addPeriodicRemoteDisplay( "process.gCodeHandler.getTotalLines()", "#totalLines" )
    winder.addPeriodicRemoteDisplay( "process.spool.getWire()", "#spoolAmount" )


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
          disableAPA_Interface( "Running." )
        }
        else
        if ( ( stopDisable )
          && ( ! apaEnabled )
          && ( ! apaEnabledInhabit ) )
        {
          enableAPA_Interface()
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

    //winder.inhibitUpdates()
  }
)

