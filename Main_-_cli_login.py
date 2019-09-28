import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
from steam.client import SteamClient
from steam.enums import EResult

import discord
from discord.ext import commands

import sys
import traceback
import json
import threading
import asyncio
from Cogs.loader import LoaderCog


preferences = json.loads(open('Login details/preferences.json', 'r').read())
command_prefix = preferences["Command Prefix"]
login = json.loads(open('Login details/sensitive details.json', 'r').read())
token = login["Bot Token"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), case_insensitive=True)
bot.remove_command('help')
bot.cli_login = True

# cogs -----------------------------------------------------------------------------------------------------------------

initial_extensions = ['Cogs.discord',
                      'Cogs.help',
                      'Cogs.steam',
                      'Cogs.loader']

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
    activity = f'{bot.owner_name}\'s trades | V{LoaderCog.__version__} | Command Prefix \"{bot.command_prefix}\"'
    activity = discord.Activity(name=activity, type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    print('-' * 30)
    print('\033[92m' + bot.user.name + ' is ready' + '\033[92m')
    print(f'Send this id: ' + '\033[95m' + f'\"{bot.user.id}\"' + '\033[95m' + '\033[92m' + ' to Gobot1234 to add your bot to the server to use the custom emojis',
          '\nThis is: ' + '\033[95m' + f'Version {LoaderCog.__version__}' + '\033[95m')
    bot.dsdone = 1
    await asyncio.sleep(30)

    while logged_on != 1:
        await bot.get_user(bot.owner_id).send('You aren\'t currently logged into your Steam account'
                                              '\nTo do that type in your 2FA code into the console.')
        await asyncio.sleep(60)
    await bot.get_user(bot.owner_id).send('I\'m online both Steam and Discord dealing with your Steam messages')
    print('-' * 30)


# threading ------------------------------------------------------------------------------------------------------------


def discordside():
    print('\033[95m' + '-' * 30 + '\033[95m')
    print('\033[95m' + 'Discord is logging on' + '\033[95m')
    bot.run(token)


def steamside():
    while 1:
        while bot.dsdone != 0:
            client = SteamClient()
            print('\033[95m' + '-' * 30 + '\033[95m')
            print('\033[95m' + 'Steam is now logging on' + '\033[95m')
            client.set_credential_location('Login Details/')  # where to store sentry files and other stuff  

            @client.on('error')
            def handle_error(result):
                print('\033[91m' + f'Logon result: {repr(result)}' + '\033[91m')

            @client.on('connected')
            def handle_connected():
                print('\033[92m' + f'Connected to: {client.current_server_addr}' + '\033[92m')

            @client.on('reconnect')
            def handle_reconnect(delay):
                print('\033[94m' + f'Reconnect in {delay}...' + '\033[94m')

            @client.on('disconnected')
            def handle_disconnect():
                print('\033[93m' + 'Disconnected.' + '\033[93m')

                if client.relogin_available:
                    print('Reconnecting...')
                    client.reconnect(maxdelay=30)

            @client.on('logged_on')
            def handle_after_logon():
                global logged_on
                logged_on = 1
                print('\033[92m' + f'Logged on as: {client.user.name}' + '\033[92m')

            @client.on('chat_message')
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

            result = client.cli_login(username=bot.username, password=bot.password)
            if result != EResult.OK:
                print('\033[91m' + f'Failed to login: {repr(result)}' + '\033[91m')
            while 1:
                client.run_forever()


t1 = threading.Thread(target=discordside)
t2 = threading.Thread(target=steamside)
t1.start()
t2.start()
