This is an updated version the manual calibration converter utility.  It should be able to run for any layer.  It takes command line parameters:
                python csv2calibration <layer> <input CSV> <output XML>

For example, the V layer is as follows:
                python csv2calibration.py V vCalibration.csv V_Calibration.xml

It must be placed in the same path as the APA being updated.  For example, C:\BIN\T01-Winder\src\winder\Data\APA\V_Test.  To run on a new layer, create an APA for this layer, copy in the .csv file and the conversion utility, and run it.  The include path for packages is relative, which is why it must be placed in the APA data directory.
