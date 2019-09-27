import discord
from discord.ext import commands, tasks
import asyncio, time


togprofit = 0

def getcurrenttime():
    global currenttime
    currenttime = time.asctime()[11:-8]

class SteamCog(commands.Cog, name='Steam'):
    """Commands that are mainly owner restricted and only work if you are logged in"""
    def __init__(self, bot):
        self.bot = bot
        self.bgcheck.start()

    @tasks.loop(seconds=5)
    async def bgcheck(self):
        if self.bot.botresp is True:
            if 'accepted' in self.bot.sbotresp:
                color2 = int('5C7E10', 16)
            elif 'declined' in self.bot.sbotresp or 'canceled' in self.bot.sbotresp:
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
            embed.set_footer(text=time.asctime())
            await self.bot.get_user(self.bot.owner_id).send(embed=embed)
            if self.bot.usermessage != 0:
                embed = discord.Embed(color=0xFFFF66)
                embed.add_field(name='User Message:',
                                value=f'You have a message from a user:\n{self.bot.usermessage}'
                                      f'\nType {self.bot.command_prefix}acknowledged',
                                inline=False)
                await self.bot.get_user(self.bot.owner_id).send(embed=embed)
                await asyncio.sleep(30)
            self.bot.botresp = False

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, *, name: str):
        """Aad is used to add items from your bot's classifieds, it allows the chaining of commands eg. `!add names=This&intent=sell, That, The other`"""
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
                global botresp
                self.bot.botresp = False
                while self.bot.botresp is False:
                    async with ctx.typing():
                        await asyncio.sleep(5)
                        nsend = 0
                        if list == 1:
                            while nsend < len(name):
                                self.bot.client.get_user(self.bot.bot64id).send_message(name[nsend])
                                nsend += 1
                                await asyncio.sleep(3)

                        if string == 1:
                            self.bot.client.get_user(self.bot.bot64id).send_message(name)
                            await asyncio.sleep(3)

                        self.bot.botresp = True

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx, *, name: str):
        """Update is used to update items from your bot's classifieds, it allows the chaining of commands eg. `!update names=This&intent=bank, That, The other`"""
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
                global botresp
                self.bot.botresp = False
                while self.bot.botresp is False:
                    async with ctx.typing():
                        await asyncio.sleep(5)
                        nsend = 0
                        if list == 1:
                            while nsend < len(name):
                                self.bot.client.get_user(self.bot.bot64id).send_message(name[nsend])
                                nsend += 1
                                await asyncio.sleep(3)

                        if string == 1:
                            self.bot.client.get_user(self.bot.bot64id).send_message(name)
                            await asyncio.sleep(3)

                        self.bot.botresp = True

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, *, name: str):
        """Remove is used to remove items from your bot's classifieds, it allows the chaining of commands eg. `!remove names=This&intent=bank, That, The Other`"""
        channel = ctx.message.channel

        def check(m):
            return m.content and m.channel == channel and m.author.id == self.bot.owner_id

        if 'names=' in name:
            mul = 'these'
            mul2 = 'commands'
            msgs = name[6:]
            name = msgs.split(', ')
            name = [self.bot.removem + x for x in name]
            list = 1

        elif 'name=' in name:
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
                global botresp
                self.bot.botresp = False
                while self.bot.botresp is False:
                    async with ctx.typing():
                        await asyncio.sleep(5)
                        nsend = 0
                        if list == 1:
                            while nsend < len(name):
                                self.bot.client.get_user(self.bot.bot64id).send_message(name[nsend])
                                nsend += 1
                                await asyncio.sleep(3)

                        if string == 1:
                            self.bot.client.get_user(self.bot.bot64id).send_message(name)
                            await asyncio.sleep(3)

                        self.bot.botresp = True

            elif choice == 'n' or choice == 'no':
                await ctx.send("The command hasn't been sent")
                response = 1
            else:
                await ctx.send('Try Again')

    @commands.command()
    @commands.is_owner()
    async def profit(self, ctx):
        """Returns your bot's profit as it normally would"""
        self.bot.botresp = False
        while self.bot.botresp is False:
            async with ctx.typing():
                self.bot.client.get_user(self.bot.bot64id).send_message(self.bot.command_prefix + 'profit')
                await asyncio.sleep(3)
                self.bot.botresp = True

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, *, message: str):
        """Send is used to send a message to the bot eg. `!send [message]`"""
        self.bot.botresp = False
        while self.bot.botresp is False:
            async with ctx.typing():
                self.bot.client.get_user(self.bot.bot64id).send_message(message)
                await ctx.send(f"Sent `{message}` to the bot")
                await asyncio.sleep(3)
                self.bot.botresp = True

    @commands.command(aliases=['bp'])
    async def backpack(self, ctx):
        """Pull up your backpack and your bot's"""
        embed = discord.Embed(title=' ', color=0x58788F)
        embed.set_thumbnail(
            url='https://steamuserimages-a.akamaihd.net/ugc/44226880714734120/EE4DAE995040556E8013F583ACBA971846FA1E2B/')
        embed.add_field(name='You backpack:', value='https://backpack.tf/profiles/' + str(self.bot.client.steam_id),
                        inline=False)
        embed.add_field(name='Your bot\'s backpack', value='https://backpack.tf/profiles/' + str(self.bot.bot64id))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def scc(self, ctx):
        """Scc is a discount version of Hackerino's command generator tool"""
        channel = ctx.message.channel
        author = ctx.message.author
        suffixes = 0
        prefixes = 0
        choice = 0
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

            # remove ---------------------------------------------------------------------------------------------------

            if choice == 'remove' or choice == 'r':
                response = 1
                do = 'remove '
                await ctx.send('What do you want to remove?')
                item_to_uar = await self.bot.wait_for('message', check=check)
                item_to_uar = item_to_uar.clean_content
                steamcommand = self.bot.removem + item_to_uar

            # update ---------------------------------------------------------------------------------------------------

            elif choice == 'update' or choice == 'u':
                do = 'update '
                await ctx.send('What items do you want to update?')
                item_to_uar = await self.bot.wait_for('message', check=check)
                item_to_uar = item_to_uar.clean_content
                steamcommand = item_to_uar
                await ctx.send('Want to add prefixes?\nType yes or no')
                response = 0
                while response == 0:
                    choice = await self.bot.wait_for('message', check=check)
                    choice = choice.clean_content.lower()

                    if choice == 'yes' or choice == 'y':
                        response = 1
                        await ctx.send(scclist)
                        prefixes = 0
                        while prefixes != 9:
                            response = 0
                            while response == 0:
                                prefix = await self.bot.wait_for('message', check=check)
                                prefix = prefix.clean_content.lower()

                                if prefix == 'price' or prefix == 'p' and notgonethrough is True:  # buy price prefix
                                    await ctx.send('Buy price in refined metal')
                                    bp = await self.bot.wait_for('message', check=check)
                                    bp = bp.clean_content.lower()
                                    buy1 = '&buy_metal=' + bp
                                    await ctx.send('Buy price in keys')
                                    bp = await self.bot.wait_for('message', check=check)
                                    bp = bp.clean_content.lower()
                                    buy2 = '&buy_keys=' + bp
                                    steamcommand = steamcommand + buy1 + buy2

                                    await ctx.send('Sell price in refined metal')
                                    sp = await self.bot.wait_for('message', check=check)
                                    sp = sp.clean_content.lower()
                                    sell1 = '&sell_metal=' + sp
                                    await ctx.send('Sell price in keys')
                                    sp = await self.bot.wait_for('message', check=check)
                                    sp = sp.clean_content.lower()
                                    sell2 = '&sell_keys=' + sp
                                    steamcommand = steamcommand + sell1 + sell2
                                    prefixes += 1
                                    scclist = scclist.replace('\nPrice', '')
                                    notgonethrough1 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'limit' or prefix == 'l' and notgonethrough1 is True:  # limit prefix
                                    await ctx.send('Max stock is')
                                    limit = await self.bot.wait_for('message', check=check)
                                    limit = limit.clean_content.lower()
                                    limit = '&limit=' + limit
                                    steamcommand = steamcommand + limit
                                    prefixes += 1
                                    scclist = scclist.replace('\nLimit', '')
                                    notgonethrough1 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'quality' or prefix == 'q' and notgonethrough2 is True:  # quality prefix
                                    await ctx.send('Quality (enter ' + qualities + ')')
                                    response = 0
                                    while response == 0:
                                        quality = await self.bot.wait_for('message', check=check)
                                        quality = quality.clean_content.lower()
                                        if quality in qualities.replace(',', '').lower():
                                            steamcommand = quality + ' ' + steamcommand
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (' + qualities + ')')
                                    prefixes += 1
                                    scclist = scclist.replace('\nQuality', '')
                                    notgonethrough2 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'intent' or prefix == 'i' and notgonethrough3 is True:  # intent prefix
                                    await ctx.send('Intent is to (' + intents + ')')
                                    response = 0
                                    while response == 0:
                                        intent = await self.bot.wait_for('message', check=check)
                                        intent = intent.clean_content.lower()
                                        if intent in intents.lower():
                                            intent = '&intent=' + intent
                                            steamcommand = steamcommand + intent
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (' + intents + ')')
                                    prefixes += 1
                                    scclist = scclist.replace('\nIntent', '')
                                    notgonethrough3 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'craftable' or prefix == 'c' and notgonethrough4 is True:  # craftable prefix
                                    await ctx.send('Is the item craftable?')
                                    response = 0
                                    while response == 0:
                                        craftable = await self.bot.wait_for('message', check=check)
                                        craftable = craftable.clean_content.lower()
                                        if craftable == 't' or craftable == 'true' or craftable == 'y' or craftable == 'yes':
                                            craftable = 'Craftable'
                                        elif craftable == 'f' or craftable == 'false' or craftable == 'n' or craftable == 'no':
                                            craftable = 'Non-Craftable'
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')
                                    steamcommand = craftable + steamcommand
                                    prefixes += 1
                                    scclist = scclist.replace('\nCraftable', '')
                                    notgonethrough4 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'australium' or prefix == 'au' and notgonethrough5 is True:  # australium prefix
                                    await ctx.send('Is the item australium?')
                                    response = 0
                                    while response == 0:
                                        australium = await self.bot.wait_for('message', check=check)
                                        australium = australium.clean_content.lower()
                                        if australium == 't' or australium == 'true' or australium == 'y' or australium == 'yes':
                                            australium = 'Strange Australium'
                                            steamcommand = australium + steamcommand
                                            response = 1
                                        elif australium == 'f' or australium == 'false' or australium:
                                            response = 1
                                            pass
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')
                                    prefixes += 1
                                    scclist = scclist.replace('\nAustralium', '')
                                    notgonethrough5 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'killstreak' or prefix == 'k' and notgonethrough6 is True:  # killstreak prefix
                                    await ctx.send(
                                        'Is the item killstreak (Killstreak (1), Specialized (2) or Professional (3))')
                                    response = 0
                                    while response == 0:
                                        killstreak = await self.bot.wait_for('message', check=check)
                                        killstreak = killstreak.clean_content.lower()
                                        if killstreak == 1 or killstreak == 'k':
                                            killstreak = 'killstreak'
                                            response = 1
                                        elif killstreak == 2 or killstreak == 's':
                                            killstreak = 'specialized'
                                            response = 1
                                        elif killstreak == 3 or killstreak == 'p':
                                            killstreak = 'professional'
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (1/2/3 or K/S/P)')
                                    steamcommand = killstreak + steamcommand
                                    prefixes += 1
                                    scclist = scclist.replace('\nKillstreak', '')
                                    notgonethrough6 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'effect' or prefix == 'e' and notgonethrough7 is True:  # effect suffix
                                    await ctx.send('What is the unusual effect? E.g Burning Flames')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    effect = suffix.clean_content
                                    steamcommand = effect + steamcommand
                                    scclist = scclist.replace('\nEffect', '')
                                    notgonethrough7 = False
                                    prefixes += 1
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'autoprice' or prefix == 'ap' and notgonethrough8 is True:  # effect suffix
                                    await ctx.send('Is autoprice enabled')
                                    response = 0
                                    while response == 0:
                                        suffix = await self.bot.wait_for('message', check=check)
                                        autoprice = suffix.clean_content.lower()
                                        if autoprice == 't' or autoprice == 'true' or autoprice == 'y' or autoprice == 'yes':
                                            autoprice = '&autoprice=' + autoprice
                                            steamcommand = steamcommand + autoprice
                                            response = 1
                                        elif autoprice == 'f' or autoprice == 'false' or autoprice == 'n' or autoprice == 'no':
                                            autoprice = '&autoprice=' + autoprice
                                            steamcommand = steamcommand + autoprice
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')
                                    scclist = scclist.replace('\nAutopricing', '')
                                    notgonethrough8 = False
                                    prefixes += 1
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif prefix == 'escape' or prefix == 'esc':
                                    response = 1
                                    steamcommand = self.bot.updatem + steamcommand
                                    prefixes = 9
                                else:
                                    await ctx.send('Try again this time with something in the list')

                    elif choice == 'no' or choice == 'n':
                        steamcommand = self.bot.updatem + steamcommand
                        response = 1

                    else:
                        await ctx.send('Please try again')

            # add ------------------------------------------------------------------------------------------------------

            elif choice == 'add' or choice == 'a':
                do = 'add '
                await ctx.send('What item do you want to add to your classifieds?')
                response = 0
                while response == 0:
                    item_to_uar = await self.bot.wait_for('message', check=check)
                    item_to_uar = item_to_uar.clean_content
                    steamcommand = item_to_uar

                    await ctx.send('Want to add suffixes?\nType yes or no')

                    choice = await self.bot.wait_for('message', check=check)
                    choice = choice.clean_content.lower()
                    if choice == 'yes' or choice == 'y':
                        await ctx.send(scclist)
                        suffixes = 0
                        while suffixes != 9:
                            response = 0
                            while response == 0:
                                suffix = await self.bot.wait_for('message', check=check)
                                suffix = suffix.clean_content

                                if suffix == 'p' or suffix == 'price' and notgonethrough is True:  # buy price suffix
                                    await ctx.send('Buy price in refined metal')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    bp = suffix.clean_content
                                    buy1 = '&buy_metal=' + bp
                                    await ctx.send('Buy price in keys')
                                    bp = await self.bot.wait_for('message', check=check)
                                    bp = bp.clean_content
                                    buy2 = '&buy_keys=' + bp
                                    steamcommand = steamcommand + buy1 + buy2

                                    await ctx.send('Sell price in refined metal')
                                    sp = await self.bot.wait_for('message', check=check)
                                    sp = sp.clean_content
                                    sell1 = '&sell_metal=' + sp
                                    await ctx.send('Sell price in keys')
                                    sp = await self.bot.wait_for('message', check=check)
                                    sp = sp.clean_content
                                    sell2 = '&sell_keys=' + sp
                                    steamcommand = steamcommand + sell1 + sell2
                                    suffixes += 1
                                    scclist = scclist.replace('\nPrice', '')
                                    notgonethrough = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'limit' or suffix == 'l' and notgonethrough1 is True:  # limit suffix
                                    response = 1
                                    await ctx.send('Max stock is (enter a number)')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    limit = suffix.clean_content
                                    limit = '&limit=' + limit
                                    steamcommand = steamcommand + limit
                                    suffixes += 1
                                    scclist = scclist.replace('\nLimit', '')
                                    notgonethrough1 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'quality' or suffix == 'q' and notgonethrough2 is True:  # quality suffix
                                    await ctx.send('Quality (enter ' + qualities + ')')
                                    response = 0
                                    while response == 0:
                                        suffix = await self.bot.wait_for('message', check=check)
                                        quality = suffix.clean_content.lower()
                                        if quality in qualities.replace(',', '').lower():
                                            quality = '&quality=' + quality
                                            steamcommand = steamcommand + quality
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (' + qualities + ')')
                                    suffixes += 1
                                    scclist = scclist.replace('\nQuality', '')
                                    notgonethrough2 = True
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'intent' or suffix == 'i' and notgonethrough3 is True:  # intent suffix
                                    await ctx.send('Intent (enter ' + intents + ')')
                                    response = 0
                                    while response == 0:
                                        suffix = await self.bot.wait_for('message', check=check)
                                        intent = suffix.clean_content
                                        if intent in intents.lower():
                                            intent = '&intent=' + intent
                                            steamcommand = steamcommand + intent
                                        else:
                                            await ctx.send('Try again with a valid value (' + intents + ')')
                                    suffixes = suffixes + 1
                                    scclist = scclist.replace('\nIntent', '')
                                    notgonethrough3 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'craftable' or suffix == 'c' and notgonethrough4 is True:  # craftable suffix
                                    await ctx.send('Is the item craftable?')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    craftable = suffix.clean_content.lower()
                                    while response == 0:
                                        if craftable == 't' or craftable == 'true' or craftable == 'y' or craftable == 'yes':
                                            craftable = 'true'
                                            response = 1
                                        elif 'f' == craftable or craftable == 'false' or craftable == 'n' or craftable == 'no':
                                            craftable = 'false'
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')
                                    craftable = '&craftable=' + craftable
                                    steamcommand = steamcommand + craftable
                                    suffixes += 1
                                    scclist = scclist.replace('\nCraftable', '')
                                    notgonethrough4 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'australium' or suffix == 'au' and notgonethrough5 is True:  # australium suffix
                                    await ctx.send('Is the item australium (True or False)')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    australium = suffix.clean_content.lower()
                                    response = 0
                                    while response == 0:
                                        if australium == 't' or australium == 'true':
                                            australium = 'true'
                                            response = 1
                                        elif 'f' == australium or australium == 'false':
                                            australium = 'false'
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (T/F)')
                                    australium = '&strange=' + australium + '&australium=' + australium
                                    steamcommand = steamcommand + australium
                                    suffixes += 1
                                    scclist = scclist.replace('\nAustralium', '')
                                    notgonethrough5 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'killstreak' or suffix == 'k' and notgonethrough6 is True:  # killstreak suffix
                                    await ctx.send('Is the item killstreak/specialized/professional?')
                                    response = 0
                                    while response == 0:
                                        suffix = await self.bot.wait_for('message', check=check)
                                        killstreak = suffix.clean_content
                                        if killstreak == 1 or killstreak == 'k' or killstreak == 'killstreak' or killstreak == 'basic':
                                            killstreak = 1
                                            response = 1
                                        elif killstreak == 2 or killstreak == 's' or killstreak == 'specialized':
                                            killstreak = 2
                                            response = 1
                                        elif killstreak == 3 or killstreak == 'p' or killstreak == 'professional':
                                            killstreak = 3
                                            response = 1
                                        else:
                                            await ctx.send('Try again with a valid value (1/2/3 or K/S/P)')
                                    killstreak = '&killstreak=' + killstreak
                                    steamcommand = steamcommand + killstreak
                                    suffixes += 1
                                    scclist = scclist.replace('\nKillstreak', '')
                                    notgonethrough6 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'effect' or suffix == 'e' and notgonethrough7 is True:  # effect suffix
                                    await ctx.send('What is the unusual effect? E.g Burning Flames')
                                    suffix = await self.bot.wait_for('message', check=check)
                                    effect = suffix.clean_content
                                    effect = '&effect=' + effect
                                    steamcommand = steamcommand + effect
                                    suffixes += 1
                                    scclist = scclist.replace('\nEffect', '')
                                    notgonethrough7 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'autoprice' or suffix == 'ap' and notgonethrough8 is True:  # effect suffix
                                    await ctx.send('Is autoprice enabled')
                                    response = 0
                                    while response == 0:
                                        suffix = await self.bot.wait_for('message', check=check)
                                        autoprice = suffix.clean_content.lower()
                                        if autoprice == 't' or autoprice == 'true' or autoprice == 'y' or autoprice == 'yes':
                                            autoprice = '&autoprice=' + autoprice
                                            steamcommand = steamcommand + autoprice
                                        elif autoprice == 'f' or autoprice == 'false' or autoprice == 'n' or autoprice == 'no':
                                            autoprice = '&autoprice=' + autoprice
                                            steamcommand = steamcommand + autoprice
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')
                                    suffixes += 1
                                    scclist = scclist.replace('\nEffect', '')
                                    notgonethrough8 = False
                                    await ctx.send(
                                        'Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                                elif suffix == 'escape' or suffix == 'esc':
                                    steamcommand = self.bot.addm + steamcommand
                                    response = 1
                                    suffixes = 9

                                else:
                                    await ctx.send('Try again this time with something in the list' + scclist)

                    elif choice == 'no' or choice == 'n':
                        response = 1
                        steamcommand = self.bot.addm + steamcommand

                    else:
                        await ctx.send('Please try again')

            else:
                await ctx.send('Please try again with Update/Add/Remove')

            # sending msgs ---------------------------------------------------------------------------------------------

            await ctx.send(f'Command to {do} {item_to_uar} is `{steamcommand}`')
            await ctx.send('Do you want to send the command to the bot?\nType yes or no')
            response = 0
            while response == 0:
                choice = await self.bot.wait_for('message', check=check)
                choice = choice.clean_content.lower()

                if choice == 'yes' or choice == 'y':
                    response = 1
                    await ctx.send("You have sent the bot a new command")
                    self.bot.client.get_user(self.bot.bot64id).send_message(steamcommand)
                elif choice == 'no' or choice == 'n':
                    response = 1
                    await ctx.send("You didn't send the command to the bot :(")
                else:
                    await ctx.send('Please try again with Y/N')


def setup(bot):
    bot.add_cog(SteamCog(bot))
