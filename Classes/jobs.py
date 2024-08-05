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
        resource_location = Map.find_resource(resource, unit)
        unit.move(resource_location['x'],resource_location['y'])
        collected = unit.has(resource)
        while (collected < ammount):
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