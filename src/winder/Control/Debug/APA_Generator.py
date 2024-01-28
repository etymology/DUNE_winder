###############################################################################
# Name: APA_Generator.py
# Uses: Randomly generate a new APA.  Temporary class for testing.
# Date: 2016-05-27
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import random
from Control.Process import Process
from Control.APA_Base import APA_Base

class APA_Generator :

  #---------------------------------------------------------------------
  @staticmethod
  def create( process, number ) :
    """
    Randomly generate a new APA.  Test function.

    Args:
      process: Instance of Process.
      number: Number of random APAs to create.
    """
    for _ in range( 0, number ) :
      random1 = random.randint( 0, 999 )
      random2 = random.randint( 0, 99 )
      random3 = random.randint( 0, 9999 )
      name =                             \
        "APA_"                           \
        + str( random1 ).zfill( 3 )      \
        + "-"                            \
        + str( random2 ).zfill( 2 )      \
        + "-"                            \
        + str( random3 ).zfill( 4 )

      process.createAPA( name )

      stage = random.randint( 0, APA_Base.Stages.COMPLETE )
      process.apa.setStage( stage, "Setting of random initial stage" )
      process.apa._windTime = random.randint( stage * 9 * 60 * 60, stage * 12 * 60 * 60 )


if __name__ == "__main__":
  APA_Generator.create( 25 )
