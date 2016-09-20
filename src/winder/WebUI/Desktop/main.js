// Instance of winder interface.
var winder

var baseStylesheets = []

// Software version variables.
var softwareVersion =
{
  "controlVersion" : 0,
  "uiVersion" : 0
}

// Status of state machines.
var states =
{
  "controlState" : 0,
  "plcState" : 0
}

//-----------------------------------------------------------------------------
// Uses:
//   See if machine is running based on control state.
// Output:
//   True if running, false if not.
//-----------------------------------------------------------------------------
function isRunning()
{
  var state = states[ "controlState" ]
  var result = ( "StopMode" != state ) && ( "HardwareMode" != state )
  return result
}

//-----------------------------------------------------------------------------
// Uses:
//   Get a parameter in the GET portion of the URL.
// Input:
//   name - Name of parameter to return.
//   url - Full URL.  If left blank the URL of the current page is used.
// Output:
//   Value of the named parameter.
// Notes:
//   Copied from StackOverflow.com.
//-----------------------------------------------------------------------------
function getParameterByName( name, url )
{
  if ( ! url )
    url = window.location.href

  name = name.replace( /[\[\]]/g, "\\$&" )
  var regex = new RegExp( "[?&]" + name + "(=([^&#]*)|&|#|$)" )
  var results = regex.exec( url )

  var returnResult
  if ( ! results )
    returnResult = null
  else
  if ( ! results[ 2 ] )
    returnResult = ''
  else
    returnResult = decodeURIComponent( results[ 2 ].replace( /\+/g, " " ) )

  return returnResult
}

//-----------------------------------------------------------------------------
// Uses:
//   Load and display the version information.
//-----------------------------------------------------------------------------
function loadVersion()
{
  winder.singleRemoteDisplay
  (
    "version.getVersion()",
    "#controlVersion",
    softwareVersion,
    "controlVersion"
  )

  winder.remoteAction
  (
    "version.isValid()",
    function( data )
    {
      if ( data )
        $( "#controlVersion" ).attr( 'class', "" )
      else
        $( "#controlVersion" ).attr( 'class', "badVersion"  )
    }
  )

  winder.singleRemoteDisplay
  (
    "uiVersion.getVersion()",
    "#uiVersion",
    softwareVersion,
    "uiVersion"
  )

  winder.remoteAction
  (
    "uiVersion.isValid()",
    function( data )
    {
      if ( data )
        $( "#uiVersion" ).attr( 'class', "" )
      else
        $( "#uiVersion" ).attr( 'class', "badVersion" )
    }
  )

}

function setupMainScreen()
{
  // Before sub-pages begin to load, register a callback to run after all
  // have been loaded.
  winder.addFullyLoadedCallback
  (
    function()
    {
      $( "main article" ).each
      (
        function()
        {
          //$( this ).draggable().resizable()
        }
      )

      $( "button.makeToggle" )
        .each
        (
          function()
          {
            if ( $( this ).val() )
              $( this ).attr( "class", "toggleDown" )
            else
              $( this ).attr( "class", "toggle" )

            //if ( ! $( this ).click() )
            {
              $( this )
                .click
                (
                  function()
                  {
                    $( this ).toggleClass( "toggle" )
                    $( this ).toggleClass( "toggleDown" )

                    var value = 0
                    if ( $( this ).attr( 'class' ) == "toggleDown" )
                      value = 1

                    $( this ).val( value )
                  }
                )
            }

          }
        )
    }
  )

  // Display system time.
  winder.addPeriodicDisplay
  (
    "systemTime.get()",
    "#systemTime",
    null,
    null,
    function( data )
    {
      var timeString = "--"
      if ( data )
      {
        var time = new Date( data + 'Z' )
        timeString = $.format.date( time, "yyyy-MM-dd HH:mm:ss.SSS")
      }

      return timeString
    }
  )

  // Update for primary state machine.
  winder.addPeriodicDisplay
  (
    "process.controlStateMachine.state.__class__.__name__",
    "#controlState",
    states,
    "controlState"
  )

  // Update for PLC state machine.
  winder.addPeriodicCallback
  (
    "io.plcLogic.getState()",
    function( value )
    {
      if ( null !== value )
      {
        var stateTranslateTable =
        [
          "Init",          // 0
          "Ready",         // 1
          "XY jog",        // 2
          "XY seek",       // 3
          "Z jog",         // 4
          "Z seek",        // 5
          "Latching",      // 6
          "Latch homing",  // 7
          "Latch release", // 8
          "Unservo",       // 9
          "Error"          // 10
        ]

        var stringValue = stateTranslateTable[ value ]
        states[ "plcState" ] = stringValue
        $( "#plcState" ).text( stringValue )

        // Change the CSS class for a PLC state error.
        if ( 10 == value )
          $( "#plcState" ).attr( 'class', 'plcError' )
        else
          $( "#plcState" ).attr( 'class', '' )

      }
      else
        $( "#plcState" ).html( winder.errorString )
    }
  )

  winder.addPeriodicEndCallback
  (
    function()
    {
      var controlState = states[ "controlState" ]
      var plcState = states[ "plcState" ]
      var isDisabled =
           ( "StopMode" == controlState )
        || ( "HardwareMode" == controlState )
        || ( "Unservo" == plcState )

      $( "#fullStopButton" ).prop( "disabled", isDisabled )
      $( "#controlState" ).text( controlState )
    }
  )

  // Load version information and have them reload on error.
  loadVersion()
  winder.addErrorClearCallback( loadVersion )

  // Start the periodic updates.
  winder.periodicUpdate()
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for loading an other page.
// Input:
//   page - Desired page to load.
//-----------------------------------------------------------------------------
function load( page )
{
  if ( winder )
    winder.shutdown()

  winder = new WinderInterface()
  $( '#main' ).html( "Loading..." )

  // Remove all styles sheets that are not base styles.
  $( 'head' )
    .find( 'link' )
    .each
    (
      function()
      {
        // Where did this style sheet come from?
        var url = $( this ).attr( 'href' )

        // Is it a base style sheet?
        if ( -1 == baseStylesheets.indexOf( url ) )
          // Remove it.
          $( this ).remove()
      }
    )

  // Loading sub page and setup main screen after sub page finishes loading.
  winder.loadSubPage
  (
    "/Desktop/Pages/" + page, "#main",
    setupMainScreen
  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Called when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    // Get the requested page.
    var page = getParameterByName( "page" )

    // If there is no page, use default.
    if ( ! page )
      page = "apa"

    // Save all the loaded style sheet URLs.  These need to stay regardless
    // of what page is loaded.
    $( 'head' )
      .find( 'link' )
      .each
      (
        function()
        {
          // Add to list of base style sheets.
          baseStylesheets.push( $( this ).attr( 'href' ) )
        }
      )

    // $$$FUTURE // Check authentication either load requested page, or show grid page.
    // $$$FUTURE winder = new WinderInterface()
    // $$$FUTURE winder.remoteAction
    // $$$FUTURE (
    // $$$FUTURE   'RemoteSession.isAuthenticated( "' + $.cookie( "sessionId" ) + '" )',
    // $$$FUTURE   function( status )
    // $$$FUTURE   {
    // $$$FUTURE     console.log( "isAuthenticated = " + status )
    // $$$FUTURE     if ( ! status )
    // $$$FUTURE     {
    // $$$FUTURE       load( "grid" )
    // $$$FUTURE       $( "#loginDiv" ).css( "display", "block" )
    // $$$FUTURE     }
    // $$$FUTURE     else
    // $$$FUTURE     {
                       $( "#pageSelectDiv" ).css( "display", "block" )
                       $( "#fullStopDiv" ).css( "display", "block" )
                       $( "#loginDiv" ).css( "display", "none" )

                       // Load the requested page.
                       load( page )
    // $$$FUTURE     }
    // $$$FUTURE   }
    // $$$FUTURE )
  }
)

//-----------------------------------------------------------------------------
// Uses:
//   Callback when version information box is clicked.
//-----------------------------------------------------------------------------
function showVersionInformation()
{
  winder.loadSubPage
  (
    "/Desktop/Modules/overlay",
    "#modalDiv",
    function()
    {
      winder.loadSubPage( "/Desktop/Modules/versionDetails", "#overlayBox" )
    }
  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback when version information box is clicked.
//-----------------------------------------------------------------------------
function showLogin()
{
  winder.loadSubPage
  (
    "/Desktop/Modules/overlay",
    "#modalDiv",
    function()
    {
      winder.loadSubPage( "/Desktop/Modules/login", "#overlayBox" )
    }
  )
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for global stop button.
//-----------------------------------------------------------------------------
function fullStop()
{
  winder.remoteAction( 'process.stop()' )
}
