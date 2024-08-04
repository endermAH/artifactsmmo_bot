import requests
import time
import math

from log import Log
from unit import Unit
from data import *
from telegram import Telegram


GREEN_SLIMES = (0, -1)
YELLOW_SLIMES = (1, -2)


class MapResource:

    def __init__(self, name):
        resource_url = f"{API_URL}/resources/{name}"
        responce = requests.get(resource_url, headers=HEADERS)
        Log.info(f"{responce.json()}")
        self.name = name
        self.drops = responce.json()['data']['drops']

    
    def __str__(self):
        return f"{self.name}"


    def can_drop(self, resource):
        can_drop = False
        for drop in self.drops:
            if drop['code'] == resource:
                can_drop = True
        return can_drop


class Map:

    @staticmethod
    def collect_map():
        map = []
        page = 1
        map_url = f"{API_URL}/maps"
        responce = requests.get(map_url, headers=HEADERS)
        max_pages = responce.json()['pages']
        map += responce.json()['data']
        if max_pages > 1:
            for page in range(2,max_pages+1):
                responce = requests.get(map_url, headers=HEADERS, params={"page": page})
                max_pages = responce.json()['pages']
                map += responce.json()['data']
        return map


    @staticmethod
    def find_resource(resource, unit):
        """ Find nearest resource """
        Log.info(f"{unit} searching for nearest {resource}")
        world_map = Map.collect_map()
        dist = 9999
        coordinates = {}
        # Log.info(f"{world_map}")
        for tile in world_map:
            if (tile['content'] != None and tile['content']['type'] == "resource"):
                map_resource = MapResource(tile['content']['code'])
                # Log.debug(f"Found {map_resource}")
                if map_resource.can_drop(resource):
                    if math.dist([tile["x"], tile['y']], [unit.x, unit.y]) < dist:
                        coordinates = {"x": tile["x"], "y": tile['y']}
        Log.info(f"{unit} found {resource} at {coordinates}")
        return coordinates

    
    @staticmethod
    def find_workshop(skill, unit):
        """ Find nearest workshop """
        Log.info(f"{unit} searching for nearest workshop:{skill}")
        world_map = Map.collect_map()
        dist = 9999
        coordinates = {}
        # Log.info(f"{world_map}")
        for tile in world_map:
            if (tile['content'] != None and tile['content']['type'] == "workshop" and tile['content']['code'] == skill):
                if math.dist([tile["x"], tile['y']], [unit.x, unit.y]) < dist:
                    coordinates = {"x": tile["x"], "y": tile['y']}
        Log.info(f"{unit} found workshop:{skill} at {coordinates}")
        return coordinates


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


Log.info("Started")

### Rimuru ###

rimuru = Unit("rimuru")
for i in range(20):
    Jobs.craft_item_reqursively('copper_armor', 1, rimuru)

###############

### Rigurt ###

# rigurt = Unit("Rigurt")
# for i in range(10):
#     Jobs.craft_item_reqursively('cooked_gudgeon', 10, rigurt)

##############

Log.info("Done")


