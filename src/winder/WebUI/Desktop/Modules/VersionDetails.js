function VersionDetails( modules )
{
  var winder = modules.get( "Winder" )

  this.versionUpdate = function()
  {
    winder.singleRemoteDisplay( "version.getVersion()", "#controlVersionString" )
    winder.singleRemoteDisplay( "version.getHash()", "#controlVersionHash" )
    winder.singleRemoteDisplay( "version.getDate()", "#controlVersionDate" )
    winder.singleRemoteDisplay( "version.verify()", "#controlVersionValid" )

    winder.singleRemoteDisplay( "uiVersion.getVersion()", "#uiVersionString" )
    winder.singleRemoteDisplay( "uiVersion.getHash()", "#uiVersionHash" )
    winder.singleRemoteDisplay( "uiVersion.getDate()", "#uiVersionDate" )
    winder.singleRemoteDisplay( "uiVersion.verify()", "#uiVersionValid" )
  }

  this.versionUI_Recompute = function()
  {
    winder.remoteAction( "uiVersion.update()", this.versionUpdate )
  }

  this.versionControlRecompute = function()
  {
    winder.remoteAction( "version.update()", this.versionUpdate )
  }

  this.close = function ()
  {
    var version = modules.get( "Version" )
    version.loadVersion()

    var overlay = modules.get( "Overlay" )
    overlay.close()
  }

  //this.versionUpdate()
  window[ "versionDetails" ] = this
}
