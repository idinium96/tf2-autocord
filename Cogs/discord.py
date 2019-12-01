import os
from asyncio import sleep
from aiohttp import ClientSession
from datetime import datetime
from json import load, dump
from os import remove, getcwd
from platform import python_version
from psutil import virtual_memory, cpu_percent
from steam import __version__ as s_version
from subprocess import getoutput

from discord import Embed, File, __version__ as d_version, errors
from discord.ext import commands, tasks

from .loader import Loader
import matplotlib.pyplot as plt


class Discord(commands.Cog):
    """Commands that are mostly help commands but more useful"""

    def __init__(self, bot):
        self.bot = bot
        self.profitgraphing.start()
        self.acceptedfiles = ('history', 'history.json', 'inventory', 'inventory.json', 'schema', 'schema.json',
                              'listings', 'listings.json')
        self.location = '/Login details/graph.png'

    async def gen_graph(self, points: int = None):
        data = load(open('Login details/profit_graphing.json', 'r'))
        if points is None:
            points = len(data)
        ignored = len(data) - points
        date_values = []
        tot_values = []
        tod_values = []
        pred_values = []

        for key in list(data.keys())[ignored:]:
            date_values.append(key)

        for value in list(data.values())[ignored:]:  # Plot the x values
            tod_values.append(float(value[0]))
            tot_values.append(float(value[1]))
            try:
                pred_values.append(float(value[2]))
            except IndexError:
                pred_values.append(0)

        # Plot the number in the list and set the line thickness.
        plt.close()
        plt.setp(plt.plot(date_values, tod_values, linewidth=3), color='blue')
        plt.setp(plt.plot(date_values, tot_values, linewidth=3), color='orange')
        plt.setp(plt.plot(date_values, pred_values, linewidth=3), color='green')

        plt.title(f'A graph to show your bot\'s profit over the last {points} days', fontsize=16)
        plt.xlabel("Date", fontsize=10)
        plt.ylabel("Keys", fontsize=10)
        plt.tick_params(axis='x', labelsize=8, rotation=90)
        plt.gca().legend(('Days profit', 'Total profit', 'Projected profit'))
        plt.tight_layout(h_pad=20, w_pad=20)
        plt.savefig(self.location)

    async def get_uptime(self):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return f'`{days}d, {hours}h, {minutes}m, {seconds}s`'

    @tasks.loop(seconds=5)
    async def profitgraphing(self):
        """A task that at 23:59 will get your profit
        It will convert all your values to keys"""
        self.bot.currenttime = str(datetime.now().strftime("%H:%M"))
        if self.bot.currenttime == '23:59':
            date = datetime.today().strftime("%d-%m-%Y")
            self.bot.client.s_bot.send_message(f'{self.bot.prefix}profit')
            await sleep(2)
            async with ClientSession() as session:
                async with session.get('https://api.prices.tf/items/5021;6?src=bptf') as response:
                    response = await response.json()
                    keyValue = response["sell"]["metal"]

            log = self.bot.graphplots.replace("You've made ", '')
            log = log.replace(' if all items were sold).', '') if 'all' in log else log[:-1]
            todprofit = log.split(' today')
            fixedtodprofit = todprofit[0]

            totprofit = str(todprofit[1]).replace(']', '').replace('[', '')
            if '(' in log:  # checks your total profit and if you have total profit
                totprofit = totprofit[2:-5].split(' in total')
            else:
                totprofit = totprofit[2:].split(' in total')
            if 'key' in fixedtodprofit or 'keys' in fixedtodprofit:  # converts 1st value to keys
                fixedtodprofit = fixedtodprofit.split(' ')
                minus = '-' if '-' in fixedtodprofit[0] else '-'

                fixedtodprofit = round(float(fixedtodprofit[0]) + float(minus + fixedtodprofit[2]) / keyValue, 2)

            else:
                fixedtodprofit = fixedtodprofit.split(' ')
                fixedtodprofit = round(float(fixedtodprofit[0]) / keyValue, 2)

            if 'key' in totprofit[0] or 'keys' in totprofit[0]:  # converting 2nd
                fixedtotprofit = totprofit[0].split(', ')
                if 'keys' in fixedtotprofit[0]:
                    fixedtotprofit[0] = fixedtotprofit[0][:-5]
                elif 'key' in fixedtotprofit[0]:
                    fixedtotprofit[0] = fixedtotprofit[0][:-3]
                fixedtotprofit[1] = fixedtotprofit[1][:-4]

                fixedtotprofit = round(float(fixedtotprofit[0]) + float(fixedtotprofit[1]) / keyValue, 2)
            else:
                fixedtotprofit = totprofit[0].split(', ')
                fixedtotprofit = round(float(fixedtotprofit[0][:-4]) / keyValue, 2)
            if 'more' in str(log):  # checks if you have predicted profit
                predprofit = str(totprofit[1]).replace(' (', '').replace('[', '').replace(']', '').replace("'",
                                                                                                           '')
                fixedpredprofit = predprofit.split(', ')
                if 'keys' in fixedpredprofit[0]:
                    fixedpredprofit[0] = fixedpredprofit[0][:-5]
                elif 'key' in fixedpredprofit[0]:
                    fixedpredprofit[0] = fixedpredprofit[0][:-3]
                elif 'ref' in fixedpredprofit[0]:
                    fixedpredprofit[0] = fixedpredprofit[0][:-4]
                try:
                    if 'ref' in fixedpredprofit[1]:
                        fixedpredprofit[1] = fixedpredprofit[1][:-4]
                except:
                    pass

                try:
                    fixedpredprofit = round(float(fixedpredprofit[0]) + float(fixedpredprofit[1]) / keyValue, 2)
                except:
                    fixedpredprofit = round(float(fixedpredprofit[0]) / keyValue, 2)

                graphdata = [fixedtodprofit, fixedtotprofit, fixedpredprofit, self.bot.trades]
            else:
                graphdata = [fixedtodprofit, fixedtotprofit, self.bot.trades]

            tempprofit = {date: graphdata}
            with open('Login details\profit_graphing.json') as f:
                data = load(f)
                data.update(tempprofit)
            with open('Login details\profit_graphing.json', 'w') as f:
                dump(data, f, indent=4)

    @commands.command()
    @commands.is_owner()
    async def last(self, ctx, days: int = 0):
        """Used to get the last x days profit

        eg. `!last 7` (days has to be an integer)"""
        async with ctx.typing():
            data = load(open('Login details/profit_graphing.json', 'r'))
            if days > len(data) or days == 0:
                days = len(data)

            await self.gen_graph(days)
            file = File(self.location, filename="graph.png")

            embed = Embed(title=f'Last {days} days profit', color=self.bot.color)
            embed.set_image(url='attachment://graph.png')
            for key, value in reversed(list(data.items())[len(data) - days:]):
                try:
                    embed.add_field(name=f'__**{key}:**__',
                                    value=f'Days profit **{value[0]}** keys. Total profit **{value[1]}** keys. '
                                          f'Predicted profit **{value[2]}** keys. Total trades **{value[3]}**',
                                    inline=False)
                except:
                    pass

            if len(embed) <= 6000:
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(f'Please try fewer days as the embed is too large to send, if you want the graph use the {self.bot.prefix}graph command')
            remove(self.location)

    @commands.command()
    @commands.is_owner()
    async def graph(self, ctx, points: int = None):
        """Used to generate a graph of all of your profit whilst using the bot"""
        async with ctx.typing():
            await self.gen_graph(points)
            file = File(self.location, filename="graph.png")
            await ctx.send('Here is your graph:', file=file)
        remove(self.location)

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

        eg. `!get history` (if you don't type anything you can see the files you can request)"""
        if file is None:
            return await ctx.send(f'You can request these files `{self.acceptedfiles}`')
        file = file.lower()
        if file in self.acceptedfiles:
            file = f'/{file}'
            if '.json' in file:
                filename = file
                file = f'{self.bot.templocation}{file}'
            elif '.json' not in file:
                filename = f'{file}.json'
                file = f'{self.bot.templocation}{file}.json'
            file = File(file, filename=filename)
            await ctx.send('Here you go, don\'t do anything naughty with it.', file=file)
        else:
            await ctx.send('I\'m sorry you can request that file')

    @commands.command(aliases=['about', 'stats', 'status'])
    async def info(self, ctx):
        """Get some interesting info about the bot"""
        rawram = virtual_memory()
        updateable = getoutput(f'git checkout {getcwd()}')
        if 'Your branch is up to date with' in updateable:
            emoji = '<:tick:626829044134182923>'
        elif 'not a git repository' in updateable:
            emoji = ('This wasn\'t cloned from GitHub')
        else:
            emoji = '<:goodcross:626829085682827266>'
        uptime = await self.get_uptime()
        embed = Embed(title="**tf2-autocord:** Developer - Gobot1234", colour=self.bot.color)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Commands loaded & Cogs loaded",
                        value=f'`{(len([x for x in self.bot.commands]))}` commands loaded, `{len([x for x in self.bot.cogs])}` cogs loaded :gear:',
                        inline=True)
        embed.add_field(name="<:compram:622622385182474254> RAM Usage",
                        value=f'`{round(rawram[3] / 1024 ** 2)}` MB used / `{round(rawram[0] / 1024 ** 2)}` MB total | `{rawram[2]}`% used',
                        inline=True)
        embed.add_field(name="<:cpu:622621524418887680> CPU Usage", value=f'`{cpu_percent()}`%', inline=True)
        embed.add_field(name=f'{self.bot.user.name} has been online for', value=uptime)
        embed.add_field(name='<:tf2autocord:624658299224326148> tf2-autocord Version',
                        value=f'Version: `{Loader.__version__}`. Up to date: {emoji}')
        embed.add_field(name=':exclamation:Command prefix',
                        value=f"Your command prefix is `{self.bot.prefix}`. "
                              f"Type {self.bot.prefix}help to list the commands you can use",
                        inline=False)
        embed.add_field(name='<:tf2automatic:624658370447671297> About the bot',
                        value='It was coded in Python to help you manage your tf2automtic bot. DM me with any '
                              'suggestions or features you would like on this bot', inline=False)
        embed.add_field(name='<:dpy:622794044547792926> Discord.py Version',
                        value=f'`{d_version}` works with versions 1.1+ of Discord.py and versions 3.5.4+ of Python',
                        inline=True)
        embed.add_field(name='<:python:622621989474926622> Python Version',
                        value=f'`{python_version()}` works with versions 3.6+ (uses f-strings)',
                        inline=True)
        embed.add_field(name='<:steam:622621553800249364> Steam Version',
                        value=f'`{s_version}` works with versions 3.4+ of Python',
                        inline=True)
        embed.add_field(name='Join the help server :hugging:', value='[Here](https://discord.gg/S3eVmxD)')
        embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435",
                         icon_url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.webp?size=1024')
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """See how long the bot has been online for"""
        uptime = await self.get_uptime()
        await ctx.send(f'{self.bot.user.mention} has been online for {uptime}')


def setup(bot):
    bot.add_cog(Discord(bot))


def teardown():
    Discord.profitgraphing.stop()
