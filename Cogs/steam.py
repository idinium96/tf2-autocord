import asyncio
from datetime import datetime

import discord
import json

from discord.ext import commands, tasks
from os import remove
from typing import Optional


class SteamCog(commands.Cog, name='Steam'):
    """Commands that are mainly owner restricted and only work if you are logged in to your steam account"""

    def __init__(self, bot):
        self.bot = bot
        self.discordcheck.start()
        self.bot.trades = 0

    def check(self, m):
        return m.content and m.author.id == self.bot.owner_id

    async def classifieds(self, ctx, name, ctype):
        if ctype == 'list':
            mul = 'these'
            mul2 = 'commands'
            dscontent = str(name).replace('[', '`').replace(']', '`').replace(', ', '`, `')
        elif ctype == 'str':
            mul = 'this'
            mul2 = 'command'
            dscontent = f'`{name}`'
        await ctx.send(f'Do you want to send {mul} {dscontent} {mul2} to the bot?')
        while 1:
            choice = await self.bot.wait_for('message', check=self.check)
            choice = choice.clean_content.lower()

            if choice == 'y' or choice == 'yes':
                await ctx.send(f'Sent {mul} {mul2} to the bot {dscontent}')
                async with ctx.typing():
                    if ctype == 'list':
                        for message in name:
                            self.bot.client.get_user(self.bot.bot64id).send_message(message)
                            await asyncio.sleep(5)

                    if ctype == 'str':
                        self.bot.client.get_user(self.bot.bot64id).send_message(name)
                        await asyncio.sleep(3)
                break

            elif choice == 'n' or choice == 'no':
                await ctx.send('The command hasn\'t been sent')
                break
            else:
                await ctx.send('Try Again')

    @tasks.loop(seconds=3)
    async def discordcheck(self):
        """The task that forwards messages from Steam to Discord"""
        if self.bot.sbotresp != 0:
            if 'Received offer' in self.bot.sbotresp:
                self.bot.trades += 1
            if 'accepted' in self.bot.sbotresp:
                color2 = 0x5C7E10
            elif 'declined' in self.bot.sbotresp or 'canceled' in self.bot.sbotresp or 'invaliditems' in self.bot.sbotresp:
                color2 = discord.Color.red()
            else:
                color2 = self.bot.color

            if 'view it here' in self.bot.sbotresp and 'https' in self.bot.sbotresp:
                image = self.bot.sbotresp.split('here ', 1)
                message = self.bot.sbotresp.replace(image[1], '')[:-1] + ':'
                image = image[1]
                embed = discord.Embed(color=color2)
                embed.add_field(name='Trade: ', value=message, inline=False)
                embed.set_image(url=image)
            else:
                embed = discord.Embed(color=color2)
                embed.add_field(name='New Message:', value=self.bot.sbotresp, inline=False)

            embed.set_footer(text=datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
                             icon_url=self.bot.user.avatar_url)
            await self.bot.get_user(self.bot.owner_id).send(embed=embed)
            if self.bot.usermessage != 0:
                embed = discord.Embed(color=0xFFFF66)
                embed.add_field(name='User Message:',
                                value=f'You have a message from a user:\n{self.bot.usermessage}'
                                      f'\nType {self.bot.command_prefix}acknowledged',
                                inline=False)
                await self.bot.get_user(self.bot.owner_id).send(embed=embed)
                await asyncio.sleep(60)
            self.bot.sbotresp = 0

    @commands.is_owner()
    @commands.command(aliases=['reconnect', 'logged_on', 'online'])
    async def relogin(self, ctx):
        """Attempt to reconnect to Steam if you logged out"""
        if self.bot.client.logged_on:
            await ctx.send(f'You are already logged in as {self.bot.client.user.name}')
        else:
            await ctx.send("Reconnecting...")
            async with ctx.typing():
                if self.bot.client.relogin_available:
                    self.bot.client.reconnect(maxdelay=30)
                    await ctx.send('Reconnected to Steam')
                else:
                    await ctx.send('Try again later or restart the program')

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def add(self, ctx):
        """Add is used to add items from your bot's classifieds

        It allows the chaining of commands
        eg. `!add names This&intent=sell, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')

    @add.command(name='name')
    async def a_name(self, ctx, *, name):
        """Handles singular adds"""
        name = f'{self.bot.addm}{name}'
        await self.classifieds(ctx, name, ctype='str')

    @add.command(name='names')
    async def a_names(self, ctx, *, name):
        """Handles multiple adds"""
        name = name.split(',')
        name = [f'{self.bot.addm}{x.lstrip().rstrip()}' for x in name]
        await self.classifieds(ctx, name, ctype='list')

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def update(self, ctx):
        """Update is used to update items from your bot's classifieds

        It allows the chaining of commands
        eg. `!update names This&intent=bank, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')

    @update.command(name='name')
    async def u_name(self, ctx, *, name):
        """Handles singular updates"""
        name = f'{self.bot.updatem}{name}'
        await self.classifieds(ctx, name, ctype='str')

    @update.command(name='names')
    async def u_names(self, ctx, *, name):
        """Handles multiple updates"""
        name = name.split(',')
        name = [f'{self.bot.updatem}{x.lstrip().rstrip()}' for x in name]
        await self.classifieds(ctx, name, ctype='list')

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def remove(self, ctx):
        """Remove is used to remove items from your bot's classifieds

        It allows the chaining of commands
        eg. `!remove items This&intent=bank, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')

    @remove.command(name='item')
    async def r_name(self, ctx, *, name):
        """Handles singular removals"""
        name = f'{self.bot.removem}{name}'
        await self.classifieds(ctx, name, ctype='str')

    @remove.command(name='items')
    async def r_names(self, ctx, *, name):
        """Handles multiple removals"""
        name = name.split(',')
        name = [f'{self.bot.removem}{x.lstrip().rstrip()}' for x in name]
        await self.classifieds(ctx, name, ctype='list')

    @commands.command()
    @commands.is_owner()
    async def profit(self, ctx):
        """Returns your bot's profit as it normally would"""
        async with ctx.typing():
            self.bot.client.get_user(self.bot.bot64id).send_message(f'{self.bot.command_prefix}profit')
            await asyncio.sleep(3)

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, *, message):
        """Send is used to send a message to the bot

        eg. `!send !message 76561198248053954 Get on steam`"""
        async with ctx.typing():
            self.bot.client.get_user(self.bot.bot64id).send_message(message)
            await ctx.send(f"Sent `{message}` to the bot")
            await asyncio.sleep(3)

    @commands.command(aliases=['bp'])
    async def backpack(self, ctx):
        """Get a link to your inventory and your bot's"""
        embed = discord.Embed(title='\u200b', color=0x58788F)
        embed.set_thumbnail(url='https://steamuserimages-a.akamaihd.net/ugc'
                                '/44226880714734120/EE4DAE995040556E8013F583ACBA971846FA1E2B/')
        embed.add_field(name='Your backpack:', value=f'https://backpack.tf/profiles/{self.bot.client.user.steam_id}')
        embed.add_field(name='Your bot\'s backpack', value=f'https://backpack.tf/profiles/{self.bot.bot64id}')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def scc(self, ctx):
        """Scc is a worse version of Hackerino's command generator tool"""
        notgonethrough = True
        notgonethrough1 = True
        notgonethrough2 = True
        notgonethrough3 = True
        notgonethrough4 = True
        notgonethrough5 = True
        notgonethrough6 = True
        notgonethrough7 = True
        notgonethrough8 = True

        scclist = '\n__You can change the:__\nPrice\nLimit\nQuality\nIntent\nCraftable\nAustralium\n' \
                  'Killstreak\nEffect\nAutopricing'
        intents = 'Bank, Buy or Sell'
        qualities = 'Unique, Strange, Vintage, Genuine, Haunted or Collector\'s'

        await ctx.send('What do you want to do?\nUpdate, Remove or Add?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=self.check)
            choice = choice.clean_content.lower()

            if choice == 'update' or choice == 'u' or choice == 'add' or choice == 'a' or choice == 'remove' or choice == 'r':
                if choice == 'update' or choice == 'u':
                    do = 'update'
                elif choice == 'add' or choice == 'a':
                    do = 'add'
                elif choice == 'remove' or choice == 'r':
                    do = 'remove'
                await ctx.send(f'What item do you want to {do}?')
                item_to_uar = await self.bot.wait_for('message', check=self.check)
                item_to_uar = item_to_uar.clean_content
                steamcommand = item_to_uar

                if do == 'remove':
                    f'{self.bot.removem}{steamcommand}'
                else:
                    await ctx.send('Want to add prefixes?\nType yes or no')
                    response = 0
                    while response == 0:
                        choice = await self.bot.wait_for('message', check=self.check)
                        choice = choice.clean_content.lower()

                        if choice == 'yes' or choice == 'y':
                            await ctx.send(scclist)
                            while 1:
                                prefix = await self.bot.wait_for('message', check=self.check)
                                prefix = prefix.clean_content.lower()

                                if prefix == 'price' or prefix == 'p' and notgonethrough:  # buy price prefix
                                    await ctx.send('Buy price in refined metal')
                                    bp = await self.bot.wait_for('message', check=self.check)
                                    bp = bp.clean_content.lower()
                                    buy1 = f'&buy_metal={bp}'
                                    await ctx.send('Buy price in keys')
                                    bp = await self.bot.wait_for('message', check=self.check)
                                    bp = bp.clean_content.lower()
                                    buy2 = f'&buy_keys={bp}'
                                    steamcommand += f'{buy1}{buy2}'

                                    await ctx.send('Sell price in refined metal')
                                    sp = await self.bot.wait_for('message', check=self.check)
                                    sp = sp.clean_content.lower()
                                    sell1 = f'&sell_metal={sp}'
                                    await ctx.send('Sell price in keys')
                                    sp = await self.bot.wait_for('message', check=self.check)
                                    sp = sp.clean_content.lower()
                                    sell2 = f'&sell_keys={sp}'
                                    steamcommand += f'{sell1}{sell2}'
                                    scclist = scclist.replace('\nPrice', '')
                                    notgonethrough1 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'limit' or prefix == 'l' and notgonethrough1:  # limit prefix
                                    await ctx.send('Max stock is')
                                    limit = await self.bot.wait_for('message', check=self.check)
                                    limit = limit.clean_content.lower()
                                    steamcommand += f'&limit={limit}'
                                    scclist = scclist.replace('\nLimit', '')
                                    notgonethrough1 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'quality' or prefix == 'q' and notgonethrough2:  # quality prefix
                                    await ctx.send(f'Quality (enter {qualities})')
                                    while 1:
                                        quality = await self.bot.wait_for('message', check=self.check)
                                        quality = quality.clean_content.lower()
                                        if quality in qualities.replace(',', '').lower():
                                            if do == 'update':
                                                steamcommand = f'{quality} {steamcommand}'

                                            elif do == 'add':
                                                quality = f'&quality={quality}'
                                                steamcommand += quality
                                            break
                                        else:
                                            await ctx.send(f'Try again with a valid value ({qualities}')

                                    scclist = scclist.replace('\nQuality', '')
                                    notgonethrough2 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'intent' or prefix == 'i' and notgonethrough3:  # intent prefix
                                    await ctx.send(f'Intent is to ({intents})')
                                    while 1:
                                        intent = await self.bot.wait_for('message', check=self.check)
                                        intent = intent.clean_content.lower()
                                        if intent in intents.lower():
                                            steamcommand += f'&intent={intent}'
                                            break
                                        else:
                                            await ctx.send('Try again with a valid value (' + intents + ')')
                                    scclist = scclist.replace('\nIntent', '')
                                    notgonethrough3 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'craftable' or prefix == 'c' and notgonethrough4:  # craftable prefix
                                    await ctx.send('Is the item craftable?')
                                    while 1:
                                        craftable = await self.bot.wait_for('message', check=self.check)
                                        craftable = craftable.clean_content.lower()
                                        if craftable == 't' or craftable == 'true' or craftable == 'y' or craftable == 'yes':
                                            if do == 'update':
                                                craftable = 'Craftable'
                                                steamcommand = f'{craftable} {steamcommand}'
                                            elif do == 'add':
                                                steamcommand += '&quality=true'
                                            break
                                        elif craftable == 'f' or craftable == 'false' or craftable == 'n' or craftable == 'no':
                                            if do == 'update':
                                                craftable = 'Non-Craftable '
                                                steamcommand = f'{craftable}{steamcommand}'
                                            elif do == 'add':
                                                steamcommand += '&quality=false'
                                        else:
                                            await ctx.send('Try again with a valid value (y/n or t/f)')
                                    scclist = scclist.replace('\nCraftable', '')
                                    notgonethrough4 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'australium' or prefix == 'au' and notgonethrough5:  # australium prefix
                                    await ctx.send('Is the item australium?')
                                    while 1:
                                        australium = await self.bot.wait_for('message', check=self.check)
                                        australium = australium.clean_content.lower()
                                        if australium == 't' or australium == 'true' or australium == 'y' or australium == 'yes':
                                            if do == 'update':
                                                australium = 'Strange Australium'
                                                steamcommand = f'{australium}{steamcommand}'
                                            elif do == 'add':
                                                australium = 'true'
                                                australium = f'&strange={australium}&australium={australium}'
                                                steamcommand += australium
                                            break
                                        elif australium == 'f' or australium == 'false' or australium:
                                            break
                                        else:
                                            await ctx.send('Try again with a valid value (y/n or t/f)')
                                    scclist = scclist.replace('\nAustralium', '')
                                    notgonethrough5 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'killstreak' or prefix == 'k' and notgonethrough6:  # killstreak prefix
                                    await ctx.send(
                                        'Is the item killstreak (Killstreak (1), Specialized (2) or Professional (3))')
                                    while 1:
                                        killstreak = await self.bot.wait_for('message', check=self.check)
                                        killstreak = killstreak.clean_content.lower()
                                        if killstreak == '1' or killstreak == 'k' or killstreak == 'killstreak' or killstreak == 'basic':
                                            if do == 'update':
                                                steamcommand = f'Killstreak {steamcommand}'
                                            elif do == 'add':
                                                steamcommand += '&quality=1'
                                            break
                                        elif killstreak == '2' or killstreak == 's' or killstreak == 'specialized':
                                            if do == 'update':
                                                steamcommand = f'Specialized {steamcommand}'
                                            elif do == 'add':
                                                steamcommand += '&quality=2'
                                            break
                                        elif killstreak == '3' or killstreak == 'p' or killstreak == 'professional':
                                            if do == 'update':
                                                steamcommand = f'Professional {steamcommand}'
                                            elif do == 'add':
                                                steamcommand += '&quality=3'
                                            break
                                        else:
                                            await ctx.send('Try again with a valid value (1/2/3 or k/s/p)')
                                    scclist = scclist.replace('\nKillstreak', '')
                                    notgonethrough6 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'effect' or prefix == 'e' and notgonethrough7:  # effect suffix
                                    await ctx.send('What is the unusual effect? E.g Burning Flames')
                                    suffix = await self.bot.wait_for('message', check=self.check)
                                    effect = suffix.clean_content
                                    if do == 'update':
                                        steamcommand = f'{effect}{steamcommand}'
                                    elif do == 'add':
                                        steamcommand += f'&effect={effect}'
                                    scclist = scclist.replace('\nEffect', '')
                                    notgonethrough7 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'autoprice' or prefix == 'ap' and notgonethrough8:  # effect suffix
                                    await ctx.send('Is autoprice enabled?')
                                    while 1:
                                        suffix = await self.bot.wait_for('message', check=self.check)
                                        autoprice = suffix.clean_content.lower()
                                        if autoprice == 't' or autoprice == 'true' or autoprice == 'y' or autoprice == 'yes' or autoprice == 'f' or autoprice == 'false' or autoprice == 'n' or autoprice == 'no':
                                            steamcommand += f'&autoprice={autoprice}'
                                            break
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')

                                    scclist = scclist.replace('\nAutopricing', '')
                                    notgonethrough8 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')
                                    break

                                elif prefix == 'escape' or prefix == 'esc':
                                    break

                                else:
                                    await ctx.send('Try again this time with something in the list')

                        elif choice == 'no' or choice == 'n':
                            if do == 'update':
                                steamcommand = f'{self.bot.updatem}{steamcommand}'
                            elif do == 'add':
                                steamcommand = f'{self.bot.addm}{steamcommand}'
                            break

                        else:
                            await ctx.send('Please try again')

            else:
                await ctx.send('Please try again with Update/Add/Remove')

            # sending msgs ---------------------------------------------------------------------------------------------

            await ctx.send(f'Command to {do} {item_to_uar} is `{steamcommand}`')
            await ctx.send('Do you want to send the command to the bot?\nType yes or no')
            while 1:
                choice = await self.bot.wait_for('message', check=self.check)
                choice = choice.clean_content.lower()

                if choice == 'yes' or choice == 'y':
                    await ctx.send("You have sent the bot a new command")
                    self.bot.client.get_user(self.bot.bot64id).send_message(steamcommand)
                    return
                elif choice == 'no' or choice == 'n':
                    await ctx.send("You didn't send the command to the bot :(")
                    return
                else:
                    await ctx.send('Please try again with y/n')

    @commands.command()
    @commands.is_owner()
    async def cashout(self, ctx):
        """Want to cash-out all your listings?"""
        listingsjson = json.loads(open(f'{self.bot.templocation}/listings.json', 'r').read())
        await ctx.send(f'Cashing out {len(listingsjson)} items, this may take a while')
        for value in listingsjson:
            command = f'{self.bot.updatem}{value["name"]}&intent=sell'
            self.bot.client.get_user(self.bot.bot64id).send_message(command)
            await ctx.send(command)
            await asyncio.sleep(5)
        await ctx.send('Completed the intent update')

    @commands.command(aliases=['raw_add'])
    @commands.is_owner()
    async def add_raw(self, ctx, *, ending: Optional = ' '):
        """Add lots of items, very volatile `!add names` is much more likely to be stable"""
        await ctx.send('Paste all the items you want to add on a new line')
        file = await self.bot.wait_for('message', check=self.check)
        file = file.content
        open(f'{self.bot.templocation}/raw_add_listings.txt', 'w+').write(file)

        items = open(f'{self.bot.templocation}/raw_add_listings.txt', 'r').read().splitlines()
        for item in items:
            self.bot.client.get_user(self.bot.bot64id).send_message(f'{self.bot.addm}{item}{ending}')
            await asyncio.sleep(5)
        await ctx.send(f'Done adding {len(items)} items')
        remove(f'{self.bot.templocation}/raw_add_listings.txt')


def setup(bot):
    bot.add_cog(SteamCog(bot))


def teardown():
    SteamCog.discordcheck.stop()
