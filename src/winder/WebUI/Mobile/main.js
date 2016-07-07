// Instance of winder interface.
var winder = new WinderInterface()

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
    url = window.location.href;

  name = name.replace( /[\[\]]/g, "\\$&" );
  var regex = new RegExp( "[?&]" + name + "(=([^&#]*)|&|#|$)" );
  var results = regex.exec( url );

  var returnResult;
  if ( ! results )
    returnResult = null;
  else
  if ( ! results[ 2 ] )
    returnResult ='';
  else
    returnResult = decodeURIComponent( results[ 2 ].replace( /\+/g, " " ) );

  return returnResult;
}

//-----------------------------------------------------------------------------
// Uses:
//   Callback for loading an other page.
// Input:
//   page - Desired page to load.
//-----------------------------------------------------------------------------
function load( page )
{
  window.location = "?page=" + page;
}

//-----------------------------------------------------------------------------
// Uses:
//   Load and display the version information.
//-----------------------------------------------------------------------------
function loadVersion()
{
  winder.singleRemoteDisplay
  (
    "Settings.getVersion()",
    "#controlVersion",
    softwareVersion,
    "controlVersion"
  )

  winder.readXML_Display
  (
    "/version.xml",
    "Major",
    "#uiVersion",
    softwareVersion,
    "uiVersion"
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
    var page = getParameterByName( "page" )
    if ( ! page )
      window.location = "?page=jog";
    else
    {
      // Begin loading the requested sub-page.
      winder.loadSubPage( "/Mobile/Pages/" + page, "#main" )

      // Initialize winder.
      //winder.initialize()

      // // Display system time.
      // winder.addPeriodicDisplay( "systemTime.get()", "#systemTime" )
      //
      // // Update for primary state machine.
      // winder.addPeriodicDisplay
      // (
      //   "process.controlStateMachine.state.__class__.__name__",
      //   "#controlState",
      //   states,
      //   "controlState"
      // )
      //
      // // Update for PLC state machine.
      // winder.addPeriodicCallback
      // (
      //   "io.plcLogic.getState()",
      //   function( value )
      //   {
      //     if ( null !== value )
      //     {
      //       stateTranslateTable =
      //       [
      //         "Init",
      //         "Ready",
      //         "XY jog",
      //         "XY seek",
      //         "Z jog",
      //         "Z seek",
      //         "Latching",
      //         "Latch homeing",
      //         "Latch release"
      //       ]
      //
      //       value = stateTranslateTable[ value ]
      //       states[ "plcState" ] = value
      //       $( "#plcState" ).text( value )
      //
      //     }
      //     else
      //       $( "#plcState" ).html( winder.errorString )
      //   }
      // )
      //
      // // Load version information and have them reload on error.
      // loadVersion()
      // winder.addErrorClearCallback( loadVersion )

      // Start the periodic updates.
      winder.periodicUpdate()
    }
  }
)
