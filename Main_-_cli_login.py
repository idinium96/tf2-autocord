import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
from steam.enums import EResult
from steam.client import SteamClient

from discord.ext import commands

import sys
import traceback
import json
import threading
import os


preferences = json.loads(open('Login details/preferences.json', 'r').read())
command_prefix = preferences["Command Prefix"]
login = json.loads(open('Login details/sensitive details.json', 'r').read())
token = login["Bot Token"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), case_insensitive=True,
                   description='Used to manage your tf2automatic bot and send all of your messages via Discord')
bot.remove_command('help')
bot.cli_login = False

# cogs -----------------------------------------------------------------------------------------------------------------

bot.initial_extensions = os.listdir('Cogs')  # getting the cog files in the "Cogs" folder and removing the none .py ones

if __name__ == '__main__':
    print(f'Extensions to be loaded are {bot.initial_extensions}')
    for extension in bot.initial_extensions:
        if extension.endswith('.py'):
            try:
                bot.load_extension(f'Cogs.{extension[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

# threading ------------------------------------------------------------------------------------------------------------

def discordside():
    print('\033[95m' + '-' * 30 + '\033[95m')
    print('\033[95m' + 'Discord is logging on' + '\033[95m')
    bot.run(token)


def steamside():
    while 1:
        if bot.dsdone is True:
            bot.client = SteamClient()
            print('\033[95m' + '-' * 30 + '\033[95m')
            print('\033[95m' + 'Steam is now logging on' + '\033[95m')
            bot.client.set_credential_location('Login Details/')  # where to store sentry files and other stuff  

            @bot.client.on('error')
            def handle_error(result):
                print('\033[91m' + f'Logon result: {repr(result)}' + '\033[91m')

            @bot.client.on('connected')
            def handle_connected():
                print('\033[92m' + f'Connected to: {bot.client.current_server_addr}' + '\033[92m')

            @bot.client.on('reconnect')
            def handle_reconnect(delay):
                print('\033[94m' + f'Reconnect in {delay}...' + '\033[94m')

            @bot.client.on('disconnected')
            def handle_disconnect():
                print('\033[93m' + 'Disconnected.' + '\033[93m')

                if bot.client.relogin_available:
                    print('Reconnecting...')
                    bot.client.reconnect(maxdelay=30)

            @bot.client.on('logged_on')
            def handle_after_logon():
                bot.logged_on = True
                print('\033[92m' + f'Logged on as: {bot.client.user.name}' + '\033[92m')

            @bot.client.on('chat_message')
            def handle_message(user, message_text):
                if user.steam_id == bot.bot64id:
                    if 'view it here' not in message_text and 'marked as declined' in message_text:
                        pass
                    else:
                        bot.sbotresp = message_text
                        bot.botresp = True
                        if 'from user' in bot.sbotresp:
                            bot.usermessage = bot.sbotresp
                        if bot.currenttime == '23:59' and "You've made" in bot.sbotresp:
                            bot.graphplots = bot.sbotresp

            result = bot.client.cli_login(username=bot.username, password=bot.password)
            if result != EResult.OK:
                print('\033[91m' + f'Failed to login: {repr(result)}' + '\033[91m')
                raise SystemExit
            while 1:
                bot.client.run_forever()



t1 = threading.Thread(target=discordside).start()
t2 = threading.Thread(target=steamside).start()
