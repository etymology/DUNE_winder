winder.addPeriodicRemoteDisplay( "io.xAxis.isSeeking()", "#xMoving" );
winder.addPeriodicRemoteDisplay( "round( io.xAxis.getDesiredPosition(), 1 ) + 0", "#xDesiredPosition" );
winder.addPeriodicRemoteDisplay( "round( io.xAxis.getPosition(), 1 ) + 0",        "#xPosition" );
winder.addPeriodicRemoteDisplay( "round( io.xAxis.getVelocity(), 2 ) + 0",        "#xVelocity" );
winder.addPeriodicRemoteDisplay( "round( io.xAxis.getAcceleration(), 2 ) + 0",    "#xAcceleration" );

winder.addPeriodicRemoteDisplay( "io.yAxis.isSeeking()", "#yMoving" )
winder.addPeriodicRemoteDisplay( "round( io.yAxis.getDesiredPosition(), 1 ) + 0", "#yDesiredPosition" );
winder.addPeriodicRemoteDisplay( "round( io.yAxis.getPosition(), 1 ) + 0",        "#yPosition" );
winder.addPeriodicRemoteDisplay( "round( io.yAxis.getVelocity(), 2 ) + 0",        "#yVelocity" );
winder.addPeriodicRemoteDisplay( "round( io.yAxis.getAcceleration(), 2 ) + 0",    "#yAcceleration" );

winder.addPeriodicRemoteDisplay( "io.zAxis.isSeeking()", "#zMoving" )
winder.addPeriodicRemoteDisplay( "round( io.zAxis.getDesiredPosition(), 1 ) + 0", "#zDesiredPosition" );
winder.addPeriodicRemoteDisplay( "round( io.zAxis.getPosition(), 1 ) + 0",        "#zPosition" );
winder.addPeriodicRemoteDisplay( "round( io.zAxis.getVelocity(), 2 ) + 0",        "#zVelocity" );
winder.addPeriodicRemoteDisplay( "round( io.zAxis.getAcceleration(), 2 ) + 0",    "#zAcceleration" );
