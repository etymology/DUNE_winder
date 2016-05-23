function overlayClose()
{
  $( "#overlayBackground" )
    .animate
    (
      {
        width: "0",
        height: "0",
        opacity: 0
      },
      {
        complete: function()
        {
          $( "#overlayBackground" ).parent().text( "" )
        }
      }
    )
}

$( document ).ready
(
  function()
  {
    $( "#overlayBackground" )
      .css
      (
        {
          opacity: 0
        }
      )
      .animate
      (
        {
          width: "100%",
          height: "100%",
          opacity: 1
        }
      )
  }
)
