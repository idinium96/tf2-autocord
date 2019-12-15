from asyncio import sleep
from aiohttp import ClientSession
from datetime import datetime
from humanize import naturalsize
from json import load, dump
from os import remove, getcwd
from platform import python_version
from psutil import Process, virtual_memory, cpu_percent
from steam import __version__ as s_version
from subprocess import getoutput
from re import search

from discord import Embed, File, __version__ as d_version, errors, HTTPException
from discord.ext import commands, tasks

from .loader import __version__ as l_version
import matplotlib.pyplot as plt


class Discord(commands.Cog):
    """Commands that are mostly help commands but more useful"""

    def __init__(self, bot):
        self.bot = bot
        self.location = 'Login_details\\graph.png'
        self.profitgraphing.start()
        self.process = Process()
        self.acceptedfiles = ('history', 'history.json', 'inventory', 'inventory.json', 'schema', 'schema.json',
                              'listings', 'listings.json')

    async def cog_unload(self):
        self.profitgraphing.cancel()

    def gen_graph(self, points: int = None):
        data = load(open('Login_details/profit_graphing.json', 'r'))
        if points is None:
            points = len(data)
        ignored = len(data) - points
        date_values = [date for date in list(data.keys())[ignored:]]  # plot x values
        tot_values = [float(value[0]) for value in list(data.values())[ignored:]]  # plot the y values
        tod_values = [float(value[1]) for value in list(data.values())[ignored:]]
        pre_values = [float(value[2]) for value in list(data.values())[ignored:]]

        # plot the number in the list and set the line thickness.
        plt.close()  # close the old session
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
    async def profitgraphing(self):
        """A task that at 23:59 will get your profit
        It will convert all your values to keys"""
        self.bot.current_time = datetime.now().strftime("%d-%m-%Y %H:%M")
        if self.bot.current_time.split()[1] == '23:59':
            self.bot.s_bot.send_message(f'{self.bot.prefix}profit')
            await sleep(2)
            async with ClientSession() as session:
                async with session.get('https://api.prices.tf/items/5021;6?src=bptf') as response:
                    response = await response.json()
                    key_value = response["sell"]["metal"]

            tod_profit = search(r'(made (.*?) today)', self.bot.graphplots).group(1)[5:-6]
            tot_profit = search(r'(today, (.*?) in)', self.bot.graphplots).group(1)[7:-3]
            try:
                pred_profit = search(r'(\((.*?) more)', self.bot.graphplots).group(1)[1:-5]
            except:
                pred_profit = 0

            fixed = []
            for to_fix in [tod_profit, tot_profit, pred_profit]:
                if to_fix == 0:
                    total = 0
                elif ', ' in to_fix:
                    to_fix = to_fix.split(', ')
                    keys = int(to_fix[0][:-5]) if 'keys' in to_fix[0] else int(to_fix[0][:-4])
                    multiplier = -1 if keys < 0 else 1
                    ref = multiplier * float(to_fix[1][:-4])
                    ref_keys = round(ref / key_value, 2)
                    total = keys + ref_keys
                else:
                    ref = float(tod_profit[:-4])
                    total = round(ref / key_value, 2)
                fixed.append(total)

            tod_profit, tot_profit, pred_profit = fixed
            graphdata = [tod_profit, tot_profit, pred_profit, self.bot.trades]
            tempprofit = {self.bot.current_time.split()[0]: graphdata}
            data = load(open('Login_details\\profit_graphing.json'))
            data.update(tempprofit)
            dump(data, open('Login_details\\profit_graphing.json', 'w'), indent=4)
            await sleep(120)

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
            self.gen_graph(days)
            embed = Embed(title=f'Last {days} days profit', color=self.bot.color)
            embed.set_image(url='attachment://graph.png')
            for date, value in reversed(list(data.items())[ignored:]):
                try:
                    embed.add_field(name=f'__**{date}:**__',
                                    value=f'Days profit **{value[0]}** keys. Total profit **{value[1]}** keys. '
                                          f'Predicted profit **{value[2]}** keys. Total trades **{value[3]}**',
                                    inline=False)
                except IndexError:
                    pass
            f = File(self.location, filename="graph.png")
            try:
                await ctx.send(embed=embed, file=f)
            except HTTPException:
                await ctx.send(f'Please try fewer days as the embed is too large to send, '
                               f'if you want the graph use the {self.bot.prefix}graph command')

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
            self.gen_graph(points)
            embed = Embed(title=f'Last {points} days profit', color=self.bot.color)
            embed.set_image(url='attachment://graph.png')
            f = File(self.location, filename="graph.png")
            await ctx.send(embed=embed, file=f)

    @commands.command()
    @commands.is_owner()
    async def acknowledged(self, ctx):
        """Used to acknowledge a user message

        This is so user messages don't get lost in the channel history"""
        self.bot.usermessage = 0
        try:
            await self.bot.message.unpin()
        except errors.Forbidden:
            pass
        await ctx.send('Acknowledged the user\'s message')

    @commands.command(aliases=['gimme'])
    @commands.is_owner()
    async def get(self, ctx, *, file=None):
        """Used to get files from your temp folder

        eg. `{prefix}get history` (if you don't type anything you can see the files you can request)"""
        if file is None:
            return await ctx.send(f'You can request these files `{self.acceptedfiles}`')
        file = file.lower()
        if file in self.acceptedfiles:
            file = f'/{file}'
            if '.json' in file:
                filename = file
                file = f'{self.bot.templocation}{file}'
            else:
                filename = f'{file}.json'
                file = f'{self.bot.templocation}{file}.json'
            file = File(file, filename=filename)
            await ctx.send('Here you go, don\'t do anything naughty with it.', file=file)
        else:
            await ctx.send('I\'m sorry you can request that file')

    @commands.command()
    async def classifieds(self, ctx):
        """Check your number of listings and get a easy read version of them in a text file"""
        file = load(open(f'{self.bot.templocation}/listings.json', 'r'))
        listings = '\n'.join([listing['name'] for listing in file])
        open('listings.txt', 'w+').write(listings)
        f = File("listings.txt", filename="listings.txt")
        remove('listings.txt')
        await ctx.send(f'You have {len(file)} listings, view them here:', file=f)

    @commands.command(aliases=['about', 'stats', 'status'])
    async def info(self, ctx):
        """Get some interesting info about the bot"""
        uptime = await self.get_uptime()
        memory_usage = self.process.memory_full_info().uss
        rawram = virtual_memory()
        updateable = getoutput(f'git checkout {getcwd()}')

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
                        value=f'Using `{naturalsize(rawram[3])}` / `{naturalsize(rawram[0])}` `{round(rawram[3] / rawram[0] * 100, 2)}`% '
                              f'of your physical memory and `{naturalsize(memory_usage)}` of which unique to this process.')
        embed.add_field(name="<:cpu:622621524418887680> CPU Usage", value=f'`{cpu_percent()}`% used')
        embed.add_field(name=f'{self.bot.user.name} has been online for:', value=uptime)
        embed.add_field(name='<:tf2autocord:624658299224326148> tf2-autocord Version',
                        value=f'Version: `{l_version()}`. Up to date: {emoji}')
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


def setup(bot):
    bot.add_cog(Discord(bot))
