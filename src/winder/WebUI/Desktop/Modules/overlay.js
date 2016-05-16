$( "#overlayBackground" ).click
(
  function()
  {
    // Self-destruct.
    $( "#overlayBackground" ).parent().text( "" )
  }
)

$( '#overlayBox' ).click
(
  function( event )
  {
    event.stopPropagation()
  }
)