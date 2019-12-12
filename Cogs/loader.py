from asyncio import sleep
from datetime import datetime
from json import loads
from os import remove, execv
from sys import argv, executable

from discord import Activity, ActivityType
from discord.ext import commands


def __version__():
    return '1.3.2'


class Loader(commands.Cog):
    """This cog just stores all of your variables nothing particularly interesting and the commands to restart the
    bot"""

    def __init__(self, bot):
        """Setting all of your bot vars to be used by other cogs/commands"""
        self.bot = bot

        login = loads(open("Login details/sensitive details.json", "r").read())
        bot.username = login["Username"]
        bot.password = login["Password"]
        try:
            bot.secrets = {
                "identity_secret": login["Identity Secret"],
                "shared_secret": login["Shared Secret"]
            }
        except:
            pass

        preferences = loads(open('Login details/preferences.json', 'r').read())
        bot.bot64id = int(preferences["Bot's Steam ID"])
        bot.prefix = preferences["Command Prefix"]
        bot.color = int(preferences["Embed Colour"], 16)
        bot.templocation = preferences["Path to Temp"]

        bot.sbotresp = 0
        bot.usermessage = 0
        bot.logged_on = 0
        bot.togglepremium = 0
        bot.dsdone = 0
        bot.trades = 0

        bot.updatem = f'{bot.prefix}update name='
        bot.removem = f'{bot.prefix}remove item='
        bot.addm = f'{bot.prefix}add name='
        bot.currenttime = datetime.now().strftime("%H:%M")

    @commands.Cog.listener()
    async def on_ready(self):
        """Setting your status, printing your bot's id to send to me,
        seeing if the bot was restarted and stored your number of trades,
        finally checking if you are logged onto steam"""
        self.bot.owner = await self.bot.application_info()
        self.bot.owner = self.bot.owner.owner
        await self.bot.change_presence(
            activity=Activity(name=f'{self.bot.owner.name}\'s trades | V{__version__()}',
                              type=ActivityType.watching))
        print(f'{"-" * 30}\n{self.bot.user.name} is ready')
        print(
            f'Send this id: "{self.bot.user.id}" to Gobot1234 to add your bot to the server to use the custom emojis')
        print(f'This is: Version {__version__()}')
        while self.bot.logged_on is False:
            if self.bot.cli_login:
                await self.bot.owner.send('You aren\'t currently logged into your Steam account\nTo do that type in '
                                          'your 2FA code into the console.')
            await sleep(60)
        print('-' * 30)
        try:
            self.bot.trades = int(open('trades.txt', 'r').read())
            channel = self.bot.get_channel(int(open('channel.txt', 'r').read()))
            if channel is not None:
                m_count = 0
                async for m in channel.history(limit=25):
                    if m_count < 1:
                        if m.author == self.bot.user:
                            await m.delete()
                            m_count += 1
                    else:
                        break

                await channel.send('Finished restarting...', delete_after=10)
            remove('channel.txt')
            remove('trades.txt')
        except FileNotFoundError:
            pass
        await self.bot.owner.send('I\'m online both Steam and Discord dealing with your Steam messages')


    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Used to reset the bot

        This won't work use this if you use `cli_login`, try not to use this as it can lead to memory shortages
        due to not letting old processes die"""
        if self.bot.cli_login:
            await ctx.send('You really really shouldn\'t do this')
        else:
            open('channel.txt', 'w+').write(str(ctx.channel.id))
            open('trades.txt', 'w+').write(str(self.bot.trades))
            await ctx.send(f'**Restarting the bot** {ctx.author.mention}, don\'t use this often')
            execv(executable, ['python'] + argv)

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Log yourself out safely"""
        open('channel.txt', 'w+').write(str(ctx.channel.id))
        open('trades.txt', 'w+').write(str(self.bot.trades))
        await ctx.send('Logging out...')
        self.bot.client.logout()
        await self.bot.close()
        raise SystemExit


def setup(bot):
    bot.add_cog(Loader(bot))
