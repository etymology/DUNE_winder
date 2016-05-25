// Instance of winder interface.
//var winder = new WinderInterface()
var winder

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
//   $$$DEBUG
// Input:
// Output:
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
var activeDiv = null
function load( page )
{
  window.location = "?page=" + page;

  /*if ( winder )
    winder.shutdown()

  winder = new WinderInterface()
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

  winder.addPeriodicEndCallback
  (
    function()
    {
      var value = states[ "controlState" ]
      var isDisabled = ( "StopMode" == value ) || ( "HardwareMode" == value )
      $( "#fullStopButton" ).prop( "disabled", isDisabled )
      $( "#controlState" ).text( value )
      states[ "controlState" ] = value
    }
  )

  // Update for PLC state machine.
  winder.addPeriodicRemoteCallback
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
          "Latch release"  // 8
        ]

        var stringValue = stateTranslateTable[ value ]
        states[ "plcState" ] = stringValue
        $( "#plcState" ).text( stringValue )
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

  /*if ( activeDiv )
  {
    var oldDiv = activeDiv
    $( activeDiv )
      .css
      (
        {
          position: "absolute"
        }
      )
      .animate
      (
        {
          width: 0,
          height: 0
        },
        //{
        //  complete: function()
        //  {
        //    $( oldDiv ).remove()
        //  }
        //}
      )
  }

  activeDiv = $( "<div />" ).appendTo( "#main" )
  winder.loadSubPage( "/Desktop/Pages/" + page, activeDiv )*/
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
      //load( page )

      winder = new WinderInterface()

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

      winder.addPeriodicEndCallback
      (
        function()
        {
          var value = states[ "controlState" ]
          var isDisabled = ( "StopMode" == value ) || ( "HardwareMode" == value )
          $( "#fullStopButton" ).prop( "disabled", isDisabled )
          $( "#controlState" ).text( value )
          states[ "controlState" ] = value
        }
      )

      // Update for PLC state machine.
      winder.addPeriodicRemoteCallback
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
              "",              // 9
              "Error"          // 10
            ]

            var stringValue = stateTranslateTable[ value ]
            states[ "plcState" ] = stringValue
            $( "#plcState" ).text( stringValue )
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

function fullStop()
{
  winder.remoteAction( 'process.stop()' )
}