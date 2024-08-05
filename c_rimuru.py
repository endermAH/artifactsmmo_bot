from Classes.jobs import Jobs
from Classes.log import Log
from Classes.unit import Unit
from Classes.telegram import Telegram


GREEN_SLIMES = (0, -1)
YELLOW_SLIMES = (1, -2)
CHICKENS = (0, 1)

Log.info("Started")

###############

### Banimaru ###

rimuru = Unit("rimuru")
# Jobs.craft_item_reqursively('cooked_gudgeon', 1, banimaru)
rimuru.move(*CHICKENS)
for i in range(10):
    Jobs.craft_item_reqursively('copper_armor', 1, rimuru)
Telegram.notify(f"`{unit}` crafted *10* of *copper_armor*")
##############

Log.info("Done")


