// Instance of winder interface.
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

  /*

  $$$FUTURE - This will load the new page without reloading everything.  Still
    isn't fully functional.

  if ( winder )
    winder.shutdown()

  winder = new WinderInterface()
  winder.loadSubPage( "/Desktop/Pages/" + page, "#main" )

  // Initialize winder.
  winder.initialize()

  // Display system time.
  winder.addPeriodicDisplay( "systemTime.get()", "#systemTime" )

  // Update for primary state machine.
  winder.addPeriodicDisplay
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
  winder.periodicUpdate()

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
      winder = new WinderInterface()

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

      // Begin loading the requested sub-page.
      winder.loadSubPage( "/Desktop/Pages/" + page, "#main" )

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
//   Callback for global stop button.
//-----------------------------------------------------------------------------
function fullStop()
{
  winder.remoteAction( 'process.stop()' )
}
