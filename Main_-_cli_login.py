import gevent.monkey

gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
from steam.client import SteamClient
from steam.enums import EResult

import discord
from discord.ext import commands

import sys
import logging, traceback
import json
import threading
import asyncio, time

preferences = json.loads(open('Login details/preferences.json', 'r').read())
command_prefix = preferences["Command Prefix"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), case_insensitive=True)
bot.remove_command('help')

# read details ---------------------------------------------------------------------------------------------------------

login = json.loads(open("Login details/sensitive details.json", "r").read())
token = login["Bot Token"]
username = login["Username"]
password = login["Password"]

bot.owner_id = int(preferences["Discord ID"])
bot.bot64id = int(preferences["Bot's Steam ID"])
bot.owner_name = preferences["Owner Name"]
bot.command_prefix = preferences["Command Prefix"]
bot.color = int(preferences["Embed Colour"], 16)
bot.templocation = preferences["Path to Temp"]

# vars -----------------------------------------------------------------------------------------------------------------

bot.sbotresp = 0
bot.usermessage = 0
bot.logged_on = 0
bot.toggleprofit = 0
bot.version = 'V.1.2'
bot.botresp = False
bot.client = SteamClient()
dsdone = 0

bot.updatem = bot.command_prefix + 'update name='
bot.removem = bot.command_prefix + 'remove item='
bot.addm = bot.command_prefix + 'add name='

activity = f'{bot.owner_name}\'s trades | {bot.version} | Command Prefix \"{bot.command_prefix}\"'
activity = discord.Activity(name=activity, type=discord.ActivityType.watching)

# cogs -----------------------------------------------------------------------------------------------------------------

initial_extensions = ['Cogs.discord',
                      'Cogs.help',
                      'Cogs.steam']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


# loading --------------------------------------------------------------------------------------------------------------


@bot.event
async def on_ready():
    await bot.change_presence(activity=activity)
    # githubupdate.start()
    print("Bot is ready")
    print('Logged in as', bot.user.name, 'Send this to Gobot1234 to add your bot to the server', bot.user.id,
          'to use the custom emojis',
          '\nThis is:', bot.version)
    global dsdone
    dsdone = 1
    await asyncio.sleep(30)

    while logged_on != 1:
        await bot.get_user(bot.owner_id).send('You aren\'t currently logged into your Steam account'
                                              '\nTo do that type in your 2FA code into the console.')
        await asyncio.sleep(60)
    await bot.get_user(bot.owner_id).send('I\'m online both Steam and Discord dealing with your Steam messages')


# threading ------------------------------------------------------------------------------------------------------------


def discordside():
    bot.run(token)


def steamside():
    global dsdone
    while 1:
        while dsdone != 0:
            logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO)
            LOG = logging.getLogger()
            client = SteamClient()
            client.set_credential_location("Login Details/")  # where to store sentry files and other stuff  

            @client.on("error")
            def handle_error(result):
                LOG.info(f'Logon result: {repr(result)}')

            @client.on("connected")
            def handle_connected():
                LOG.info(f'Connected to: {client.current_server_addr}')

            @client.on("reconnect")
            def handle_reconnect(delay):
                LOG.info(f'Reconnect in {delay}...')

            @client.on("disconnected")
            def handle_disconnect():
                LOG.info("Disconnected.")

                if client.relogin_available:
                    LOG.info("Reconnecting...")
                    client.reconnect(maxdelay=60)

            @client.on("logged_on")
            def handle_after_logon():
                global logged_on
                logged_on = 1
                LOG.info('-' * 30)
                LOG.info(f'Logged on as: {client.user.name}')
                LOG.info('-' * 30)

            @client.on("chat_message")
            def handle_message(user, message_text):
                global sbotresp
                global botresp
                global usermessage
                if user.steam_id == bot.bot64id:
                    if 'view it here' not in message_text and 'marked as declined' in message_text:
                        pass
                    else:
                        bot.sbotresp = message_text
                        bot.botresp = True
                        if 'from user' in bot.sbotresp:
                            bot.usermessage = bot.sbotresp
                        if time == '23:59' and "You've made" in bot.sbotresp:
                            bot.graphplots = bot.sbotresp
                else:
                    pass

            result = client.cli_login(username=username, password=password)
            if result != EResult.OK:
                LOG.info(f'Failed to login: {repr(result)}')
                sys.exit()

            while 1:
                client.run_forever()


t1 = threading.Thread(target=discordside)
t2 = threading.Thread(target=steamside)
t1.start()
t2.start()
