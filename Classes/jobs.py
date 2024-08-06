import requests

from Classes.log import Log
from Classes.maps import *
from Classes.unit import Unit
from Classes.telegram import Telegram
from data import *

class Jobs:

    @staticmethod
    def collect_resource(resource, ammount, unit):
        """ Find nearest resource and collect required ammount in inventory """
        Log.info(f"{unit} started collecting {ammount} of {resource}")
        collected = unit.has(resource)
        if collected > ammount:
            Log.info(f"{unit} already has {ammount} of {resource}")
            return
        resource_location = Map.find_resource(resource, unit)
        unit.move(resource_location['x'],resource_location['y'])
        while (collected < ammount):
            if resource_location['type'] == "monster":
                data = unit.fight_cell()
                if data['fight']['result'] == "lose":
                    Telegram.notify(f"{unit} losed fight during collecting {resource}")
                    return false
            if resource_location['type'] == "resource":
                data = unit.collect_resources()
            # Log.debug(f"{data}")
            if (data == None): 
                continue
            collected = unit.has(resource)
            Log.info(f"{unit} collected {collected} of {resource}...")
        Log.info(f"{unit} Successfully collected {collected} of {resource}")


    @staticmethod
    def craft_items(item, ammount, unit):
        """ Craft ammount item """
        Log.info(f"{unit} started crafting {ammount} of {item}")
        # get workshop type
        item_url = f"{API_URL}/items/{item}"
        responce = requests.get(item_url, headers=HEADERS)
        item_info = responce.json()['data']
        skill = item_info['item']['craft']['skill']
        # search for workshop
        workshop_location = Map.find_workshop(skill, unit)
        # go to workshop 
        unit.move(workshop_location['x'], workshop_location['y'])
        # creaft required ammount
        for i in range(ammount):
            unit.craft(item)
    

    @staticmethod
    def craft_item_reqursively(item, count, unit):
        """ Collect all recources and craft item """
        items = Jobs.__get_required_resources(item, count, {"harvest": {}, "craft": {}})
        Log.info(f"{unit} Items to craft {item}({count}): {items}")
        for harvest_item, harvest_count in items['harvest'].items():
            Log.info(f"{unit} Harvesting {harvest_count} of {harvest_item}")
            Jobs.collect_resource(harvest_item, harvest_count, unit)
        for craft_item, craft_count in dict(reversed(list(items['craft'].items()))).items():
            Log.info(f"{unit} Crafting {craft_item} of {craft_count}")
            Jobs.craft_items(craft_item, craft_count, unit)
        Log.info(f"{unit} Successfully crafted {item}")
        Telegram.notify(f"`{unit}` Successfully crafted *{count}* of *{item}*")
        return


    @staticmethod
    def __get_required_resources(item, count, res_array={"harvest": {}, "craft": {}}):
        """ Returns list of resources required to craft """
        Log.debug(f"Processing {item}")
        item_url = f"{API_URL}/items/{item}"
        responce = requests.get(item_url, headers=HEADERS)
        Log.debug(f"{responce.json()}")
        item_info = responce.json()['data']['item']
        if item_info['craft'] == None:
            if item in res_array['harvest']:
                res_array['harvest'][item] += count
            else:
                res_array['harvest'][item] = count
            return res_array
        else:
            if item in res_array['craft']:
                res_array['craft'][item] += count
            else:
                res_array['craft'][item] = count
            for craft_item in item_info['craft']['items']:
                item_res_array = Jobs.__get_required_resources(craft_item['code'], craft_item['quantity']*count, res_array)
            return res_array

    
    @staticmethod
    def farm_level(unit, skill, target_level):
        """ Reaches level in target skill """
        implemented = ["woodcutting", "mining", "fishing", "weaponcrafting", "gearcrafting"]
        harvesting = ["woodcutting", "mining", "fishing"]
        crafting = ["weaponcrafting", "gearcrafting", "cooking", "jewelrycrafting"]
        if skill not in implemented:
            Log.error(f"Reaching {implemented} level is not implemented")
            return None
        try:
            skill_name = f"{skill}_level"
            Log.info(f"{unit} Current {skill} level is {unit.data[skill_name]}/{target_level}")
            if skill in harvesting:
                Jobs.farm_harvesting_level(unit, skill, target_level)
            if skill in crafting:
                Jobs.farm_crafting_level(unit, skill, target_level)
        except:
            Log.error(f"{unit} Failed to reach {skill}({target_level}) on {position}")
            Telegram.notify(f"`{unit}` Failed to reach *{skill}({target_level})* on *{position}* - please check logs.")


    @staticmethod
    def farm_crafting_level(unit, skill, target_level):
        """ Reaches level in any crafting skill """
        items_to_craft = {
            "weaponcrafting": {
                0: "copper_dagger",
                5: "sticky_dagger",
                10: "iron_sword",
                15: "multislimes_sword",
                20: "battlestaff",
                25: "skull_wand",
                30: "gold_sword"
            },
            "gearcrafting": {
                0: "copper_boots",
                5: "copper_legs_armor",
                10: "iron_boots",
                15: "mushmush_wizard_hat",
                20: "steel_helm",
                25: "lizard_skin_armor",
                30: "gold_platebody"
            },
            "cooking": {
                0: "cooked_gudgeon",
                5: "cooked_gudgeon",
                10: "cooked_shrimp",
                15: "cooked_shrimp",
                20: "cooked_trout",
                25: "cooked_trout",
                30: "cooked_bass"
            },
            "jewelrycrafting": {
                0: "copper_ring",
                5: "life_amulet",
                10: "iron_ring",
                15: "air_ring",
                20: "ring_of_chance",
                25: "ring_of_chance",
                30: "ruby_ring"
            }
        }
        skill_level_key = f"{skill}_level"
        current_level = unit.data[skill_level_key]
        item_key = math.floor(current_level/5)*5
        if item_key > 30: item_key = 30
        item_to_craft = items_to_craft[skill][item_key]
        Log.info(f"{unit} Starting farming {skill} level on {item_to_craft} crafting")
        while (current_level < target_level):
            Jobs.craft_item_reqursively(item_to_craft, 1, unit)
            unit.deposit_all()
            new_current_level = unit.data[skill_level_key]
            if new_current_level != current_level:
                Log.info(f"{unit} reached level {new_current_level}/{target_level} in {skill}")
                Telegram.notify(f"`{unit}` reached level *{new_current_level}/{target_level}* in * {skill}*")
            current_level = new_current_level


    @staticmethod
    def farm_harvesting_level(unit, skill, target_level):
        """ Reaches level in any harvesting skill """
        farming_map = {
            "woodcutting": {
                0: (6, 1),
                10: (-2, 5),
                20: (3, 5),
                30: (9, 8)
            },
            "mining": {
                0: (2, 0),      # copper
                10: (1, 7),     # iron
                20: (1, 6),     # coal
                30: (10, -4)    # gold
            },
            "fishing": {
                0: (4, 2), 
                10: (5, 2),
                20: (-2, 6),
                30: (-3, 6)
            }
        }
        skill_level_key = f"{skill}_level"
        current_level = unit.data[skill_level_key]
        location_key = math.floor(current_level/10)*10
        if location_key > 30: location_key = 30
        location = farming_map[skill][location_key]
        Log.info(f"{unit} Starting farming on {location}")
        unit.move(*location)
        while (current_level < target_level):
            unit.collect_resources()
            if unit.is_full():
                unit.deposit_all()
                unit.move(*location)
            new_current_level = unit.data[skill_level_key]
            if new_current_level != current_level:
                Log.info(f"{unit} reached level {new_current_level}/{target_level} in {skill}")
                Telegram.notify(f"`{unit}` reached level *{new_current_level}/{target_level}* in * {skill}*")
            current_level = new_current_level
            # check level reached

    