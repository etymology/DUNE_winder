function Log()
{
  //-----------------------------------------------------------------------------
  // Uses:
  //   Load the log data into a filtered table.
  // Input:
  //   loadAll - True if all log data should be loaded, false to only load some.
  //-----------------------------------------------------------------------------
  this.loadData = function( loadAll )
  {
    // Filter table object with columns for the log file.
    var filteredTable =
        new FilteredTable
        (
          [ "Time", "Module", "Type", "Description" ],
          [ false, true, true, false ],
          [ "200px", "25px", "25px" ]
        )

    var query = "log.getAll( 50 )"
    if ( loadAll )
      query = "log.getAll()"

    var loadingText = $( "<p />" )
      .attr( "id", "logTable" )
      .text( "Loading..." )

    $( "#logTable" ).replaceWith( loadingText )

    winder.remoteAction
    (
      query,
      function( data )
      {
        var dataSet = []

        for ( item of data )
          dataSet.push( item.split( "\t" ) )

        filteredTable.loadFromArray( dataSet )
        filteredTable.setSort( 0, 1 )
        filteredTable.display( "#logTable" )

        $( "#logEntries" ).text( dataSet.length )
      }
    )
  }

  // Toggle button to select full-log or partial log display.
  winder.addToggleButton
  (
    "#fullLog",
    null,
    null,
    null,
    this.loadData
  )

  // Load initial data.
  this.loadData( false )
}

//-----------------------------------------------------------------------------
// Uses:
//   Call when page loads.
//-----------------------------------------------------------------------------
$( document ).ready
(
  function()
  {
    log = new Log()
  }
)

