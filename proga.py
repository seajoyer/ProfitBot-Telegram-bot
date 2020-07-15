import configparser
import pickle
import time

from telethon import events

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import connection

from datetime import date, datetime

all_messages = []

config = configparser.ConfigParser()
config.read("/home/Dmitry/Projects/ProfitBot/config.ini")



api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(None, api_id, api_hash)

@client.on(events.NewMessage(chats=('Profit2020bot')))
async def normal_handler(event):
    if event.message.to_dict()['message'] == 'Overload':
        await send_message('http://t.me/telemetr_chat_bot')

@client.on(events.NewMessage(chats=('telemetr_chat_bot')))
async def normal_handler(event):
    all_messages.append(event.message.to_dict()['message'])

client.start()

async def send_message(channal):

    female_goro = 'https://t.me/joinchat/AAAAAFcdEJ-HYLqd3U1e8w\n\nhttps://t.me/joinchat/AAAAAFc0EXkmDoWlBTSVeg\n\nhttps://t.me/joinchat/AAAAAE2wBVb3WnFKPKKIFQ\n\nhttps://t.me/joinchat/AAAAAFNpkHCd68B3Z08I4g\n\nhttps://t.me/joinchat/AAAAAEhDI0BJEB7xmwJV5w\n\nhttps://t.me/joinchat/AAAAAFDRkMiT2j0AZ-DyiQ\n\nhttps://t.me/joinchat/AAAAAEpov_EQ-Lmdugnu9w\n\nhttps://t.me/joinchat/AAAAAFPKZVZczIW-JMUB0Q\n\nhttps://t.me/joinchat/AAAAAElBFQd_GQsRpyiGOA\n\nhttps://t.me/joinchat/AAAAAEyux5pvsmuV72KELA\n\nhttps://t.me/joinchat/AAAAAE43OJq4-33TObd8QQ\n\nhttps://t.me/joinchat/AAAAAFI15NR7SvazeatvYQ'
    male_goro = 'https://t.me/joinchat/AAAAAFAfB3Oc1ARYofaVaA\n\nhttps://t.me/joinchat/AAAAAEleiFKyAk9E8nFvnw\n\nhttps://t.me/joinchat/AAAAAEXqB7r29Omdt8jkAw\n\nhttps://t.me/joinchat/AAAAAFijcvKeEgsOxk7s7A\n\nhttps://t.me/joinchat/AAAAAFiKihPJhBVbavclqg\n\nhttps://t.me/joinchat/AAAAAFQ120SmCSlTRjvVEw\n\nhttps://t.me/joinchat/AAAAAFRi2oEDqVnTRzhxog\n\nhttps://t.me/joinchat/AAAAAFMLtoAiCuJAhgt-yg\n\nhttps://t.me/joinchat/AAAAAE62--tnPlKWNLnXnw\n\nhttps://t.me/joinchat/AAAAAEyFi3qW3RhC2Rgqjw\n\nhttps://t.me/joinchat/AAAAAFhehPuBQopEzZh0ew\n\nhttps://t.me/joinchat/AAAAAEvShdRVBKU6YSybwQ'
    female_facts = 'https://t.me/joinchat/AAAAAFPaEpvCnT-ak_mtyg\n\nhttps://t.me/joinchat/AAAAAE33ML6GzvW9tekJ_w\n\nhttps://t.me/joinchat/AAAAAFVNda_33ykOj4jXHg\n\nhttps://t.me/joinchat/AAAAAEl8dEN10lVQtCeiKw\n\nhttps://t.me/joinchat/AAAAAFNE2lRBfktXT_Cc2A\n\nhttps://t.me/joinchat/AAAAAEiL3fDNmnGffxPTmA\n\nhttps://t.me/joinchat/AAAAAEUbLsg86r_WIl5JVQ\n\nhttps://t.me/joinchat/AAAAAFXAUCOMIeLAKkeUfQ\n\nhttps://t.me/joinchat/AAAAAE3F4YhUzMWPUEogbQ\n\nhttps://t.me/joinchat/AAAAAEVhlrqhwj5G-a7gtA\n\nhttps://t.me/joinchat/AAAAAFdfMCuJAlEUNnsSQg\n\nhttps://t.me/joinchat/AAAAAFG9eP6qtAPfgYvdEw'
    male_facts = 'https://t.me/joinchat/AAAAAEjo_i1L09hYd5OXbQ\n\nhttps://t.me/joinchat/AAAAAFkjHIdnkBHLb5fkiQ\n\nhttps://t.me/joinchat/AAAAAFkT1Mqquixt6QNr2A\n\nhttps://t.me/joinchat/AAAAAE2CrhweYpyJAPJidQ\n\nhttps://t.me/joinchat/AAAAAFgH8khSsMsDJJHVSg\n\nhttps://t.me/joinchat/AAAAAFJczwWrBJu46pjdlA\n\nhttps://t.me/joinchat/AAAAAEb5-M6DvJMZrB4Ohg\n\nhttps://t.me/joinchat/AAAAAFU4N_gGCRUO7iiVxQ\n\nhttps://t.me/joinchat/AAAAAFW3UuxFQCm1oNwyYw\n\nhttps://t.me/joinchat/AAAAAEm8uWXCBuSk6nJS5g\n\nhttps://t.me/joinchat/AAAAAFEw6wiqb0n8VeG2rw\n\nhttps://t.me/joinchat/AAAAAFI9PI1oajbqXh1oqQ'

    await client.send_message(channal, female_goro)
    time.sleep(1.7)
    await client.send_message(channal, male_goro)
    time.sleep(1.7)
    await client.send_message(channal, female_facts)
    time.sleep(1.7)
    await client.send_message(channal, male_facts)
    time.sleep(1.7)

    client.loop.run_until_complete(main())

async def dump_all_messages():

# +380954793734

    global all_messages
    with open('/home/Dmitry/Projects/ProfitBot/channel_messages.pickle', 'wb') as outfile:
         pickle.dump(all_messages, outfile, protocol=2)
         all_messages = []


async def main():
    await dump_all_messages()


with client:
    client.loop.run_forever()
