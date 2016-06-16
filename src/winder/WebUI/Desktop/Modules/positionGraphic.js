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
        var MIN_X = 58    //52
        var MAX_X = 1110

        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var MIN_X_POSITION = -250
        var MAX_X_POSITION = 6800

        var x = MAX_X - MIN_X
        x *= motorStatus.motor[ "xPosition" ] - MIN_X_POSITION
        x /= ( MAX_X_POSITION - MIN_X_POSITION )
        x += MIN_X

        $( "#loopImage" ).css( "left", x + "px" )
        //$( "#debug" ).text( x )

        var HEAD_X_OFFSET = 100

        // Limits of image (in pixels)
        var MIN_Y = 387
        var MAX_Y = 28

        // Limits of travel (in mm)
        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var MIN_Y_POSITION = -25
        var MAX_Y_POSITION = 2800

        x += HEAD_X_OFFSET

        var y = MAX_Y - MIN_Y
        y *= motorStatus.motor[ "yPosition" ] - MIN_Y_POSITION
        y /= ( MAX_Y_POSITION - MIN_Y_POSITION )
        y += MIN_Y

        $( "#headImage" ).css( "left", x + "px" )
        $( "#headImage" ).css( "top", y + "px" )
        // var loopPosition = $( "#loopImage" ).position()
        // var headPosition = $( "#headImage" ).position()
        // $( "#debug" ).html
        // (
        //   loopPosition.left + ", " + loopPosition.top + "<br />" + headPosition.left + ", " + headPosition.top
        // )
      }
    )
  }

  $( "#headImage" ).draggable()

}

var positionGraphic = new PositionGraphic()
