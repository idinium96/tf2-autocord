import discord
from discord.ext import commands
import json
import asyncio

with open('Login details/preferences.json', 'r') as f:
    preferences = f.read()
    preferences = json.loads(preferences)
    owner_id = int(preferences["Discord ID"])
    bot64id = int(preferences["Bot's Steam ID"])
    owner_name = preferences["Owner Name"]
    command_prefix = preferences["Command Prefix"]
    color = int(preferences["Embed Colour"], 16)
    templocation = preferences["Path to Temp"]

acceptedfiles = ['history', 'history.json', 'inventory', 'inventory.json', 'schema', 'schema.json', 'listings',
                 'listings.json']


def is_owner(ctx):
    return ctx.message.author.id == owner_id


class DiscordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_owner)
    async def acknowledged(self, ctx):
        global usermessage
        usermessage = 0
        await ctx.send('Acknowledged the user\'s message')

    @commands.command()
    @commands.check(is_owner)
    async def togpremium(self, ctx):
        global togglepremium
        if togglepremium == 0:
            togglepremium = 1
            await ctx.send(
                'Premium Alerts now toggled on (this will send you a message when 1 months and 29 days have gone past)')
        elif togglepremium == 1:
            togglepremium = 0
            await ctx.send('Premium Alerts now toggled off')

        while togglepremium == 1:
            await asyncio.sleep(4654687)  # 2 months in seconds - 1 day = 4654687 seconds
            await ctx.send('You may wish to renew your premium subscription')

    @commands.command()
    @commands.check(is_owner)
    async def donate(self, ctx):
        embed = discord.Embed(title=' ', color=0x2e3bad)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.png?size=1024')
        embed.add_field(name='Want to donate?',
                        value='https://steamcommunity.com/tradeoffer/new/?partner=287788226&token=NBewyDB2')
        embed.set_footer(text='Thank you for any donations')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_owner)
    async def get(self, ctx, *, file: str):
        file = file.lower()
        if file in acceptedfiles:
            file = '/' + file
            if '.json' in file:
                filename = file
                file = templocation + file
            elif '.json' not in file:
                filename = file + '.json'
                file = templocation + file + '.json'
            file = discord.File(file, filename=filename)
            await ctx.send('Here you go, don\'t do anything naughty with it.', file=file)
        else:
            await ctx.send('I\'m sorry you can request that file')


def setup(bot):
    bot.add_cog(DiscordCog(bot))
