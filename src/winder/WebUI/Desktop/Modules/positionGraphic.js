function PositionGraphic()
{
  var self = this

  // Scale factor for all images.
  var SCALE = 0.7

  //-----------------------------------------------------------------------------
  // Uses:
  //   Setup periodic callback that will reposition images.  Don't call until
  //   page is fully loaded.
  //-----------------------------------------------------------------------------
  this.initialize = function()
  {
    // Image position
    winder.addPeriodicEndCallback
    (
      function()
      {
        // Limits of image (in pixels)
        var MIN_X = 58 * SCALE    //52
        var MAX_X = 1110 * SCALE

        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var MIN_X_POSITION = -250
        var MAX_X_POSITION = 6800

        var x = MAX_X - MIN_X
        x *= motorStatus.motor[ "xPosition" ] - MIN_X_POSITION
        x /= ( MAX_X_POSITION - MIN_X_POSITION )
        x += MIN_X

        $( "#loopImage" )
          .css( "left", x + "px" )

        var HEAD_X_OFFSET = 100 * SCALE

        // Limits of image (in pixels)
        var MIN_Y = 387 * SCALE
        var MAX_Y = 28 * SCALE

        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var MIN_Y_POSITION = -25
        var MAX_Y_POSITION = 2800

        x += HEAD_X_OFFSET

        var y = MAX_Y - MIN_Y
        y *= motorStatus.motor[ "yPosition" ] - MIN_Y_POSITION
        y /= ( MAX_Y_POSITION - MIN_Y_POSITION )
        y += MIN_Y

        $( "#headImage" )
          .css( "left", x + "px" )
          .css( "top", y + "px" )

        // Limits of image (in pixels)
        var MIN_HEAD_Z = 783 * SCALE
        var MAX_HEAD_Z = 1064 * SCALE

        // Limits of travel (in mm)
        // $$$DEBUG - This should come from machine geometry.
        var MIN_Z_POSITION = 0
        var MAX_Z_POSITION = 435

        var z = MAX_HEAD_Z - MIN_HEAD_Z
        z *= motorStatus.motor[ "zPosition" ] - MIN_Z_POSITION
        z /= ( MAX_Z_POSITION - MIN_Z_POSITION )
        z += MIN_HEAD_Z

        if ( 1 == motorStatus.motor[ "headSide" ] )
          z = MAX_HEAD_Z

        $( "#zHeadImage" )
          .css( "left", z + "px" )

        // Limits of image (in pixels)
        var MIN_HEAD_Z = 0 * SCALE
        var MAX_HEAD_Z = 281 * SCALE

        var z = MAX_HEAD_Z - MIN_HEAD_Z
        z *= motorStatus.motor[ "zPosition" ] - MIN_Z_POSITION
        z /= ( MAX_Z_POSITION - MIN_Z_POSITION )
        z += MIN_HEAD_Z

        $( "#zArmImage" )
          .css( "left", z + "px" )

        // zHeadPosition = $( "#zArmImage" ).position()
        // $( "#debug" ).html
        // (
        //   zHeadPosition.left + ", " + zHeadPosition.top
        // )
      }
    )
  }

  //-----------------------------------------------------------------------------
  // Uses:
  //   Setup images to use scale factor.
  //-----------------------------------------------------------------------------
  var rescale = function()
  {
    var width = $( this ).width() * SCALE
    $( this ).width( width )
    $( this ).css( "display", "inline" )

    var ITEMS = [ "margin-left", "margin-top", "top" ]
    for ( index in ITEMS )
    {
      var item = ITEMS[ index ]

      var newSize = $( this ).css( item )
      var raw = newSize
      if ( newSize )
      {
        newSize  = newSize.replace( "px", "" )
        if ( $.isNumeric( newSize ) )
        {
          newSize  = parseFloat( newSize )
          newSize *= SCALE

          $( this ).css( item, newSize )
          console.log( $( this ).attr( "id" ) + " " + raw + " " + item + " " + newSize )
        }
      }
    }
  }

  //
  // Load all images.
  //

  $( "<img />" )
    .attr( "src", "Images/Base.png" )
    .attr( "id", "baseImage" )
    .attr( "alt", "Front view" )
    .load( rescale )
    .appendTo( "#sideGraphic" )

  $( "<img />" )
    .attr( "src", "Images/Loop.png" )
    .attr( "id", "loopImage" )
    .attr( "alt", "Loop view" )
    .load( rescale )
    .appendTo( "#sideGraphic" )

  $( "<img />" )
    .attr( "src", "Images/Head.png" )
    .attr( "id", "headImage" )
    .attr( "alt", "Head view" )
    .load( rescale )
    .appendTo( "#sideGraphic" )

  $( "<img />" )
    .attr( "src", "Images/Z_Base.png" )
    .attr( "id", "zBaseImage" )
    .attr( "alt", "Z-Base view" )
    .load( rescale )
    .appendTo( "#zGraphic" )

  $( "<img />" )
    .attr( "src", "Images/Z_Head.png" )
    .attr( "id", "zHeadImage" )
    .attr( "alt", "Z-Head view" )
    .load( rescale )
    .appendTo( "#zGraphic" )

  $( "<img />" )
    .attr( "src", "Images/Z_Arm.png" )
    .attr( "id", "zArmImage" )
    .attr( "alt", "Z-Arm view" )
    .load( rescale )
    .appendTo( "#zGraphic" )

}

var positionGraphic = new PositionGraphic()
