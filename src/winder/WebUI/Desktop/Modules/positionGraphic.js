function PositionGraphic()
{
  var self = this

  this.initialize = function()
  {
    // Image position
    winder.addPeriodicEndCallback
    (
      function()
      {
        // Limits of image (in pixels)
        var minX = 52
        var maxX = 1040

        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var minPosition = -250
        var maxPosition = 6800

        var x = maxX - minX
        x *= motorStatus.motor[ "xPosition" ] - minPosition
        x /= ( maxPosition - minPosition )
        x += minX

        $( "#loopImage" ).css( "left", x + "px" )
        //$( "#debug" ).text( x )
      }
    )
  }
}

var positionGraphic = new PositionGraphic()
