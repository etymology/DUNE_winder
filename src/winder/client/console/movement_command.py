from .command import Command

class MovementCommand( Command ):
   class Keys:
      MovementRateCallback = "movement_rate_callback"

   def __init__( self, **kwargs ):
      if MovementCommand.Keys.MovementRateCallback in kwargs:
         self.movement_rate_callback = kwargs[ MovementCommand.Keys.MovementRateCallback ]
         del kwargs[ MovementCommand.Keys.MovementRateCallback ]
      else:
         self.movement_rate_callback = None
