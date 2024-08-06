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
        self.__update_data(responce.json()['data'])


    def __str__(self):
        """ Return as a string """
        return f"{self.name}[{self.x}:{self.y}]"


    def __update_data(self, data):
        """ Updates char properties from data """
        self.data = data
        self.x = self.data['x']
        self.y = self.data['y']
        self.inventory = self.data['inventory']


    def __action(self, action, payload={}, on_error=None, on_success=None):
        """ Performs any action with api"""
        action_url = f"{API_URL}/my/{self.name}/action/{action}"
        responce = requests.post(action_url, json=payload, headers=HEADERS)
        if ("error" in responce.json()):
            if (responce.json()['error']['code'] == 499): 
                Log.info("Waiting and restarting crafting...")
                time.sleep(3)
                data = self.__action(action, payload, on_error, on_success)
                return data
            Log.error(f"{self} Failed to {action} due to: {responce.text}")
            if callable(on_error):
                on_error(responce.json()['error'])
        else:
            data = responce.json()['data']
            cooldown = data['cooldown']['total_seconds']
            self.__update_data(data['character'])
            # Log.debug(f"Inventory updated: {self.inventory}")
            if callable(on_success):
                on_success(data)
            Log.info(f"{self} Success, waiting for cooldown {cooldown}")
            time.sleep(cooldown + 3)
            return data


    def move(self, x:int, y:int):
        """ Move unit to coordinates """
        Log.info(f"Moving {self.name} to [{x}:{y}]")
        payload = { "x": x, "y": y } 
        def on_success(data):
            Log.info(f"{self} successfully moved. Here is {data['destination']}.")
        self.__action(action="move", payload=payload, on_success=on_success)


    def fight_cell(self):
        """ Triggers batlle on current location """
        Log.info(f"{self} Starting battle on current location...")
        def on_success(data):
            fight = data['fight']
            Log.info(f"{self} Battle with finised [{fight['result']}]. \nXP: {fight['xp']}\nGold: {fight['gold']}")
        data = self.__action(action="fight", on_success=on_success)
        return data


    def collect_resources(self):
        """ Collect resources on current location """
        Log.info(f"{self} Starting harvesting on current location...")
        def on_success(data):
            harvest_details = data['details']
            Log.info(f"{self} Harvesting with finised. Details: {harvest_details}")
        data = self.__action(action="gathering", on_success=on_success)
        return data


    def craft(self, item):
        """ Try to craft item """
        Log.info(f"[{self.name}] Crafting {item}")
        payload = { "code": item }
        def on_success(data):
            Log.info(f"Crafted {item}")
        data = self.__action(action="crafting", payload=payload, on_success=on_success)
        return data


    def has(self, item):
        """ Returns count of item in inventory """
        for inventory_item in self.inventory:
            if inventory_item['code'] == item:
                return inventory_item['quantity']
        return 0


    def is_full(self):
        """ Returns count of item in inventory """
        inventory_max = self.data['inventory_max_items']
        inventory_current = 0
        for inventory_item in self.inventory:
            if inventory_item['code'] != '':
                inventory_current += inventory_item['quantity']
        Log.debug(f"inventory_current: {inventory_current} inventory_max: {inventory_max}")
        return inventory_current >= inventory_max


    def deposit_all(self):
        """ Deposite all items from inventory """
        BANK = (4,1)
        self.move(*BANK)
        for inventory_item in self.inventory:
            def on_success(data):
                Log.info(f"{self} Moved to deposit {inventory_item['code']}({inventory_item['quantity']})")
            if ( inventory_item['code'] != '' ):
                payload = { "code": inventory_item['code'], "quantity": inventory_item['quantity'] }
                data = self.__action(action="bank/deposit", payload=payload, on_success=on_success)
        Log.info(f"{self} All inventory moved to deposit")
        return 0