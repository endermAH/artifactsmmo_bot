import requests


class Telegram:

    @staticmethod
    def notify(message):
        """ Sends message from telegram bot """
        url = f"https://api.telegram.org/bot{TG_BOT_KEY}/sendMessage"
        params = { 'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'markdown' }
        response = requests.post(url, params=params)