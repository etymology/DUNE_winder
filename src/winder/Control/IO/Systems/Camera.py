###############################################################################
# Name: Camera.py
# Uses: Interface to vision system.
# Date: 2016-12-16
# Author(s):
#   Andrew Que <aque@bb7.com>
# NOTES:
#   Uses Cognex camera and custom PLC trigger/capture setup.  The PLC provides
# two interfaces for using the camera.  The first is a method to setup camera
# triggering at regular intervals in X/Y.  The second is a FIFO that
# accumulates capture data.  These two systems must be implemented in the PLC
# for maximum speed.
###############################################################################
from IO.Devices.PLC import PLC

class Camera:

  #---------------------------------------------------------------------
  def __init__( self, plc ) :
    """
    Constructor.

    Args:
      plcLogic: Instance of PLC_Logic.
    """

    self.cameraTrigger        = PLC.Tag( plc, "Cam_F_Trigger", tagType="BOOL" )
    #self.cameraTriggerEnable  = PLC.Tag( plc, "Cam_F:O.Control.TriggerEnable", tagType="BOOL" )
    self.cameraTriggerEnable  = PLC.Tag( plc, "Cam_F_En", tagType="BOOL" )

    self.cameraFIFO_MotorX     = PLC.Tag( plc, "FIFO_Data[0]", tagType="REAL" )
    self.cameraFIFO_MotorY     = PLC.Tag( plc, "FIFO_Data[1]", tagType="REAL" )
    self.cameraFIFO_Status     = PLC.Tag( plc, "FIFO_Data[2]", tagType="REAL" )
    self.cameraFIFO_MatchLevel = PLC.Tag( plc, "FIFO_Data[3]", tagType="REAL" )
    self.cameraFIFO_CameraX    = PLC.Tag( plc, "FIFO_Data[4]", tagType="REAL" )
    self.cameraFIFO_CameraY    = PLC.Tag( plc, "FIFO_Data[5]", tagType="REAL" )

    self.cameraFIFO_Clock      = PLC.Tag( plc, "READ_FIFOS", tagType="BOOL" )

    self.cameraDeltaEnable     = PLC.Tag( plc, "EN_POS_TRIGGERS", tagType="BOOL" )
    self.cameraX_Delta         = PLC.Tag( plc, "X_DELTA", tagType="REAL" )
    self.cameraY_Delta         = PLC.Tag( plc, "Y_DELTA", tagType="REAL" )

    # EN_POS_TRIGGER - Enable camera position trigger. BOOL
    # X_DELTA - Offset to trigger REAL
    # Y_DELTA - Offset to trigger REAL

    # $$$DEBUG - Old.  Probably not needed.
    attributes = PLC.Tag.Attributes()
    attributes.isPolled = True
    self.cameraResultStatus = PLC.Tag( plc, "Cam_F:I.InspectionResults[0]", attributes, tagType="REAL" )
    self.cameraResultScore  = PLC.Tag( plc, "Cam_F:I.InspectionResults[1]", attributes, tagType="REAL" )
    self.cameraResultX      = PLC.Tag( plc, "Cam_F:I.InspectionResults[2]", attributes, tagType="REAL" )
    self.cameraResultY      = PLC.Tag( plc, "Cam_F:I.InspectionResults[3]", attributes, tagType="REAL" )

    self.captureFIFO = []

    # $$$DEBUG - Remove
    self.captureFIFO.append(
      {
        "MotorX"     : 1,
        "MotorY"     : 2,
        "Status"     : 1,
        "MatchLevel" : .95,
        "CameraX"    : 100,
        "CameraY"    : 200
      }
    )

    self.captureFIFO.append(
      {
        "MotorX"     : 3,
        "MotorY"     : 4,
        "Status"     : 1,
        "MatchLevel" : .95,
        "CameraX"    : 400,
        "CameraY"    : 500
      }
    )

    self._callback = None

  #---------------------------------------------------------------------
  def setCallback( self, callback ) :
    """
    Set a callback to run during enable/disabling of triggering.

    Args:
      callback: The callback to run.

    Notes:
      Callback is passed a single parameter, True if trigger was being enabled,
      False if trigger is being disabled.
    """

    self._callback = callback

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update FIFO registers.
    Call periodically after a trigger has been setup.

    Returns:
      True if there was data in the FIFO, False if FIFO was empty.
    """

    # Clock FIFO.
    self.cameraFIFO_Clock.set( 1 )

    # Any data in FIFO?
    isData = self.cameraFIFO_MotorX.poll()

    #print self.cameraFIFO_MotorX.get()

    if self.cameraFIFO_MotorX.get() > 0 :

      print "Got data"

      # Update remaining FIFO values.
      # $$$FUTURE - Do a block read.
      self.cameraFIFO_MotorY.poll()
      self.cameraFIFO_Status.poll()
      self.cameraFIFO_MatchLevel.poll()
      self.cameraFIFO_CameraX.poll()
      self.cameraFIFO_CameraY.poll()

      # Place all FIFO values in capture FIFO.
      self.captureFIFO.append(
        {
          "MotorX"     : self.cameraFIFO_MotorX.get(),
          "MotorY"     : self.cameraFIFO_MotorY.get(),
          "Status"     : self.cameraFIFO_Status.get(),
          "MatchLevel" : self.cameraFIFO_MatchLevel.get(),
          "CameraX"    : self.cameraFIFO_CameraX.get(),
          "CameraY"    : self.cameraFIFO_CameraY.get()
        }
      )

    return isData

  #---------------------------------------------------------------------
  def reset( self ) :
    """$$$DEBUG"""
    self.captureFIFO = []
    self.cameraDeltaEnable.set( 0 )
    self.cameraTriggerEnable.set( 0 )

  #---------------------------------------------------------------------
  def startScan( self, deltaX, deltaY ) :
    """
    Begin a pin scan.
    Call stopped before any motion begins.

    Args:
      deltaX: Distance in X to trigger camera.
      deltaY: Distance in Y to trigger camera.

    Notes:
      Typically either deltaX or deltaY is 0 with one one delta being used
      for a scan.  Deltas account for direction by being positive or negative.
    """

    # Flush capture FIFO.
    self.captureFIFO = []

    #self.cameraDeltaEnable.set( 0 )
    self.cameraTriggerEnable.set( 1 )
    self.cameraX_Delta.set( deltaX )
    self.cameraY_Delta.set( deltaY )
    self.cameraDeltaEnable.set( 1 )

    if self._callback :
      self._callback( True )

  #---------------------------------------------------------------------
  def endScan( self ) :
    """
    Finish a pin scan.
    Disables PLC camera trigger logic.
    """
    self.cameraDeltaEnable.set( 0 )
    self.cameraTriggerEnable.set( 0 )

    # $$$DEBUG - Temporary.
    with open( "cameraDump.txt", 'a' ) as outputFile :
      for row in self.captureFIFO :
        for key in row :
          outputFile.write( str( row[ key ] ) + "," )

        outputFile.write( "\n" )

      outputFile.write( "\n\n" )

    if self._callback :
      self._callback( False )
