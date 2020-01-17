from gevent.monkey import patch_socket, patch_ssl; patch_socket(); patch_ssl()
from aiohttp import ClientSession
from datetime import datetime
from logging import getLogger, Formatter, StreamHandler, FileHandler, DEBUG, ERROR
from os import listdir
from os.path import isfile, join
from sys import stderr
from traceback import print_exc
from time import sleep

from discord import ClientException
from discord.ext.commands import Bot, when_mentioned_or
from steam.enums import EResult
from steam.client import SteamClient
from steam import guard
from Login_details import preferences, sensitive_details


class AutoCord(Bot):
    def __init__(self):
        super().__init__(command_prefix=when_mentioned_or(preferences.command_prefix), case_insensitive=True,
                         description='**tf2-autocord** is a Discord bot that manages your tf2automatic bot. As it '
                                     'sends your Steam messages through Discord by logging into to your Steam '
                                     'account, then it will then monitor Steam chat messages from tf2automatic then '
                                     'send them to your Discord bot.')

    async def on_connect(self):
        bot.dsdone = True

    async def setup(self, bot):
        bot.dsdone = False
        bot.log = getLogger('tf2autocord')
        bot.log.setLevel(DEBUG)
        fh = FileHandler(filename='tf2autocord.log', encoding='utf-8', mode='w')
        fh.setLevel(DEBUG)
        ch = StreamHandler()
        ch.setLevel(ERROR)
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        bot.log.addHandler(fh)
        bot.log.addHandler(ch)
        bot.log.info('Discord is logging on')
        bot.log.info('-' * 30)

        bot.initial_extensions = [f[:-3] for f in listdir('Cogs') if isfile(join('Cogs', f))]
        print(f'Extensions to be loaded are {bot.initial_extensions}')
        bot.log.info(f'Extensions to be loaded are {bot.initial_extensions}')

        for extension in bot.initial_extensions:
            try:
                bot.load_extension(f'Cogs.{extension}')
            except (ClientException, ModuleNotFoundError):
                bot.log.error('Failed to load extension %s.', extension, file=stderr)
                print_exc()
        bot.log.info('Completed loading extensions')
        bot.session = ClientSession()

    def steam_start(self, bot):
        print('Steam is now logging on')
        bot.log.info('Steam is now logging on')
        bot.steam = SteamClient()
        bot.steam.set_credential_location('Login_details')  # where to store sentry files and other stuff  

        @bot.steam.on('error')
        def handle_error(result):
            bot.log.error(f'Logon result: {repr(result)}')

        @bot.steam.on('connected')
        def handle_connected():
            bot.log.info(f'Connected to: {bot.steam.current_server_addr}')

        @bot.steam.on('reconnect')
        def handle_reconnect(delay):
            if bot.steam is None:
                raise SystemExit
            bot.log.info(f'Reconnect in {delay}...')

        @bot.steam.on('disconnected')
        def handle_disconnect():
            bot.log.warning('Disconnected.')
            if bot.steam is None:
                raise SystemExit
            if bot.steam.relogin_available:
                bot.log.info('Reconnecting...')
                bot.steam.reconnect(maxdelay=30)

        @bot.steam.on('logged_on')
        def handle_after_logon():
            bot.s_bot = bot.steam.get_user(bot.bot64id)
            bot.logged_on = True
            bot.log.info(f'Logged on as: {bot.steam.user.name}')

        @bot.steam.on('chat_message')
        def handle_message(user, message_text):
            if user.steam_id == bot.bot64id:
                if message_text.startswith('Message from'):
                    bot.user_message = message_text
                elif bot.current_time.split()[1] == '23:59' \
                        and message_text.startswith("You've made") \
                        or message_text.startswith("Trades today"):
                    bot.daily = message_text

                else:
                    bot.sbotresp = message_text

        if preferences.cli_login:
            bot.log.info('Logging in using cli_login')
            result = bot.steam.cli_login(username=sensitive_details.username, password=sensitive_details.password)
        else:
            bot.log.info('Logging in using automatic')
            SA = guard.SteamAuthenticator(sensitive_details.secrets).get_code()
            result = bot.steam.login(username=sensitive_details.username, password=sensitive_details.password,
                                      two_factor_code=SA)
            if result == EResult.TwoFactorCodeMismatch:
                sleep(2)
                result = bot.steam.login(username=sensitive_details.username, password=sensitive_details.password,
                                          two_factor_code=SA)

        if result != EResult.OK:
            bot.log.fatal(f'Failed to login: {repr(result)}')
            raise SystemExit
        bot.steam.run_forever()

    def run(self, bot):
        print('Discord is logging on')
        bot.loop.run_until_complete(bot.setup(bot))
        try:
            bot._steam = bot.loop.run_in_executor(None, self.steam_start, bot)
            bot.launch_time = datetime.utcnow()
            super().run(sensitive_details.token)
        except RuntimeError:
            bot.log.info('Logging out')
            bot.steam = None
        except KeyboardInterrupt:
            bot.log.info('Logging out')
            bot.steam = None
        finally:
            raise SystemExit


if __name__ == '__main__':
    bot = AutoCord()
    bot.run(bot)
