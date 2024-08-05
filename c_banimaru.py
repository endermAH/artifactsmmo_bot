from Classes.jobs import Jobs
from Classes.log import Log
from Classes.unit import Unit
from Classes.telegram import Telegram


GREEN_SLIMES = (0, -1)
YELLOW_SLIMES = (1, -2)
BLUE_SLIMES = (0, -2)
CHICKENS = (0, 1)

Log.info("Started")

###############

### Banimaru ###

banimaru = Unit("Banimaru")
# Jobs.craft_item_reqursively('cooked_gudgeon', 1, banimaru)
# Jobs.craft_item_reqursively('wooden_shield', 1, banimaru)
banimaru.move(*BLUE_SLIMES)
for i in range(50):
    banimaru.fight_cell()
Telegram.notify(f"`{banimaru}` Killed *50* of *YELLOW_SLIMES*")
##############

Log.info("Done")

