import discord
from discord.ext import commands

import asyncio
import json
import os

from sys import argv, executable
from datetime import datetime


class LoaderCog(commands.Cog, name='Loader'):
    """This cog just stores all of your variables nothing particularly interesting and a few commands for development"""
    __version__ = '1.2'

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
        bot.botresp = False
        bot.beginSteam = False
        bot.dsdone = 0
        bot.currenttime = datetime.now().strftime("%H:%M")

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
        await asyncio.sleep(15)

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
        try:
            self.bot.reload_extension(extension)
            await ctx.send(f'{ctx.message.author.display_name}, `{extension}` has been reloaded')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'{ctx.message.author.display_name}, `{extension}` hasn\'t been loaded')
            await ctx.send(f"I'm going to load it now.")
            self.bot.load_extension(extension)
            raise

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Used to reset the bot

        This won't work use this if you use `cli_login`, try not to use this"""
        if self.bot.cli_login:
            await ctx.send('You really really shouldn\'t do this')
        else:
            await ctx.send('**Restarting the bot**, don\'t use this often')
            os.execv(executable, ['python'] + argv)


def setup(bot):
    bot.add_cog(LoaderCog(bot))
