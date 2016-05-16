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
      console.log( "Control version " + data )
      if ( data )
        $( "#controlVersion" ).attr( 'class', "" )
      else
        $( "#controlVersion" ).attr( 'class', "badVersion" )
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
      window.location = "?page=apa";
    else
    {
      // Begin loading the requested sub-page.
      winder.loadSubPage( "/Desktop/Pages/" + page, "#main" )

      // Initialize winder.
      winder.initialize()

      // Display system time.
      winder.addPeriodicRemoteDisplay( "systemTime.get()", "#systemTime" )

      // Update for primary state machine.
      winder.addPeriodicRemoteDisplay
      (
        "process.controlStateMachine.state.__class__.__name__",
        "#controlState",
        states,
        "controlState"
      )

      // Update for PLC state machine.
      winder.addPeriodicRemoteCallback
      (
        "io.plcLogic.getState()",
        function( value )
        {
          if ( null !== value )
          {
            stateTranslateTable =
            [
              "Init",
              "Ready",
              "XY jog",
              "XY seek",
              "Z jog",
              "Z seek",
              "Latching",
              "Latch homeing",
              "Latch release"
            ]

            value = stateTranslateTable[ value ]
            states[ "plcState" ] = value
            $( "#plcState" ).text( value )

          }
          else
            $( "#plcState" ).html( winder.errorString )
        }
      )

      // Load version information and have them reload on error.
      loadVersion()
      winder.addErrorClearCallback( loadVersion )

      // Start the periodic updates.
      winder.periodicRemoteUpdate()
    }
  }
)


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
