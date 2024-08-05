import requests
import time

from Classes.log import Log
from data import *

class Unit:

    def __init__(self, name):
        """ Initialization script """
        stats_url = f"{API_URL}/characters/{name}"
        responce = requests.get(stats_url, headers=HEADERS)

        self.name = name
        self.x = responce.json()['data']['x']
        self.y = responce.json()['data']['y']
        self.inventory = responce.json()['data']['inventory']


    def __str__(self):
        """ Return as a string """
        return f"{self.name}[{self.x}:{self.y}]"


    def __action(self, action, payload={}, on_error=None, on_success=None):
        """ Performs any action with api"""
        action_url = f"{API_URL}/my/{self.name}/action/{action}"
        responce = requests.post(action_url, json=payload, headers=HEADERS)
        if ("error" in responce.json()):
            Log.error(f"[{self.name}] Failed to {action} due to: {responce.text}")
            if callable(on_error):
                on_error(responce.json()['error'])
        else:
            data = responce.json()['data']
            cooldown = data['cooldown']['total_seconds']
            self.inventory = data['character']['inventory']
            # Log.debug(f"Inventory updated: {self.inventory}")
            if callable(on_success):
                on_success(data)
            Log.info(f"[{self.name}] Success, waiting for cooldown {cooldown}")
            time.sleep(cooldown + 3)
            return data


    def move(self, x:int, y:int):
        """ Move unit to coordinates """
        Log.info(f"Moving {self.name} to [{x}:{y}]")
        payload = { "x": x, "y": y } 
        def on_success(data):
            self.x = data['character']['x']
            self.y = data['character']['y']
            Log.info(f"{self} successfully moved. Here is {data['destination']}.")
        self.__action(action="move", payload=payload, on_success=on_success)


    def fight_cell(self):
        """ Triggers batlle on current location """
        Log.info(f"{self} Starting battle on current location...")
        def on_success(data):
            fight = data['fight']
            Log.info(f"{self} Battle with finised [{fight['result']}]. \nXP: {fight['xp']}\nGold: {fight['gold']}")
        def on_error(error):
            if (error['code'] == 499): 
                Log.info("Waiting and restarting battle...")
                time.sleep(3)
                self.fight_cell()
        self.__action(action="fight", on_success=on_success, on_error=on_error)


    def collect_resources(self):
        """ Collect resources on current location """
        Log.info(f"{self} Starting harvesting on current location...")
        def on_success(data):
            harvest_details = data['details']
            Log.info(f"{self} Harvesting with finised. Details: {harvest_details}")
        def on_error(error):
            if (error['code'] == 499): 
                Log.info("Waiting and restarting harvesting...")
                time.sleep(3)
                self.collect_resources()
        data = self.__action(action="gathering", on_success=on_success, on_error=on_error)
        return data


    def craft(self, item):
        """ Try to craft item """
        Log.info(f"[{self.name}] Crafting {item}")
        payload = { "code": item }
        def on_success(data):
            Log.info(f"Crafted {item}")
        def on_error(error):
            if (error['code'] == 499): 
                Log.info("Waiting and restarting crafting...")
                time.sleep(3)
                self.collect_resources()
        data = self.__action(action="crafting", payload=payload, on_success=on_success, on_error=on_error)
        return data


    def has(self, item):
        """ Returns count of item in inventory """
        for inventory_item in self.inventory:
            if inventory_item['code'] == item:
                return inventory_item['quantity']
        return 0