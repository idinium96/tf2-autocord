import discord
from discord.ext import commands, tasks

import asyncio
import datetime


class SteamCog(commands.Cog, name='Steam'):
    """Commands that are mainly owner restricted and only work if you are logged in to your steam account"""

    def __init__(self, bot):
        self.bot = bot
        self.discordcheck.start()
        self.bot.trades = 0


    @tasks.loop(seconds=5)
    async def discordcheck(self):
        if self.bot.sbotresp is not None:
            if 'Recieved offer' in self.bot.sbotresp:
                self.bot.trades += 1
            if 'accepted' in self.bot.sbotresp:
                color2 = int('5C7E10', 16)
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

            embed.set_footer(text=str(datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')))  # 12hr time, am/pm, weekday, day, month
            await self.bot.get_user(self.bot.owner_id).send(embed=embed)
            if self.bot.usermessage != 0:
                embed = discord.Embed(color=0xFFFF66)
                embed.add_field(name='User Message:',
                                value=f'You have a message from a user:\n{self.bot.usermessage}'
                                      f'\nType {self.bot.command_prefix}acknowledged',
                                inline=False)
                await self.bot.get_user(self.bot.owner_id).send(embed=embed)
                await asyncio.sleep(60)
            self.bot.sbotresp = None


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

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, *, name):
        """Aad is used to add items from your bot's classifieds

        It allows the chaining of commands eg. `!add names=This&intent=sell, That, The other`"""
        channel = ctx.message.channel

        def check(m):
            return m.content and m.channel == channel and m.author.id == self.bot.owner_id

        string = 0
        list = 0
        if 'names=' in name:
            mul = 'these'
            mul2 = 'commands'
            msgs = name[6:]
            name = msgs.split(', ')
            name = [self.bot.addm + x for x in name]
            list = 1

        elif 'name=' in name:
            mul = 'this'
            mul2 = 'command'
            msgs = name[5:]
            name = self.bot.addm + msgs
            string = 1

        if list == 1:
            dscontent = str(name).replace('[', '`').replace(']', '`').replace(', ', '`, `')
        elif string == 1:
            dscontent = f'`{name}`'
        await ctx.send(f'Do you want to send {mul} {dscontent} {mul2} to the bot?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=check)
            choice = choice.clean_content.lower()

            if choice == 'y' or choice == 'yes':
                response = 1
                await ctx.send(f'Send {mul} {mul2} to the bot {dscontent}')
                async with ctx.typing():
                    await asyncio.sleep(5)
                    if list == 1:
                        for message in name:
                            self.bot.client.get_user(self.bot.bot64id).send_message(message)
                            await asyncio.sleep(3)

                    if string == 1:
                        self.bot.client.get_user(self.bot.bot64id).send_message(name)
                        await asyncio.sleep(3)

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx, *, name):
        """Update is used to update items from your bot's classifieds

        It allows the chaining of commands eg. `!update names=This&intent=bank, That, The other`"""
        channel = ctx.message.channel

        def check(m):
            return m.content and m.channel == channel and m.author.id == self.bot.owner_id

        if 'names=' in name:
            mul = 'these'
            mul2 = 'commands'
            msgs = name[6:]
            name = msgs.split(', ')
            name = [self.bot.updatem + x for x in name]
            list = 1

        elif 'name=' in name:
            mul = 'this'
            mul2 = 'command'
            msgs = name[5:]
            name = self.bot.updatem + msgs
            string = 1

        if list == 1:
            dscontent = str(name).replace('[', '`').replace(']', '`').replace(', ', '`, `')
        elif string == 1:
            dscontent = f'`{name}`'
        await ctx.send(f'Do you want to send {mul} {dscontent} {mul2} to the bot?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=check)
            choice = choice.clean_content.lower()

            if choice == 'y' or choice == 'yes':
                response = 1
                await ctx.send(f'Send {mul} {mul2} to the bot {dscontent}')
                async with ctx.typing():
                    await asyncio.sleep(5)
                    if list == 1:
                        for message in name:
                            self.bot.client.get_user(self.bot.bot64id).send_message(message)
                            await asyncio.sleep(3)

                    if string == 1:
                        self.bot.client.get_user(self.bot.bot64id).send_message(name)
                        await asyncio.sleep(3)

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, *, name):
        """Remove is used to remove items from your bot's classifieds

        It allows the chaining of commands eg. `!remove names=This&intent=bank, That, The Other`"""
        channel = ctx.message.channel

        def check(m):
            return m.content and m.channel == channel and m.author.id == self.bot.owner_id

        if 'items=' in name:
            mul = 'these'
            mul2 = 'commands'
            msgs = name[6:]
            name = msgs.split(', ')
            name = [self.bot.removem + x for x in name]
            list = 1

        elif 'item=' in name:
            mul = 'this'
            mul2 = 'command'
            msgs = name[5:]
            name = self.bot.removem + msgs
            string = 1

        if list == 1:
            dscontent = str(name).replace('[', '`').replace(']', '`').replace(', ', '`, `')
        elif string == 1:
            dscontent = f'`{name}`'
        await ctx.send(f'Do you want to send {mul} {dscontent} {mul2} to the bot?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=check)
            choice = choice.clean_content.lower()

            if choice == 'y' or choice == 'yes':
                response = 1
                await ctx.send(f'Send {mul} {mul2} to the bot {dscontent}')
                async with ctx.typing():
                    await asyncio.sleep(5)
                    if list == 1:
                        for message in name:
                            self.bot.client.get_user(self.bot.bot64id).send_message(message)
                            await asyncio.sleep(3)
                    if string == 1:
                        self.bot.client.get_user(self.bot.bot64id).send_message(name)
                        await asyncio.sleep(3)

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

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

        eg. `!send !message 76561198248053954 Get on steam `"""
        async with ctx.typing():
            self.bot.client.get_user(self.bot.bot64id).send_message(message)
            await ctx.send(f"Sent `{message}` to the bot")
            await asyncio.sleep(3)

    @commands.command(aliases=['bp'])
    async def backpack(self, ctx):
        """Pull up your backpack and your bot's"""
        embed = discord.Embed(title=' ', color=0x58788F)
        embed.set_thumbnail(url='https://steamuserimages-a.akamaihd.net/ugc'
                '/44226880714734120/EE4DAE995040556E8013F583ACBA971846FA1E2B/')
        embed.add_field(name='Your backpack:', value=f'https://backpack.tf/profiles/{self.bot.client.user.steam_id}')
        embed.add_field(name='Your bot\'s backpack', value=f'https://backpack.tf/profiles/{self.bot.bot64id}')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def scc(self, ctx):
        """Scc is a worse version of Hackerino's command generator tool

        scc makes me happy and it should make you aswell and it's easy to use :thumbsup:"""
        channel = ctx.channel
        author = ctx.author
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

        def check(m):
            return m.content and m.channel == channel and m.author.id == self.bot.owner_id

        await ctx.send('What do you want to do?\nUpdate, Remove or Add?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=check)
            choice = choice.clean_content.lower()

            if choice == 'update' or choice == 'u' or choice == 'add' or choice == 'a' or choice == 'remove' or choice == 'r':
                if choice == 'update' or choice == 'u':
                    do = 'update'
                elif choice == 'add' or choice == 'a':
                    do = 'add'
                elif choice == 'remove' or choice == 'r':
                    do = 'remove'
                await ctx.send(f'What item do you want to {do}?')
                item_to_uar = await self.bot.wait_for('message', check=check)
                item_to_uar = item_to_uar.clean_content
                steamcommand = item_to_uar

                if do == 'remove':
                    f'{self.bot.removem}{steamcommand}'
                else:
                    await ctx.send('Want to add prefixes?\nType yes or no')
                    response = 0
                    while response == 0:
                        choice = await self.bot.wait_for('message', check=check)
                        choice = choice.clean_content.lower()

                        if choice == 'yes' or choice == 'y':
                            response = 1
                            prefixes = 0
                            await ctx.send(scclist)

                            while prefixes != 9:
                                response = 0
                                while response == 0:
                                    prefix = await self.bot.wait_for('message', check=check)
                                    prefix = prefix.clean_content.lower()

                                    if prefix == 'price' or prefix == 'p' and notgonethrough:  # buy price prefix
                                        await ctx.send('Buy price in refined metal')
                                        bp = await self.bot.wait_for('message', check=check)
                                        bp = bp.clean_content.lower()
                                        buy1 = '&buy_metal=' + bp
                                        await ctx.send('Buy price in keys')
                                        bp = await self.bot.wait_for('message', check=check)
                                        bp = bp.clean_content.lower()
                                        buy2 = '&buy_keys=' + bp
                                        steamcommand += buy1 + buy2

                                        await ctx.send('Sell price in refined metal')
                                        sp = await self.bot.wait_for('message', check=check)
                                        sp = sp.clean_content.lower()
                                        sell1 = '&sell_metal=' + sp
                                        await ctx.send('Sell price in keys')
                                        sp = await self.bot.wait_for('message', check=check)
                                        sp = sp.clean_content.lower()
                                        sell2 = '&sell_keys=' + sp
                                        steamcommand += sell1 + sell2
                                        prefixes += 1
                                        scclist = scclist.replace('\nPrice', '')
                                        notgonethrough1 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'limit' or prefix == 'l' and notgonethrough1:  # limit prefix
                                        await ctx.send('Max stock is')
                                        limit = await self.bot.wait_for('message', check=check)
                                        limit = limit.clean_content.lower()
                                        steamcommand += '&limit=' + limit
                                        prefixes += 1
                                        scclist = scclist.replace('\nLimit', '')
                                        notgonethrough1 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'quality' or prefix == 'q' and notgonethrough2:  # quality prefix
                                        await ctx.send('Quality (enter ' + qualities + ')')
                                        while 1:
                                            quality = await self.bot.wait_for('message', check=check)
                                            quality = quality.clean_content.lower()
                                            if quality in qualities.replace(',', '').lower():
                                                if do == 'update':
                                                    steamcommand = quality + ' ' + steamcommand

                                                elif do == 'add':
                                                    quality = '&quality=' + quality
                                                    steamcommand += quality
                                                break
                                            else:
                                                await ctx.send('Try again with a valid value (' + qualities + ')')

                                        prefixes += 1
                                        scclist = scclist.replace('\nQuality', '')
                                        notgonethrough2 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'intent' or prefix == 'i' and notgonethrough3:  # intent prefix
                                        await ctx.send('Intent is to (' + intents + ')')
                                        response = 0
                                        while response == 0:
                                            intent = await self.bot.wait_for('message', check=check)
                                            intent = intent.clean_content.lower()
                                            if intent in intents.lower():
                                                steamcommand += '&intent=' + intent
                                                response = 1
                                            else:
                                                await ctx.send('Try again with a valid value (' + intents + ')')
                                        prefixes += 1
                                        scclist = scclist.replace('\nIntent', '')
                                        notgonethrough3 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'craftable' or prefix == 'c' and notgonethrough4:  # craftable prefix
                                        await ctx.send('Is the item craftable?')
                                        while 1:
                                            craftable = await self.bot.wait_for('message', check=check)
                                            craftable = craftable.clean_content.lower()
                                            if craftable == 't' or craftable == 'true' or craftable == 'y' or craftable == 'yes':
                                                if do == 'update':
                                                    craftable = 'Craftable '
                                                    steamcommand = craftable + steamcommand
                                                elif do == 'add':
                                                    steamcommand += '&quality=true'
                                                break
                                            elif craftable == 'f' or craftable == 'false' or craftable == 'n' or craftable == 'no':
                                                if do == 'update':
                                                    craftable = 'Non-Craftable '
                                                    steamcommand = craftable + steamcommand
                                                elif do == 'add':
                                                    steamcommand += '&quality=false'
                                            else:
                                                await ctx.send('Try again with a valid value (y/n or t/f)')
                                        prefixes += 1
                                        scclist = scclist.replace('\nCraftable', '')
                                        notgonethrough4 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'australium' or prefix == 'au' and notgonethrough5:  # australium prefix
                                        await ctx.send('Is the item australium?')
                                        while 1:
                                            australium = await self.bot.wait_for('message', check=check)
                                            australium = australium.clean_content.lower()
                                            if australium == 't' or australium == 'true' or australium == 'y' or australium == 'yes':
                                                if do == 'update':
                                                    australium = 'Strange Australium'
                                                    steamcommand = australium + steamcommand
                                                elif do == 'add':
                                                    australium = 'true'
                                                    australium = '&strange=' + australium + '&australium=' + australium
                                                    steamcommand = steamcommand + australium
                                                break
                                            elif australium == 'f' or australium == 'false' or australium:
                                                break
                                            else:
                                                await ctx.send('Try again with a valid value (y/n or t/f)')
                                        prefixes += 1
                                        scclist = scclist.replace('\nAustralium', '')
                                        notgonethrough5 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'killstreak' or prefix == 'k' and notgonethrough6:  # killstreak prefix
                                        await ctx.send(
                                            'Is the item killstreak (Killstreak (1), Specialized (2) or Professional (3))')
                                        while 1:
                                            killstreak = await self.bot.wait_for('message', check=check)
                                            killstreak = killstreak.clean_content.lower()
                                            if killstreak == '1' or killstreak == 'k' or killstreak == 'killstreak' or killstreak == 'basic':
                                                if do == 'update':
                                                    steamcommand = 'Killstreak ' + steamcommand
                                                elif do == 'add':
                                                    steamcommand += '&quality=1'
                                                break
                                            elif killstreak == '2' or killstreak == 's' or killstreak == 'specialized':
                                                if do == 'update':
                                                    steamcommand = 'Specialized ' + steamcommand
                                                elif do == 'add':
                                                    steamcommand += '&quality=2'
                                                break
                                            elif killstreak == '3' or killstreak == 'p' or killstreak == 'professional':
                                                if do == 'update':
                                                    steamcommand = 'Professional ' + steamcommand
                                                elif do == 'add':
                                                    steamcommand += '&quality=3'
                                                break
                                            else:
                                                await ctx.send('Try again with a valid value (1/2/3 or k/s/p)')
                                        prefixes += 1
                                        scclist = scclist.replace('\nKillstreak', '')
                                        notgonethrough6 = False
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'effect' or prefix == 'e' and notgonethrough7:  # effect suffix
                                        await ctx.send('What is the unusual effect? E.g Burning Flames')
                                        suffix = await self.bot.wait_for('message', check=check)
                                        effect = suffix.clean_content
                                        if do == 'update':
                                            steamcommand = effect + steamcommand
                                        elif do == 'add':
                                            steamcommand += '&effect=' + effect
                                        scclist = scclist.replace('\nEffect', '')
                                        notgonethrough7 = False
                                        prefixes += 1
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                    elif prefix == 'autoprice' or prefix == 'ap' and notgonethrough8:  # effect suffix
                                        await ctx.send('Is autoprice enabled')
                                        while 1:
                                            suffix = await self.bot.wait_for('message', check=check)
                                            autoprice = suffix.clean_content.lower()
                                            if autoprice == 't' or autoprice == 'true' or autoprice == 'y' or autoprice == 'yes':
                                                steamcommand += '&autoprice=' + autoprice
                                                break
                                            elif autoprice == 'f' or autoprice == 'false' or autoprice == 'n' or autoprice == 'no':
                                                steamcommand += '&autoprice=' + autoprice
                                                break
                                            else:
                                                await ctx.send('Try again with a valid value (Y/N or T/F)')

                                        scclist = scclist.replace('\nAutopricing', '')
                                        notgonethrough8 = False
                                        prefixes += 1
                                        await ctx.send(
                                            f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

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
                choice = await self.bot.wait_for('message', check=check)
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


def setup(bot):
    bot.add_cog(SteamCog(bot))
