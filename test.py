from telegram import Bot
import asyncio

bot_token = '7349296181:AAHhlfSzSrWwQJ--JomDMl-h36I6zgMdyvY'
chat_id = '291961162'
message = 'Hello, this is a test message!'

async def send_message():
    bot = Bot(token=bot_token)
    await  bot.send_message(chat_id=chat_id, text=message)

asyncio.run(send_message())

print("Message sent!")