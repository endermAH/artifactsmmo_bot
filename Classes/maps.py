import requests
import math

from Classes.log import Log
from Classes.unit import Unit
from data import *

class MapResource:

    def __init__(self, name):
        resource_url = f"{API_URL}/resources/{name}"
        responce = requests.get(resource_url, headers=HEADERS)
        Log.info(f"{responce.json()}")
        if ("error" in responce.json() and responce.json()['error']['code'] == 404):
            Log.info(f"Resource {name} not found, searching for monster")
            resource_url = f"{API_URL}/monsters/{name}"
            responce = requests.get(resource_url, headers=HEADERS)
            # Log.info(f"{responce.json()}")

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
            if (tile['content'] != None):
                if (tile['content']['type'] in ["resource", "monster"]):
                    map_resource = MapResource(tile['content']['code'])
                    # Log.debug(f"Found {map_resource}")
                    if map_resource.can_drop(resource):
                        if math.dist([tile["x"], tile['y']], [unit.x, unit.y]) < dist:
                            coordinates = {"x": tile["x"], "y": tile['y'], "type": tile['content']['type']}
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