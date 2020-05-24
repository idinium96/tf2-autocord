from asyncio import sleep
from datetime import datetime
from json import load, dump
from math import floor
from os import remove
from platform import python_version
from subprocess import getoutput
from re import search

import ago
import matplotlib.pyplot as plt
from discord import Embed, File, __version__ as d_version
from discord.ext import commands, tasks, buttons
from humanize import naturalsize
from psutil import virtual_memory, cpu_percent
from steam import __version__ as s_version

from .loader import __version__ as l_version


class Discord(commands.Cog):
    """Commands that are mostly help commands but more useful"""

    def __init__(self, bot):
        self.bot = bot
        self.location = 'Login_details\\graph.png'
        self.accepted_files = ('pricelist', 'pricelist.json', 'polldata', 'polldata.json')

        self.statsAndpolldata.start()

    def cog_unload(self):
        self.statsAndpolldata.cancel()

    def gen_graph(self, points: int = None):
        plt.close()  # close the old session
        data = load(open('Login_details/profit_graphing.json', 'r'))
        if points is None:
            points = len(data)
        ignored = len(data) - points
        date_values = [date for date in list(data.keys())[ignored:]]  # plot x values
        tot_values = [float(value[0]) for value in list(data.values())[ignored:]]  # plot the y values
        tod_values = [float(value[1]) for value in list(data.values())[ignored:]]
        pre_values = [float(value[2]) for value in list(data.values())[ignored:]]

        # plot the number in the list and set the line thickness.
        plt.setp(plt.plot(date_values, tod_values, linewidth=3), color='blue')
        plt.setp(plt.plot(date_values, tot_values, linewidth=3), color='orange')
        plt.setp(plt.plot(date_values, pre_values, linewidth=3), color='green')

        plt.title(f'A graph to show your bot\'s profit over the last {points} days', fontsize=16)
        plt.xlabel('Date', fontsize=10)
        plt.ylabel('Keys', fontsize=10)
        plt.tick_params(axis='x', labelsize=8, rotation=90)
        plt.gca().legend(('Days profit', 'Total profit', 'Projected profit'))
        plt.tight_layout(h_pad=20, w_pad=20)
        plt.savefig(self.location, format='png')

    async def get_uptime(self):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return f'`{days}d, {hours}h, {minutes}m, {seconds}s`'

    @tasks.loop(seconds=20)
    async def statsAndpolldata(self):
    # pylint: disable=unbalanced-tuple-unpacking
        """A task that at every 6 hours UTC will get trade statistic and
        send the polldata.json file as backup every 00:01 UTC"""
        self.bot.current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
        if self.bot.current_time.split()[1] in ['23:59', '05:59', '11:59', '17:59']:
            self.bot.s_bot.send_message(f'{self.bot.prefix}stats')
            await sleep(60)

    @commands.command()
    @commands.is_owner()
    async def last(self, ctx, days: int = None):
        """Used to get the last x days profit

        eg. `{prefix}last 7` (days has to be an integer)"""
        async with ctx.typing():
            data = load(open('Login_details/profit_graphing.json', 'r'))
            if days is None or days > len(data):
                days = len(data)
            ignored = len(data) - days
            await self.bot.loop.run_in_executor(None, self.gen_graph, days)

            last = buttons.Paginator(title=f'Last {days} days profit', colour=self.bot.color, embed=True, timeout=90,
                                     use_defaults=True, length=10,
                                     entries=[f'__**{date}**__ - Days profit **{value[0]}** keys. Total profit '
                                              f'**{value[1]}** keys. Predicted profit **{value[2]}** keys. '
                                              f'Total trades **{value[3]}**' for date, value in
                                              reversed(list(data.items())[ignored:])])

            await last.start(ctx)
            f = File(self.location, filename="graph.png")
            await ctx.send(file=f)

    @commands.command()
    @commands.is_owner()
    async def graph(self, ctx, points: int = 0):
        """Used to generate a graph of all of your profit whilst using the bot"""
        async with ctx.typing():
            len_points = len(load(open('Login_details/profit_graphing.json', 'r')))
            if points == 0 or points > len_points:
                points = len_points
            if points <= 1:
                points = 3
            await self.bot.loop.run_in_executor(None, self.gen_graph, points)
            embed = Embed(title=f'Last {points} days profit', color=self.bot.color)
            embed.set_image(url='attachment://graph.png')
            f = File(self.location, filename="graph.png")
            await ctx.send(embed=embed, file=f)

    @commands.command(aliases=['gimme'])
    @commands.is_owner()
    async def get(self, ctx, *, file=None):
        """Used to get files from your temp folder

        eg. `{prefix}get history` (if you don't type anything you can see the files you can request)"""
        if file is None:
            return await ctx.send(f'You can request these files `{self.accepted_files}`')
        file = file.lower()
        if file in self.accepted_files:
            file = f'/{file}'
            if '.json' in file:
                filename = file
                file = f'{self.bot.files}{file}'
            else:
                filename = f'{file}.json'
                file = f'{self.bot.files}{file}.json'
            file = File(file, filename=filename)
            await ctx.send('Here you go, don\'t do anything naughty with it.', file=file)
        else:
            await ctx.send('I\'m sorry you can request that file')

    @commands.command()
    async def classifieds(self, ctx):
        """Check your number of listings and get a easy read version of them in a text file"""
        file = load(open(f'{self.bot.files}/pricelist.json', 'r'))
        listings = '\n'.join([listing['sku'] for listing in file])
        open('listings.txt', 'w+').write(listings)
        f = File("listings.txt", filename="listings.txt")
        await ctx.send(f'You have {len(file)} listings, view them here:', file=f)
        await sleep(10)
        remove('listings.txt')

    @commands.command(aliases=['about', 'stats', 'status'])
    async def info(self, ctx):
        """Get some interesting info about the bot"""
        uptime = await self.get_uptime()
        rawram = virtual_memory()
        updateable = await self.bot.loop.run_in_executor(None, getoutput, f'git checkout Public')

        if 'Your branch is up to date with' in updateable:
            emoji = '<:tick:626829044134182923>'
        elif 'not a git repository' in updateable:
            emoji = 'This wasn\'t cloned from GitHub'
        else:
            emoji = '<:goodcross:626829085682827266>'

        embed = Embed(title="**tf2-autocord:** - System information",
                      description=f'Commands loaded & Cogs loaded: `{len(self.bot.commands)}` commands loaded, '
                                  f'`{len(self.bot.cogs)}` cogs loaded :gear:', colour=self.bot.color)
        embed.add_field(name="<:compram:622622385182474254> RAM Usage",
                        value=f'Using `{naturalsize(rawram[3])}` / `{naturalsize(rawram[0])}` `{round(rawram[3] / rawram[0] * 100, 2)}`%')
        embed.add_field(name="<:cpu:622621524418887680> CPU Usage", value=f'`{cpu_percent()}`% used')
        embed.add_field(name=f'{self.bot.user.name} has been online for:', value=uptime)
        embed.add_field(name='<:tf2autocord:624658299224326148> tf2-autocord Version',
                        value=f'Version: `{l_version}`. Up to date: {emoji}')
        embed.add_field(name=':exclamation:Command prefix',
                        value=f'Your command prefix is `{self.bot.prefix}`. Type {self.bot.prefix}help to list the '
                              f'commands you can use')
        embed.add_field(name='<:tf2automatic:624658370447671297> About the bot',
                        value='It was coded in Python to help you manage your tf2automtic bot. DM me with any '
                              'suggestions or features you would like on this bot', inline=False)
        embed.add_field(name='<:dpy:622794044547792926> Discord.py Version',
                        value=f'`{d_version}` works with versions 1.1+ of Discord.py and versions 3.5.4+ of Python')
        embed.add_field(name='<:python:622621989474926622> Python Version',
                        value=f'`{python_version()}` works with versions 3.6+ (uses f-strings)')
        embed.add_field(name='<:steam:622621553800249364> Steam Version',
                        value=f'`{s_version}` works with versions 3.4+ of Python')
        embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435",
                         icon_url='https://cdn.discordapp.com/avatars/340869611903909888/9e3719ecc71ebfb3612ceccf02da4c7a.webp?size=1024')
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """See how long the bot has been online for"""
        uptime = await self.get_uptime()
        await ctx.send(f'{self.bot.user.mention} has been online for {uptime}')

    def unix_parse(self, time):
        return datetime.utcfromtimestamp(time)

    @commands.command()
    async def history(self, ctx, days: int = 30):
        _sorted = {}
        file = load(open(f'{self.bot.files}/history.json', 'r'))
        try:
            black_list = open('Login_details/blacklist', 'r').read().splitlines()
        except FileNotFoundError:
            black_list = []

        for trade in file.values():
            try:
                if trade['time_sold'] + 60 * 60 * 24 * days > datetime.utcnow().timestamp():
                    if trade['time_sold'] and trade['name'] not in black_list:
                        profit = trade['bought'] - trade['sold']

                        human_time_to_sell = ago.human(
                            self.unix_parse(trade['time_bought']) - self.unix_parse(trade['time_sold']))
                        _sorted[profit] = [trade['name'], human_time_to_sell]
            except KeyError:
                pass
        checker = buttons.Paginator(title='History checker', colour=self.bot.color, embed=True, timeout=90, use_defaults=True,
                                    entries=[f'**{index}.** {trade[1][0]}, was sold {trade[1][1]} for '
                                             f'{floor((trade[0] / 9) * 100) / 100 if trade[0] > 0 else -1 * floor(abs(trade[0]) / 9 * 100) / 100} '
                                             f'ref {"profit" if trade[0] > 0 else "loss"}' for index, trade in
                                             enumerate(sorted(_sorted.items(), reverse=True), start=1)], length=10)
        await checker.start(ctx)


def setup(bot):
    bot.add_cog(Discord(bot))
