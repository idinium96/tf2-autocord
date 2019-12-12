from gevent.monkey import patch_socket, patch_ssl
patch_socket()
patch_ssl()
from steam.enums import EResult
from steam.client import SteamClient
from steam import guard

from json import loads
from sys import stderr
from traceback import print_exc
from threading import Thread
from os import listdir
from os.path import isfile, join
from logging import getLogger, DEBUG, Formatter, FileHandler

from discord import ClientException
from discord.ext import commands

# setup ----------------------------------------------------------------------------------------------------------------

preferences = loads(open('Login details/preferences.json', 'r').read())
command_prefix = preferences["Command Prefix"]
login = loads(open('Login details/sensitive details.json', 'r').read())
token = login["Bot Token"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), case_insensitive=True,
                   description='Used to manage your tf2automatic bot and send all of Steam messages through Discord')
bot.cli_login = False

# logging --------------------------------------------------------------------------------------------------------------

bot.log = getLogger()
bot.log.setLevel(DEBUG)
handler = FileHandler(filename='tf2autocord.log', encoding='utf-8', mode='w')
handler.setFormatter(Formatter('%(asctime)s : %(levelname)s : %(name)s | %(message)s'))
bot.log.addHandler(handler)

# cogs -----------------------------------------------------------------------------------------------------------------

bot.initial_extensions = [f.replace('.py', '') for f in listdir("Cogs") if isfile(join("Cogs", f))]
if __name__ == '__main__':
    bot.log.info(f'Extensions to be loaded are {bot.initial_extensions}')
    for extension in bot.initial_extensions:
        try:
            bot.load_extension(f'Cogs.{extension}')
        except (ClientException, ModuleNotFoundError):
            bot.log.error(f'Failed to load extension {extension}.', file=stderr)
            print_exc()

# threading ------------------------------------------------------------------------------------------------------------

def discordside():
    bot.log.info('-' * 30)
    print('Discord is logging on')
    bot.log.info('Discord is logging on')
    try:
        bot.dsdone = True
        bot.run(token)
    except RuntimeError:
        bot.log.info('Logging out')
        raise SystemExit


def steamside():
    while 1:
        if bot.dsdone is True:
            bot.client = SteamClient()
            print('Steam is now logging on')
            bot.log.info('Steam is now logging on')
            bot.client.set_credential_location('Login Details/')  # where to store sentry files and other stuff  

            @bot.client.on('error')
            def handle_error(result):
                bot.log.error(f'Logon result: {repr(result)}')

            @bot.client.on('connected')
            def handle_connected():
                bot.log.info(f'Connected to: {bot.client.current_server_addr}')

            @bot.client.on('reconnect')
            def handle_reconnect(delay):
                bot.log.info(f'Reconnect in {delay}...')

            @bot.client.on('disconnected')
            def handle_disconnect():
                bot.log.warning('Disconnected.')

                if bot.client.relogin_available:
                    bot.log.info('Reconnecting...')
                    bot.client.reconnect(maxdelay=30)

            @bot.client.on('logged_on')
            def handle_after_logon():
                bot.logged_on = True
                bot.log.info(f'Logged on as: {bot.client.user.name}')

            @bot.client.on('chat_message')
            def handle_message(user, message_text):
                if user.steam_id == bot.bot64id:
                    if 'from user' in message_text:
                        bot.usermessage = message_text
                    if bot.currenttime == '23:59' and "You've made" in message_text:
                        bot.graphplots = message_text
                    else:
                        bot.sbotresp = message_text

            SA = guard.SteamAuthenticator(bot.secrets).get_code()
            result = bot.client.login(username=bot.username, password=bot.password, two_factor_code=SA)
            if result != EResult.OK:
                bot.log.fatal(f'Failed to login: {repr(result)}')
                raise SystemExit

            bot.s_bot = bot.client.get_user(bot.bot64id)
            try:
                bot.client.run_forever()
            except KeyboardInterrupt:
                bot.client.logout()
                print('Logging out')
                bot.log.info('Logging out')
                raise SystemExit


Thread(target=discordside).start()
Thread(target=steamside).start()
