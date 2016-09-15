// Instance of winder interface.
var winder = new WinderInterface()

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
//  window.location = "?page=" + page;

  if ( winder )
    winder.shutdown()

  winder = new WinderInterface()
  $( '#main' ).html( "Loading..." )
  $( 'head link, head style' ).remove()

  var cssLink =
    $( "<link rel='stylesheet' type='text/css' href='/Mobile/main.css'>" )

  $( "head" ).append( cssLink )
  winder.loadSubPage( "/Mobile/Pages/" + page, "#main" )

  winder.periodicUpdate()
}

//-----------------------------------------------------------------------------
// Uses:
//   Called when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    var page = getParameterByName( "page" )
    if ( ! page )
      window.location = "?page=menu";
    else
    {
      // Begin loading the requested sub-page.
      winder.loadSubPage( "/Mobile/Pages/" + page, "#main" )

      // Start the periodic updates.
      winder.periodicUpdate()
    }
  }
)
