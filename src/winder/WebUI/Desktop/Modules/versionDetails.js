function versionUpdate()
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

function versionUI_Recompute()
{
  winder.remoteAction( "uiVersion.update()", versionUpdate )
}

function versionControlRecompute()
{
  winder.remoteAction( "version.update()", versionUpdate )
}

versionUpdate()