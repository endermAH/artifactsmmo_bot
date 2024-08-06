from Classes.jobs import Jobs
from Classes.log import Log
from Classes.unit import Unit
from Classes.maps import *
from Classes.telegram import Telegram


GREEN_SLIMES = (0, -1)
YELLOW_SLIMES = (1, -2)
BLUE_SLIMES = (0, -2)
CHICKENS = (0, 1)

Log.info("Started")

###############

### Rigurt ###

rigurt = Unit("Rigurt")
# rigurt.deposit_all()
Jobs.farm_level(unit=rigurt, skill="weaponcrafting", target_level=2)
# Jobs.craft_item_reqursively('cooked_chicken', 10, rigurt)
# Jobs.craft_item_reqursively('cooked_chicken', 10, rigurt)
# Jobs.craft_item_reqursively('cooked_chicken', 10, rigurt)
# Jobs.craft_item_reqursively('cooked_chicken', 10, rigurt)
# Jobs.craft_item_reqursively('cooked_chicken', 10, rigurt)

##############

# Map.find_resource('raw_beef', rigurt)

Log.info("Done")


