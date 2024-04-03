###############################################################################
# Name: AnodePlaneArray.py
# Uses: Anode Plane Array (APA) management.
# Date: 2016-03-01
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import

from Library.Recipe import Recipe

from Machine.Settings import Settings
from Machine.LayerCalibration import LayerCalibration

from .APA_Base import APA_Base


class AnodePlaneArray(APA_Base):

    # There can only be a single working instance of an APA, and it must be
    # saved before loading or starting a new one.
    activeAPA = None

    # ---------------------------------------------------------------------
    def __init__(
        self,
        gCodeHandler,
        apaDirectory,
        recipeDirectory,
        recipeArchiveDirectory,
        name,
        log,
        systemTime,
        createNew=False
    ):
        """
        Constructor.

        Args:
          gCodeHandler: Instance of G_CodeHandler.
          apaDirectory: Directory APA data is stored.
          recipeDirectory: Directory recipes are stored.
          recipeArchiveDirectory: Directory recipes are archived.
          name: Name/serial number of APA.
          log: Instance of system log file.
          systemTime: Instance of TimeSource.
          createNew: True if this APA should be created should it not already exist.
        """

        APA_Base.__init__(self, apaDirectory, name, systemTime)

        # If there was an APA previously active, save it.
        if AnodePlaneArray.activeAPA:
            AnodePlaneArray.activeAPA.close()

        AnodePlaneArray.activeAPA = self

        self._recipeDirectory = recipeDirectory
        self._recipeArchiveDirectory = recipeArchiveDirectory
        self._log = log
        self._gCodeHandler = gCodeHandler
        self._systemTime = systemTime
        self._startTime = systemTime.get()

        # Uninitialized data.
        self._recipe = None
        self._calibration = None

        self._log.attach(self.getPath() + AnodePlaneArray.LOG_FILE)

        if createNew:
            self.save()
        else:
            self.load()

    # ---------------------------------------------------------------------
    def _getG_CodeLogName(self, layer):
        """
        Get the name of the G-Code log for this layer.

        Args:
          layer: Name of the layer.
        """
        return f"{self.getPath()}/Layer{layer}{Settings.G_CODE_LOG_FILE}"

    # ---------------------------------------------------------------------
    def closeLoadedRecipe(self):
        """
        Close the open recipe and reset internals to blank APA.
        """
        if self._calibrationFile:
            self._calibrationFile = None
            self._calibration = None
            self._gCodeHandler.useLayerCalibration(None)

        if self._recipeFile:
            self._recipeFile = None
            self._gCodeHandler.closeG_Code()

        self._layer = None
        self._lineNumber = None

    # ---------------------------------------------------------------------
    def loadRecipe(self, layer=None, recipeFile=None, startingLine=None):
        """
        Load a recipe file into G_CodeHandler.

        Args:
          layer: The current working layer.
          recipeFile: File name of recipe to load.
          startingLine: What line to start from in recipe.

        Returns:
          True if there was an error, False if not.
        """
        if layer != None:
            self._layer = layer

        isError = False
        # If there is a calibration file, load it.
        if self._calibrationFile:
            archivePath = f"{self.getPath()}/Calibration"
            self._calibration = LayerCalibration(archivePath=archivePath)

            try:
                self._calibration.load(self.getPath(), self._calibrationFile)
            except LayerCalibration.Error as exception:

                errorString = f"Invalid calibration hash for {self._calibrationFile} because {str(exception)}."

                errorData = [self._calibrationFile] + exception.data

                self._log.add(
                    self.__class__.__name__,
                    "LOAD",
                    f"{errorString}  Rehashing.",
                    errorData,
                )

                try:
                    self._calibration.load(
                        self.getPath(), self._calibrationFile, exceptionForMismatch=False)
                    self._calibration.save()
                except LayerCalibration.Error as exception:
                    error = "Invalid calibration file."
                    isError = True

                    self._gCodeHandler.useLayerCalibration(None)

                    self._log.add(
                        self.__class__.__name__,
                        "LOAD",
                        f"{errorString}  Aborting.",
                        errorData,
                    )

            self._log.add(
                self.__class__.__name__,
                "LOAD",
                f"Loaded calibration file {self._calibrationFile}.",
                [self._calibrationFile, self._calibration.hashValue],
            )

            # Make use of calibration.
            self._gCodeHandler.useLayerCalibration(self._calibration)

        else:
            # If there is no calibration, use none.
            self._gCodeHandler.useLayerCalibration(None)

        if recipeFile != None:
            self._recipeFile = recipeFile

        if startingLine != None:
            self._lineNumber = startingLine

        if not isError:
            self._recipe = Recipe(
                f"{self._recipeDirectory}/{self._recipeFile}",
                self._recipeArchiveDirectory,
            )
            self._gCodeHandler.loadG_Code(
                self._recipe.getLines(), self._calibration)

            # Assign a G-Code log.
            gCodeLogName = self._getG_CodeLogName(self._layer)
            self._gCodeHandler.setG_CodeLog(gCodeLogName)

        if not isError:
            isError |= self._gCodeHandler.setLine(self._lineNumber)
            if isError:
                error = "Invalid line number."

        if not isError:
            self._log.add(
                self.__class__.__name__,
                "GCODE",
                f"Loaded G-Code file {self._recipeFile}, active layer {self._layer}, starting at line {str(self._lineNumber)}",
                [
                    self._recipeFile,
                    self._layer,
                    self._lineNumber,
                    self._recipe.getDescription(),
                    self._recipe.getID(),
                ],
            )
        else:
            self._log.add(
                self.__class__.__name__,
                "GCODE",
                f"Failed to loaded G-Code file {self._recipeFile}, starting at line {str(self._lineNumber)}",
                [error, self._recipeFile, self._lineNumber],
            )

        return isError

    # ---------------------------------------------------------------------
    def load(self):
        """
        Load

        Returns:
          True if there was an error, False if not.
        """

        # Log message about AHA change.
        self._log.add(
            self.__class__.__name__,
            "LOAD",
            f"Loaded APA called {self._name}",
            [self._name],
        )

        APA_Base.load(self)

        if self._recipeFile:
            self.loadRecipe(self._layer)
            self._gCodeHandler.setInitialLocation(
                self._x, self._y, self._headLocation)

    # ---------------------------------------------------------------------
    def getCalibrationFile(self):
        """
        Get the file name of the calibration file currently in use.

        Returns:
          File name of the calibration file currently in use.  None if no calibration
          file has yet been assigned.
        """
        return self._calibrationFile

    # ---------------------------------------------------------------------
    def setupBlankCalibration(self, layer, geometry):
        """
        Setup a blank calibration file for layer.
        """
        self._calibration = LayerCalibration()
        self._calibration.zFront = geometry.mostlyRetract
        self._calibration.zBack = geometry.mostlyExtend
        self._calibrationFile = f"{layer}_Calibration.xml"
        self._calibration.save(self.getPath(), self._calibrationFile)

    # ---------------------------------------------------------------------
    def setStage(self, stage, message="<unspecified>"):
        """
        Set the APA progress stage.

        Args:
          stage: Integer number (table in APA_Base.Stages) of APA progress.
          message: Message/reason for changing to new stage.
        """

        # Note in the log the stage change.
        self._log.add(
            self.__class__.__name__,
            "STAGE",
            f"APA stage change from {str(self._stage)} to {str(stage)}.  Reason: {message}",
            [self._stage, stage, message],
        )
        self._stage = stage

    # ---------------------------------------------------------------------
    def save(self):
        """
        Save current APA state to file.
        """
        self._lineNumber = self._gCodeHandler.getLine()
        APA_Base.save(self)

    # ---------------------------------------------------------------------
    def close(self):
        """
        Close an APA.  Call during shutdown sequence.  Called internally when new
        APA is loaded.
        """

        self.setLocation(
            self._gCodeHandler._x,
            self._gCodeHandler._y,
            self._gCodeHandler._headPosition
        )

        self._gCodeHandler.closeG_CodeLog()
        self.save()

        elapsedTime = self._systemTime.getDelta(self._startTime)
        deltaString = self._systemTime.getElapsedString(elapsedTime)

        self._log.add(
            self.__class__.__name__,
            "CLOSE",
            f"Closing APA {self._name}, {str(self._recipeFile)}:{str(self._lineNumber)} after {deltaString}",
            [self._name, self._recipeFile, self._lineNumber, elapsedTime],
        )
        self._log.detach(self.getPath() + AnodePlaneArray.LOG_FILE)
        AnodePlaneArray.activeAPA = None

# end class


if __name__ == "__main__":

    from Library.Log import Log
    from Library.SystemTime import SystemTime

    systemTime = SystemTime()
    log = Log(systemTime)
    log.add("Main", "START", "Control system starts.")

    from Machine.G_CodeHandlerBase import G_CodeHandlerBase

    gCodeHandler = G_CodeHandlerBase()

    apa = AnodePlaneArray(
        gCodeHandler,
        ".",
        ".",
        ".",
        "TestAPA",
        log,
        True)

    apa.save()
    apa.load()
