function FullStop( modules )
{
  var self = this;
  var winder;

  try {
      modules.load(["../../Scripts/Winder", "/Desktop/Modules/RunStatus"], function() {
          winder = modules.get("Winder");
          var runStatus = modules.get("RunStatus");

          // Button enable.
          winder.addPeriodicEndCallback(function() {
              var isDisabled = !runStatus.isInMotion();
              $("#fullStopButton").prop("disabled", isDisabled);
          });
      });
  } catch (error) {
      console.error("Error loading modules:", error);
      // Handle the error as needed
  }
  

  //-----------------------------------------------------------------------------
  // Uses:
  //   Callback for global stop button.
  //-----------------------------------------------------------------------------
  this.stop = function ()
  {
    winder.remoteAction( 'process.stop()' )
  }

  window[ "fullStop" ] = this
}
