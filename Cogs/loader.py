from asyncio import sleep
from datetime import datetime
from os import remove

from discord import Activity, ActivityType
from discord.ext import commands, tasks

from Login_details import preferences, sensitive_details


__version__ = '1.5.3'
__author__ = 'Gobot1234#2435'


class Loader(commands.Cog):
    """This cog just stores all of your variables nothing
    particularly interesting and the commands to restart the bot"""

    def __init__(self, bot):
        """Setting all of your bot vars to be used by other cogs/commands"""
        self.bot = bot
        bot.bot64id = preferences.bots_steam_id
        bot.color = int(preferences.embed_colour, 16)
        bot.files = preferences.files
        bot.prefix = preferences.command_prefix

        bot.sbotresp = 0
        bot.user_message = 0
        bot.logged_on = 0
        bot.dsdone = 0

        bot.updatem = f'{bot.prefix}update name='
        bot.removem = f'{bot.prefix}remove name='
        bot.addm = f'{bot.prefix}add name='
        bot.currenttime = datetime.now().strftime("%d-%m-%Y %H:%M")
        bot.first = True

    def cog_unload(self):
        self.check_if_logged_in.cancel()

    async def async__init__(self):
        """Setting your status, printing your bot's id to send to me,
        seeing if the bot was restarted and stored your number of trades,
        finally checking if you are logged onto steam"""
        if self.bot.first:
            self.bot.owner = (await self.bot.application_info()).owner
            self.bot.channel_live_trades = self.bot.get_channel(preferences.channel_id_live_trades) or self.bot.owner
            self.bot.channel_trades_statistic = self.bot.get_channel(preferences.channel_id_trades_statistic) or self.bot.owner
            self.bot.channel_offer_review = self.bot.get_channel(preferences.channel_id_offer_review) or self.bot.owner
            await self.bot.change_presence(activity=Activity(name=f'{self.bot.owner.name}\'s trades | V{__version__}',
                                                             type=ActivityType.watching))
            print('-' * 30, f'\n{self.bot.user.name} is ready')
            print(f'Send this id: "{self.bot.user.id}" to {__author__} '
                  f'to add your bot to the server to use the custom emojis')
            print(f'This is: Version {__version__}')
            while self.bot.logged_on is False:
                if self.bot.cli_login:
                    await self.bot.owner.send('You aren\'t currently logged into your Steam account\nTo do that type '
                                              'in your 2FA code into the console.')
                await sleep(60)
            print('-' * 30)
            try:
                channel = self.bot.get_channel(int(open('channel.txt', 'r').read()))
                if channel is not None:
                    async for m in channel.history(limit=2):
                        if m.author == self.bot.user:
                            await m.delete()
                    await channel.send('Finished restarting...', delete_after=10)
                remove('channel.txt')
            except FileNotFoundError:
                pass
            await sleep(60)

    @tasks.loop(minutes=30)
    async def check_if_logged_in(self):
        if not self.bot.client.logged_on:
            self.bot.log.info('Automatically restarting as I have been logged out of Steam')
            self.bot.client = None
            await self.bot.session.close()
            await self.bot.close()
            raise SystemExit

    @commands.Cog.listener()
    async def on_ready(self):
        await self.async__init__()

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        """Logout the bot safely"""
        await ctx.send('Logging out...')
        self.bot.client.logout()
        open('channel.txt', 'w+').write(str(ctx.channel.id))
        self.bot.client = None
        await self.bot.session.close()
        await self.bot.close()
        raise SystemExit


def setup(bot):
    bot.add_cog(Loader(bot))
