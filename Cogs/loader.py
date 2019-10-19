import traceback

import discord
from discord.ext import commands

import asyncio
import json
import os

from sys import argv, executable, stderr
from datetime import datetime


class LoaderCog(commands.Cog, name='Loader'):
    """This cog just stores all of your variables nothing particularly interesting and a few commands for development"""
    __version__ = '1.2.2'

    def __init__(self, bot):
        self.bot = bot

        login = json.loads(open("Login details/sensitive details.json", "r").read())
        bot.username = login["Username"]
        bot.password = login["Password"]
        try:
            bot.secrets = {
                "identity_secret": login["Identity Secret"],
                "shared_secret": login["Shared Secret"]
            }
        except:
            pass

        preferences = json.loads(open('Login details/preferences.json', 'r').read())
        bot.owner_id = int(preferences["Discord ID"])
        bot.bot64id = int(preferences["Bot's Steam ID"])
        bot.owner_name = preferences["Owner Name"]
        bot.command_prefix = preferences["Command Prefix"]
        bot.color = int(preferences["Embed Colour"], 16)
        bot.templocation = preferences["Path to Temp"]

        bot.sbotresp = 0
        bot.usermessage = 0
        bot.logged_on = 0
        bot.toggleprofit = 0
        bot.dsdone = 0
        bot.currenttime = datetime.now().strftime("%H:%M")
        bot.trades = 0

        bot.updatem = f'{bot.command_prefix}update name='
        bot.removem = f'{bot.command_prefix}remove item='
        bot.addm = f'{bot.command_prefix}add name='

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(
            name=f'{self.bot.owner_name}\'s trades | V{LoaderCog.__version__} | Command Prefix \"{self.bot.command_prefix}\"',
            type=discord.ActivityType.watching))
        print('-' * 30)
        print('\033[92m' + self.bot.user.name + ' is ready' + '\033[92m')
        print(
            f'Send this id: ' + '\033[95m' + f'\"{self.bot.user.id}\"' + '\033[95m' + '\033[92m' + ' to Gobot1234 to add your bot to the server to use the custom emojis',
            '\nThis is: ' + '\033[95m' + f'Version {LoaderCog.__version__}' + '\033[95m')
        self.bot.dsdone = True
        try:
            self.bot.trades = int(open('trades.txt', 'r').read())
        except:
            pass
        await asyncio.sleep(15)
        try:
            os.remove('trades.txt')
        except:
            pass
        while self.bot.logged_on is False:
            if self.bot.cli_login:
                await self.bot.get_user(self.bot.owner_id).send('You aren\'t currently logged into your Steam account'
                                                                '\nTo do that type in your 2FA code into the console.')
            await asyncio.sleep(60)
        await self.bot.get_user(self.bot.owner_id).send('I\'m online both Steam and Discord dealing with your Steam '
                                                        'messages')
        print('-' * 30)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, extension):
        """You probably don't need to use this, however it can be used to reload a cog

        eg. `!reload loader`"""
        if 'Cogs.' not in extension:
            extension = 'Cogs.' + extension.lower()
        if '.py' in extension:
            extension = extension[:-3]
        if extension == 'Cogs.all':
            self.bot.initial_extensions = os.listdir(
                'Cogs')  # getting the cog files in the "Cogs" folder and removing the none .py ones

            for extension in self.bot.initial_extensions:
                if extension.endswith('.py'):
                    try:
                        self.bot.reload_extension(f'Cogs.{extension[:-3]}')
                    except Exception as e:
                        await ctx.send(
                            f'**`ERROR:`** {ctx.message.author.display_name}, `{extension}` `{type(e).__name__}` - {e} hasn\'t been loaded')
                        print(f'Failed to load extension {extension}.', file=stderr)
                        traceback.print_exc()
                    else:
                        await ctx.send(
                            f'**`SUCCESS`** {ctx.message.author.display_name}, `{extension}` has been reloaded')
            await ctx.send(f'Finished reloading these `{self.bot.initial_extensions}` cogs')
            return
        try:
            self.bot.reload_extension(extension)
        except commands.ExtensionNotLoaded as e:
            await ctx.send(
                f'**`ERROR:`** {ctx.message.author.display_name}, `{extension}` `{type(e).__name__}` - {e} hasn\'t been loaded')
            await ctx.send(f"I'm going to load it now.")
            try:
                self.bot.load_extension(extension)
            except Exception as e:
                await ctx.send(f'**`ERROR:`** `{type(e).__name__}` - {e}')
                print(f'Failed to load extension {extension}.', file=stderr)
                traceback.print_exc()
            raise
        else:
            await ctx.send(f'**`SUCCESS`** {ctx.message.author.display_name}, `{extension}` has been reloaded')

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Used to reset the bot

        This won't work use this if you use `cli_login`, try not to use this"""
        if self.bot.cli_login:
            await ctx.send('You really really shouldn\'t do this')
        else:
            open('trades.txt', 'w+').write(str(self.bot.trades))
            await ctx.send(f'**Restarting the bot** {ctx.author.mention}, don\'t use this often')
            os.execv(executable, ['python'] + argv)


def setup(bot):
    bot.add_cog(LoaderCog(bot))
