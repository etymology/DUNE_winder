#==============================================================================
# Name: IO.py
# Uses: Master I/O instance.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
# Note:
#   All software should use the instance of "io" for all hardware I/O and
#   nothing else in this directory.
#
#==============================================================================
from Maps.SimulatedIO import SimulatedIO

# Create instance of I/O.
io = SimulatedIO()
