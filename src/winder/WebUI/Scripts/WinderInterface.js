///////////////////////////////////////////////////////////////////////////////
// Name: WinderInterface.js
// Uses: Interface to winder control.
// Date: 2016-05-03
// Author(s):
//   Andrew Que <aque@bb7.com>
// Example:
//   Creating an instance:
//     var winder = new WinterInterface()
// Notes:
//   Avoid uses ECMAScript 6 functions (let, const, class, etc.) because not all
//   mobile browers support these functions.
///////////////////////////////////////////////////////////////////////////////

var WinderInterface = function()
{
  // Reference to ourselves.
  var self = this

  // Set to true in order to always force a reload (rather than used cached
  // loads).  Should be false for production for best performance.
  var FORCE_RELOAD = true

  // Set to true to shutdown periodic updates.
  var periodicShutdown = false

  // Delay (in milliseconds) between periodic updates.
  var updateRate = 100

  // True when unable to communicate to winder.
  var isInError = false

  // List of remote commands that are updated periodically, and the callbacks run
  // when they have new data.
  var periodicCallbacks = []

  // Last values of each of the remote commands.  Used so that only values
  // that have changed get a callback.
  var periodicHistory = {}

  // Semaphore to prevent periodic update command from running multiple
  // instances.  Can happen if network delay is too long.
  var periodicUpdateSemaphore = 0

  // The enable status of buttons/inputs/selects.  Used to save the current
  // state of these tags before disabling them in the event of an error.
  var buttonEnables

  // The periodic remote commands are each assigned an id because there needs
  // to be a way to translate from a remote query to the data returned by that
  // query.  Two dictionaries are used to do this.
  //   periodicQuery maps an id to a remote query.
  //   periodicCallbackTable maps an id to a callback function.
  // This intermediate id is needed because the query probably isn't safe as
  // an XML field name.  So a unique id is used instead.  The id simply takes
  // the form "idN" where N is an integer number starting at 0 and incrementing
  // by one for each periodic query.
  var periodicCallbackTable = {}
  var periodicQuery = {}

  // Callbacks to run when an error occurs.
  var onErrorCallbacks = []

  // Callback to run when an error state clears.
  var onErrorClearCallbacks = []

  // Callbacks to run when periodic functions have all been run.
  var onPeriodicEndCallbacks = []

  // Callbacks run once pages is completely loaded.
  var onFullyLoadedCallbacks = []

  // Default error string.
  this.errorString = '<span class="error">X</span>'

  // Enable states of the toggle buttons.  If an error occurs, all the toggle buttons are
  // disabled.  The state they were before being disabled is saved in this map.
  var toggleButtonStates = {}

  // Number of pages currently still loading.
  // Used for triggering fully-loaded event.
  var pagesLoading = 0

  //---------------------------------------------------------------------------
  // Uses:
  //   Populate a combobox was elements from a remote query.
  // Input:
  //  tagId - The id of the combobox to populate.
  //  remoteCommand - Command that returns combobox option data.
  //  selectCommand - Optional command that returns the current selection.
  //  additionalCallback - Optional callback to run after list has been loaded.
  // Notes:
  //   The remote command needs to be a function that returns a list.  Each
  //   item of the list is then made an option in the combobox.
  //   The combobox will first be emptied.
  //   The first entry of the combobox is always blank.
  //---------------------------------------------------------------------------
  this.populateComboBox = function( tagId, remoteCommand, selectCommand, additionalCallback )
  {
    // Issue remote command.
    self.remoteAction
    (
      remoteCommand,
      function( data )
      {
        // Empty the combobox and make first entry blank.
        $( tagId )
          .empty()
          .append
          (
            $( "<option />" )
              .val( "" )
              .text( "" )
          )

        // Loop through result data and add an option for each element.
        for ( var dataIndex in data )
        {
          var item = data[ dataIndex ]
          $( tagId )
            .append
            (
              $( "<option />" )
                .val( item )
                .text( item )
            )
        }
        // If there is a command to get the current selection, run it.
        if ( selectCommand )
        {
          // Issue remote command.
          self.remoteAction
          (
            selectCommand,
            function( data )
            {
              $( tagId ).val( data )

              if ( additionalCallback )
                additionalCallback()
            }
          )
        }

      }
    )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a sub-page to current page.
  // Input:
  //   page - Filename (less extension) to load.
  //   tag - The id of the location to append this data.  Typically a <article>.
  //   callback - Function to run after everything has loaded.
  //   callbackParameters - Parameters to pass to callback.
  // Notes:
  //   The page must have the extension "html".  In addition this function will
  //   also load the page with the extension ".js".
  //---------------------------------------------------------------------------
  this.loadSubPage = function( page, tag, callback, callbackParameters )
  {
    // The random line is added to the end of a URL to force the browser to
    // actually load the data.  Otherwise, the browser may used a cached
    // version.
    var randomLine = ""
    if ( FORCE_RELOAD )
      randomLine = "?random=" + Math.random()

    var cssLink =
      $( "<link rel='stylesheet' type='text/css' href='" + page + ".css" + randomLine + "'>" )

    $( "head" ).append( cssLink )

    // Denote an other page is loading.
    pagesLoading += 1

    $( tag )
      .load
      (
        page + ".html" + randomLine ,
        function()
        {
          // Load the Javascipt for this page.
          // NOTE: Done after the page loads so that all elements have been
          // created before Javascript runs.
          $.getScript
          (
            page + ".js",
            function()
            {
              // If there is a callback once page is finished loading, run it.
              if ( callback )
                callback( callbackParameters )

              // One more page is finished loading.
              pagesLoading -= 1

              // If all pages have been loaded, run fully loaded callbacks.
              if ( 0 == pagesLoading )
                for ( var index in onFullyLoadedCallbacks )
                  onFullyLoadedCallbacks[ index ]()
            }
          )
        }
      )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Get updated values for all data read periodically and run their callbacks
  //   if any of the data has changed.  Internal function--no need to call
  //   externally.
  //---------------------------------------------------------------------------
  this.periodicUpdate = function()
  {
    // Use a semaphore to prevent a stack-up of multiple instances.  Could
    // happen if there are long network delays.
    if ( ( 0 == periodicUpdateSemaphore )
      && ( Object.keys( periodicQuery ).length > 0 ) )
    {
      periodicUpdateSemaphore += 1

      // Make the request to the remote server.
      $.post
      (
        "",
        periodicQuery
      )
      .error
      (
        // Callback if there has been an error in retrieving the data.
        function()
        {
          if ( ! isInError )
          {
            // Run all the remote callbacks with no data to signal an error.
            for ( var index in periodicCallbacks )
            {
              var remoteCallback = periodicCallbacks[ index ]
              remoteCallback[ 1 ]( null )
            }

            // All data is invalid and must be refreshed.
            periodicHistory = {}

            // Enable blinking.
            $( '.error' ).blink( { delay: 500 } )

            // Save the state of each button, input, and select, then disable
            // them.
            buttonEnables = {}
            $( "main button, main input, main select" )
              .each
              (
                function()
                {
                  buttonEnables[ this.id ] = $( this ).prop( "disabled" )
                  $( this ).prop( "disabled", true )
                }
              )

            // Run error callbacks.
            for ( var index in onErrorCallbacks )
              onErrorCallbacks[ index ]()
          }

          // Now in an error state.
          isInError = true

          periodicUpdateSemaphore -= 1
        }
      )
      .done
      (
        // Callback when data arrives.
        function( data )
        {
          if ( isInError )
          {
            // Restore operational status of buttons, inputs, and selects.
            $( "main button, main input, main select" )
              .each
              (
                function()
                {
                  $( this ).prop( "disabled", buttonEnables[ this.id ]  )
                }
              )

            // Run error-clear callbacks.
            for ( var index in onErrorClearCallbacks )
              onErrorClearCallbacks[ index ]()

          }

          // Data arrived, thus not in an error state.
          isInError = false

          // Get XML data.
          var xml = $( data )

          // For each of the data results...
          // Results are all children of <ResultData>.
          xml.find( 'ResultData' )
            .first()
            .children()
            .each
            (
              function()
              {
                // Extract the result of this command.
                var valueString = $( this ).text()

                valueString = jQuery.parseJSON( valueString )

                // Extract the ID of the result.
                var id = this.tagName

                // Has the value changed?
                if ( periodicHistory[ id ] != valueString )
                {

                  // Fetch the callback function associated with the ID.
                  callbackFunction = periodicCallbackTable[ id ]

                  // Send the retrieved data to the callback.
                  callbackFunction( valueString )

                  // Save the current data.
                  periodicHistory[ id ] = valueString
                }

              } // each callback function

            ) // each

          // Run end of period update callbacks.
          for ( var index in onPeriodicEndCallbacks )
            onPeriodicEndCallbacks[ index ]()

          // Release semaphore.
          periodicUpdateSemaphore -= 1
        }
      )

    }

    // Setup to run this function again.  (i.e. make it periodic.)
    // NOTE: This needs to happen even if the function was skipped due to
    // the semaphore being in use.
    if ( ! self.periodicShutdown )
      setTimeout( self.periodicUpdate, updateRate )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a remote query and a callback function to be sent new data to the
  //   list of periodically updated queries.
  // Input:
  //   query - Remote query to execute that returns the desired data.
  //   callback - Function to be sent the data when data changes.
  // Notes:
  //   The callback function receives one parameter containing the new data.
  //   Callbacks are not run if the data has not changed.
  //---------------------------------------------------------------------------
  this.addPeriodicCallback = function( query, callback )
  {
    periodicCallbacks.push( [ query, callback ] )

    // Build a remote query table, and a callback table.  The query table
    // associates an ID with a remote command needing to be issued.  The
    // callback table associates the ID with the callback function to run
    // if the data changes.
    var values = ""
    var index = 0
    periodicCallbackTable = {}
    periodicQuery = {}
    for ( var index in periodicCallbacks )
    {
      var remoteCallback = periodicCallbacks[ index ]
      // Make an ID for this callback.
      var id = "id" + index
      periodicCallbackTable[ id ] = remoteCallback[ 1 ]
      periodicQuery[ id ] = remoteCallback[ 0 ]
      index += 1
    }

  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a remote query that is periodically updated and displayed in a tag.
  // Input:
  //   query - Remote query to execute that returns the desired data.
  //   displayId - The id of the tag the data is displayed.
  //   variableMap - Dictionary to place value of item. (Optional)
  //   variableIndex - Input in dictionary to place value of item. (Optional)
  //   formatFunction - Optional function to format data before displaying.
  //   formatParameters - Optional parameters passed to format function.
  //---------------------------------------------------------------------------
  this.addPeriodicDisplay = function
  (
    query,
    displayId,
    variableMap,
    variableIndex,
    formatFunction,
    formatParameters
  )
  {
    // Add a periodic callback with the callback being specified.
    self.addPeriodicCallback
    (
      query,
      function( value )
      {
        self.displayCallback
        (
          value,
          displayId,
          variableMap,
          variableIndex,
          formatFunction,
          formatParameters
        )
      }
    )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a periodic query whose value is saved in a dictionary.
  // Input:
  //   query - Remote query to execute that returns the desired data.
  //   variableMap - Dictionary to place value of item.
  //   variableIndex - Input in dictionary to place value of item.
  //   callback - Optional function to to call wiht data. (Optional)
  //   callbackParameters - Optional parameters passed to callback function.
  //                        (Optional)
  // Notes:
  //   Callback gets two parameters: value read, followed by callback
  //   parameters.
  //---------------------------------------------------------------------------
  this.addPeriodicRead = function
  (
    query,
    variableMap,
    variableIndex,
    callback,
    callbackParameters
  )
  {
    // Add a periodic callback with the callback being specified.
    self.addPeriodicCallback
    (
      query,
      function( value )
      {
        // Save value.
        variableMap[ variableIndex ] = value

        // Run callback if requested.
        if ( callback )
          callback( value, callbackParameters )
      }
    )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Execute a remote action.
  // Input:
  //   actionQuery - The action to execute on remote server.
  //   callback - A callback to run with the results of this query.  Optional.
  // Notes:
  //   Remote actions are a query (presumably a Python command) whose results
  //   are returned as a JSON object.  This JSON object is unpacked and that
  //   unpacked result sent to the callback.
  //---------------------------------------------------------------------------
  this.remoteAction = function( actionQuery, callback )
  {
    // Run the query.
    $.post
    (
      "",
      {
        action : actionQuery
      }
    )
    .error
    (
      function()
      {
        if ( callback )
          callback( null )
      }
    )
    .done
    (
      function( data )
      {
        // If there is a callback, send it the results.
        if ( callback )
        {
          var xml = $( data )
          var value = xml.find( "action" ).text()

          value = jQuery.parseJSON( value )

          if ( callback )
            callback( value )
        }
      }
    )
  }


  //---------------------------------------------------------------------------
  // Uses:
  //   Function that is called to display a value in a tag.
  // Input:
  //   value - Value to display.
  //   displayId - Tag on screen to display item.
  //   variableMap - Dictionary to place value of item. (Optional)
  //   variableIndex - Input in dictionary to place value of item. (Optional)
  //   formatFunction - Function to format the data before being displayed. (Optional)
  //   formatParameters - Parameter to pass to the format function. (Optional)
  // Example:
  //   var savedValue = {}
  //   winderInterface.displayCallback
  //   (
  //     1234,
  //     "#tag",
  //     savedValue,
  //     "name",
  //     function( value )
  //     {
  //       return Math.round( value )
  //     }
  //   )
  //---------------------------------------------------------------------------
  this.displayCallback = function
  (
    value,
    displayId,
    variableMap,
    variableIndex,
    formatFunction,
    formatParameters
  )
  {
    // If this value needs to be saved...
    if ( ( variableMap )
      && ( variableIndex ) )
        variableMap[ variableIndex ] = value

    // If the value needs to be formatted...
    if ( formatFunction )
      value = formatFunction( value, formatParameters )

    // Display value.
    $( displayId ).text( value )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Load an item from remote server and display it in a given tag.
  // Input:
  //   query - Query to be made of remote server.
  //   displayId - Tag on screen to display item.
  //   variableMap - Dictionary to place value of item. (Optional)
  //   variableIndex - Input in dictionary to place value of item. (Optional)
  //   formatFunction - Function to format the data before being displayed. (Optional)
  //   formatParameters - Parameter to pass to the format function. (Optional)
  //---------------------------------------------------------------------------
  this.singleRemoteDisplay = function
  (
    query,
    displayId,
    variableMap,
    variableIndex,
    formatFunction,
    formatParameters
  )
  {
    self.remoteAction
    (
      query,
      function( value )
      {
        self.displayCallback
        (
          value,
          displayId,
          variableMap,
          variableIndex,
          formatFunction,
          formatParameters
        )
      }
    )
  }

  //---------------------------------------------------------------------------
  // Input:
  //   fileName - Path and name of XML file from remote server.
  //   xmlFiled - The specific XML tag that has the data to be displayed.
  //   displayId - Tag on screen to display item.
  //   variableMap - Dictionary to place value of item. (Optional)
  //   variableIndex - Input in dictionary to place value of item. (Optional)
  //   formatFunction - Function to format the data before being displayed. (Optional)
  //   formatParameters - Parameter to pass to the format function. (Optional)
  //---------------------------------------------------------------------------
  this.readXML_Display = function
  (
    fileName,
    xmlFiled,
    displayId,
    variableMap,
    variableIndex,
    formatFunction,
    formatParameters
  )
  {
    // Run the query.
    $.get( fileName )
      .done
      (
        function( data )
        {
          var xml = $( data )
          var value = xml.find( xmlFiled ).text()

          self.displayCallback
          (
            value,
            displayId,
            variableMap,
            variableIndex,
            formatFunction,
            formatParameters
          )
        }
      )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Turn a button into a true/false toggle button.
  // Input:
  //   tagId - Id of <button> to modify.
  //   getQuery - Query to get the initial status of button.  Can be undefined.
  //   setQuery - Query to set state of button.  Use "$" to denote where value
  //     is placed.
  //   getCallback - Optional callback after updating value.
  //   setCallback - Optional callback after change.
  // Returns:
  //   Function that can be called to manually update the buttons using the
  //   get query.  Function is moot if no get query is specified.
  //---------------------------------------------------------------------------
  this.addToggleButton = function( tagId, getQuery, setQuery, getCallback, setCallback )
  {
    // Save the enable/disabled state of the button in case we modify it latter.
    toggleButtonStates[ tagId ] = $( tagId ).prop( "disabled" )

    // Function that sets the state of button with data being true or false.
    var updateFunction =
      function( data )
      {
        $( tagId ).prop( "disabled", toggleButtonStates[ tagId ] )
        toggleButtonStates[ tagId ] = null

        value = ( data === true ) || ( data == "1" )
        className = "toggle"
        if ( value )
          className = "toggleDown"

        $( tagId ).attr( 'class', className )

        var value = 0
        if ( $( this ).attr( 'class' ) == "toggleDown" )
          value = 1

        $( tagId ).val( value )

        if ( getCallback )
          getCallback( data )
      }

    // If there is a function that can query the current state of button...
    if ( getQuery )
    {
      // Disable button until we know what state (on/off) it should be in.
      $( tagId ).prop( "disabled", true )

      // Function to get the current state of button.
      queryFunction = function()
      {
        // Get the initial value.
        self.remoteAction( getQuery, updateFunction )
      }

      // Run the query now.
      queryFunction()

      // Also query the state of the button anytime we go from an error
      // state to working.
      self.addErrorClearCallback( queryFunction )
    }

    // Disable the button if there is a loss of communication to server.
    self.addErrorCallback
    (
      function()
      {
        if ( null !== toggleButtonStates[ tagId ] )
        {
          toggleButtonStates[ tagId ] = $( tagId ).prop( "disabled" )
          $( tagId ).attr( 'class', "" )
          $( tagId ).prop( "disabled", true )
        }
      }
    )

    // Callback when button is clicked.
    $( tagId )
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

          // If there is a set query to run...
          if ( null != setQuery )
          {
            // Construct query.
            query = setQuery.replace( "$", value )
            self.remoteAction
            (
              query,
              function( value )
              {
                // Call the update function (make sure the transition took place).
                updateFunction( value )

                // Run additional callback.
                if ( setCallback )
                  setCallback ( value )
              }
            )
          }
          else
          if ( setCallback )
            setCallback( value )
        }
      )

    // Return the update function.
    return updateFunction
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a callback to be run when there is an error reading data from the
  //   server.  Typically used to disable the interface.
  // Input:
  //   callback - Function to run.
  //---------------------------------------------------------------------------
  this.addErrorCallback = function( callback )
  {
    onErrorCallbacks.push( callback )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a callback to be run after an error state has cleared.  Typically
  //   used to re-enable/re-load interface.
  // Input:
  //   callback - Function to run.
  //---------------------------------------------------------------------------
  this.addErrorClearCallback = function( callback )
  {
    onErrorClearCallbacks.push( callback )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a callback to be run after all periodic variables have been updated.
  // Input:
  //   callback - Function to run.
  //---------------------------------------------------------------------------
  this.addPeriodicEndCallback = function( callback )
  {
    onPeriodicEndCallbacks.push( callback )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Add a callback to be run after the entire pages has finished loading.
  // Input:
  //   callback - Function to run.
  //---------------------------------------------------------------------------
  this.addFullyLoadedCallback = function( callback )
  {
    onFullyLoadedCallbacks.push( callback )
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Allows periodic updates to be inhibited.
  // Input:
  //   isInhibit - True to inhibit, false to uninhibit.
  // Notes:
  //   This inhibit is incremental.  It must be called with isInhibit set to
  //   false as many times as set to true in order to enable updates.
  //---------------------------------------------------------------------------
  this.inhibitUpdates = function( isInhibit )
  {
    if ( isInhibit )
      periodicUpdateSemaphore += 1
    else
      periodicUpdateSemaphore -= 1
  }

  //---------------------------------------------------------------------------
  // Uses:
  //   Shutdown periodic update function.  Call when internals of page are to
  // be reloaded.
  //---------------------------------------------------------------------------
  this.shutdown = function()
  {
    this.periodicShutdown = true
  }

}
