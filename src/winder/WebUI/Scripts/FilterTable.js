///////////////////////////////////////////////////////////////////////////////
// Name: FilterTable.js
// Uses: Table that has filtered columns and is sortable.
// Date: 2016-05-11
// Author(s):
//   Andrew Que <aque@bb7.com>
///////////////////////////////////////////////////////////////////////////////

//=============================================================================
// Uses:
//   A filterable, sortable table display class.
// Inputs:
//   columnNames - Array of column names.
//   columnFilterEnables - Either:
//     An array of booleans as to which columns should allow filters (true),
//     and which should not (false).
//     True/false to enable/disable filters on all columns.
//   columnWidth - An array of width parameters for each column.  Optional.
//=============================================================================
function FilteredTable( columnNames, columnFilterEnables, columnWidths )
{
  var self = this

  this.id = Math.floor( Math.random() * 0xFFFFFFFF )

  // Table data.
  var data

  var activeFilter = [ null, "" ]
  var sortColumn = null
  var sortDirection = null

  var filteredData

  // If using a global filter enable, or no filters are enabled...
  if ( ( false === columnFilterEnables )
    || ( true === columnFilterEnables )
    || ( undefined === columnFilterEnables ) )
  {
    // Assume they don't want filtering options (sorting only).
    var defaultSetting = false

    // If all columns are to allow filtering...
    if ( columnFilterEnables )
      defaultSetting = true

    // Build filter enables with default value.
    columnFilterEnables = []
    for ( var index in columnNames )
    {
      var column = columnNames[ index ]
      columnFilterEnables.push( defaultSetting )
    }
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Get a list of all the unique items from a column.
  //---------------------------------------------------------------------------
  this.getUnique = function( column )
  {
    var results = []
    for ( var rowIndex in data )
    {
      var row = data[ rowIndex ]
      var item = row[ column ]
      if ( results.indexOf( item ) == -1 )
        results.push( item )
    }

    return results
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Filter the data displayed.
  // Inputs:
  //   column - Index of the column to filter.  Optional.
  //   filter - Data to allow in column.  Optional.
  // Note:
  //   If column and filter are omitted, the last filter is used.  Useful to
  //   recompute displayed data.
  //   This only sets the filter--must call display to show results.
  //---------------------------------------------------------------------------
  this.filter = function( column, filter )
  {
    filteredData = []

    if ( column && filter )
      activeFilter = [ column, filter ]
    else
    {
      column = activeFilter[ 0 ]
      filter = activeFilter[ 1 ]
    }

    // If there is a filter to apply...
    if ( "" != filter )
    {
      // Loop through all the raw data looking for matches...
      for ( var rowIndex in data )
      {
        row = data[ rowIndex ]
        // If this row is a match, add it to the filter data.
        if ( row[ column ] == filter )
          filteredData.push( row )
      }
    }
    else
      // Make copy of data.
      filteredData = data.slice()

    // If sorting is enabled...
    if ( ( null !== sortColumn )
      && ( null !== sortDirection ) )
    {
      // Do a sort using a custom callback that sorts based on the select column
      // and direction of sort.
      filteredData.sort
      (
        function( a, b )
        {
          // Get the objects in the selected column as strings.
          a = a[ sortColumn ].toString()
          b = b[ sortColumn ].toString()

          // Compare strings.
          var result = a.localeCompare( b )

          // Account for sort direction.
          // (Remember: sort direction is either 1 or -1.)
          result *= sortDirection

          return result
        }
      )
    }
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Set the sorting order.
  // Input:
  //   column - Which column to sort by.
  //   direction - True for low to high, false for high to low.
  // Note:
  //   This only sets the sort--must call display to show sorted results.
  //---------------------------------------------------------------------------
  this.setSort = function( column, direction )
  {
    sortColumn = column

    if ( direction )
      direction = 1
    else
      direction = -1

    sortDirection = direction

    // Re-run the filter.
    self.filter()
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Display the filtered data.
  // Inputs:
  //   tableId - Id of the table tag to place data.  Tag will be overwritten.
  //---------------------------------------------------------------------------
  this.display = function( tableId )
  {
    // Tag id without hash character.
    var idString = tableId.replace( "#", "" )

    // Create a new table element to replace old.
    var table = $( "<table />" ).attr( "id", idString )
    $( tableId ).replaceWith( table )

    // If there are column widths to use...
    if ( columnWidths )
    {
      // For each of the columns, set the width.
      // NOTE: Additional styles can be applied from style sheet--this is only
      // for widths.
      var tableRow = $( "<colgroup />" ).appendTo( table )
      for ( var index in columnWidths )
      {
        var width = columnWidths[ index ]
        $( "<col/>" )
          .appendTo( tableRow )
          .width( width )
      }
    }

    var tableHeader = $( "<thead />" ).appendTo( table )

    // Table heading with column names.
    var tableRow = $( "<tr />" ).appendTo( tableHeader )
    for ( var columnIndex in columnNames )
    {
      // Look up column name.
      var columnName = columnNames[ columnIndex ]

      // Alias the column index for callback function.
      let localColumn = columnIndex

      var cell = $( "<th/>" )
        .appendTo( tableRow )
        .text( columnName )
        .click
        (
          function()
          {
            var message = $( "<p />" ).attr( "id", idString ).text( "Sorting..." )
            $( tableId ).replaceWith( message )

            if ( localColumn != sortColumn )
            {
              sortColumn = localColumn
              sortDirection = 1
            }
            else
              sortDirection *= -1

            self.filter()
            self.display( tableId )
          }
        )

      // If this is the sorted column, draw the arrow.
      if ( columnIndex == sortColumn )
      {
        var arrow = "&#8593;"
        if ( -1 == sortDirection )
          arrow = "&#8595;"

        // Create a <div> tag to hold sorting arrow.
        var labelId = "columnSort_" + this.id + "_" + columnIndex
        $( "<div/>" )
          .attr( "id", labelId )
          .css
          (
            {
              "border" : "none",
              "background" : "none",
              "float" : "right",
              "margin" : 0,
              "padding" : 0
            }
          )
          .html( arrow )
          .appendTo( cell )

      }
    }

    // Filter drop-downs.
    tableRow = $( "<tr />" ).appendTo( tableHeader )
    for ( var column in columnNames )
    {
      // If this column can be filtered...
      if ( columnFilterEnables[ column ] )
      {
        var cell = $( "<td/>" ).appendTo( tableRow )

        // Localize column for callback function.
        let currentColumn = column

        // Pull-down select tag with a callback to apply a filter to this
        // column.
        var selectElement =
          $( '<select />' )
            .appendTo( cell )
            .change
            (
              function()
              {
                // Get the filter value.
                var filter = $( this ).val()

                // Filter this column using the filter value.
                self.filter( currentColumn, filter )

                // Redraw table.
                self.display( tableId )
              }
            )

        // Default no filtering option.
        $( "<option></option>" ).appendTo( selectElement )

        // Get all the unique items in this column.
        var items = this.getUnique( column )

        // Display filtering options for column.
        for ( var index in items )
        {
          var item = items[ index ]
          $( "<option />" )
            .appendTo( selectElement )
            .text( item )
        }

        // Select the active filter (if filtering is enabled).
        if ( activeFilter[ 0 ] == column )
          selectElement.val( activeFilter[ 1 ] )
        else
          selectElement.val( "" )

      }
      else
        // If no filter for this column, just make a blank column.
        $( "<td/>" ).appendTo( tableRow )

    }

    // If there is as yet no filtered data, use the full data set.
    if ( ! filteredData )
      filteredData = data

    // Fill the body of the table with data.
    var tableBody = $( "<tbody />" ).appendTo( table )
    for ( var row in filteredData )
    {
      var rowData = filteredData[ row ]
      var tableRow = $( "<tr />" ).appendTo( tableBody )
      for ( var index in rowData )
      {
        var item = rowData[ index ]
        $( "<td/>" )
          .appendTo( tableRow )
          .attr( "id", "cell_" + this.id + "_" + row + "_" + index )
          .text( item )
      }
    }

  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Load table data from an array.
  // Input:
  //   newData - 2d array with all data for the table.
  //   columnMapping - Translation table to map which column of the input data
  //     go to which columns of the table.  Optional.
  // Example:
  //   var columnNames = [ 'Name', 'Birth', 'Weight', 'SSN' ]
  //   var columnMapping = [ 0, 2, 1 ]
  //   var data =
  //     [
  //       [ 'Bob', '1/1/1970', 150, 123-45-6789 ],
  //       [ 'Jane','2/2/1972', 120, 123-45-5429 ],
  //       [ 'Jim', '3/3/1973', 170, 123-45-6234 ]
  //     ]
  //   var filteredTable = new FilteredTable( columnNames )
  //   filteredTable.loadFromArray( data, columnMapping )
  //
  //   In the example, the SSN column is not displayed in the table, and weight
  //   is displayed before birth.
  //---------------------------------------------------------------------------
  this.loadFromArray = function( newData, columnMapping )
  {
    data = []

    // If no column mapping is given, assume a 1:1 correlation between the new
    // data and the resulting data.
    if ( ! columnMapping )
    {
      columnMapping = []
      for ( var index in columnNames )
        columnMapping.push( index )
    }

    // Loop through all rows in new data...
    for ( var rowIndex in newData )
    {
      var row = newData[ rowIndex ]
      // Build a row using column mapping.
      // Allows columns to be out-of-order or ignored all together.
      var rowData = []
      for ( var mappingIndex in columnMapping )
      {
        var itemIndex = columnMapping[ mappingIndex ]
        var item = row[ itemIndex ]

        rowData.push( item )
      }

      data.push( rowData )
    }
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Get the cell id for a given row and column.
  // Input:
  //   row - Desired row.
  //   column - Desired column.
  // Output:
  //   Tag id for desired cell.
  //---------------------------------------------------------------------------
  this.getCellId = function( row, column )
  {
    return "cell_" + this.id + "_" + row + "_" + column
  }

}

