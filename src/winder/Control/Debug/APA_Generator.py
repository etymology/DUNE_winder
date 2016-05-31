###############################################################################
# Name: APA_Generator.py
# Uses: Randomly generate a new APA.  Temporary class for testing.
# Date: 2016-05-27
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import random
from Control.Process import Process

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


if __name__ == "__main__":
  APA_Generator.create( 25 )
