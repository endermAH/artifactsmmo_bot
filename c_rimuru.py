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
Jobs.craft_item_reqursively('iron_armor', 1, rimuru)
Jobs.craft_item_reqursively('iron_legs_armor', 1, rimuru)
Jobs.craft_item_reqursively('iron_helm', 1, rimuru)
Jobs.craft_item_reqursively('iron_boots', 1, rimuru)
# Jobs.craft_item_reqursively('cooked_gudgeon', 1, banimaru)
# rimuru.move(*CHICKENS) 
# for i in range(30):
#     Jobs.craft_item_reqursively('copper_legs_armor', 1, rimuru)
# Telegram.notify(f"`{rimuru}` crafted *30* of *copper_legs_armor*")
##############

Log.info("Done")


