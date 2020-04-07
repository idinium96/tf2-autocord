from asyncio import sleep
from datetime import datetime
from json import loads
from os import remove
from re import findall

from discord import Colour, Embed, HTTPException
from discord.ext import commands, tasks

from Login_details import preferences

class Steam(commands.Cog):
    """Commands that are mainly owner restricted and only work if you are logged in to your Steam account"""

    def __init__(self, bot):
        self.bot = bot
        self.first = True

        self.discordcheck.start()

    def check(self, m):
        return m.author == self.bot.owner

    def cog_unload(self):
        self.discordcheck.cancel()
        self.user_message.cancel()

    async def classifieds(self, ctx, name):
        if isinstance(name, list):
            mul = 'these'
            mul2 = 'commands'
            dscontent = "`, `".join([item for item in name])
        else:
            mul = 'this'
            mul2 = 'command'
            dscontent = name
        await ctx.send(f'Do you want to send {mul} `{dscontent}` {mul2} to the bot?')
        while 1:
            choice = await self.bot.wait_for('message', check=self.check)
            choice = choice.content.lower()

            if choice == 'y' or choice == 'yes':
                await ctx.send(f'Sent {mul} {mul2} to the bot `{dscontent}`')
                async with ctx.typing():
                    if isinstance(name, list):
                        for message in name:
                            self.bot.s_bot.send_message(message)
                            await sleep(5)

                    if isinstance(name, str):
                        self.bot.s_bot.send_message(name)
                        await sleep(3)
                break

            elif choice == 'n' or choice == 'no':
                await ctx.send('The command hasn\'t been sent')
                break
            else:
                await ctx.send('Try Again')

    @tasks.loop(seconds=1)
    async def discordcheck(self):
        """The task that forwards messages from Steam to Discord"""
        if self.bot.user_message != 0:
            self.user_message.cancel()
            self.user_message.start()
        elif self.bot.sbotresp != 0:
            sbotresp = self.bot.sbotresp
            message = sbotresp
            if sbotresp.startswith('Trade '):
                embed = Embed(color=self.bot.color)

                ids = findall(r'\d+', sbotresp)
                trade_num = ids[0]
                trader_id = int(ids[1])
                trader = self.bot.client.get_user(trader_id)
                message = message.replace(f" #{trade_num}", "")
                if trader is not None:
                    message = message.replace(f'Trade with {trader_id} is',
                                              f'A trade with ||{trader.name}|| {trader.name} ({trader_id}) has been marked as')
                    message = message.replace(f" ||{trader.name}||", "")
                    message = message.replace('Summary:', '\n__Summary:__')
                    message = message.replace('Asked:', '- **Asked:**')
                    message = message.replace('Offered:', '- **Offered:**')
                    message = message.replace('Current key selling price:', '- **Current key selling price:**')
                    embed.set_author(name=f'Trade from: {trader.name}',
                                     url=trader.steam_id.community_url,
                                     icon_url=trader.get_avatar_url())
                embed.description = message
                embed.set_footer(text=f'Trade #{trade_num} • {datetime.now().strftime("%c")} UTC',
                                 icon_url=self.bot.user.avatar_url)
                await self.bot.channel_live_trades.send(embed=embed)
            
            elif sbotresp.startswith('Offer '):
                if 'not active' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
                elif 'not exist' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
                else:
                    embed = Embed(color=self.bot.color)
                    ownerID = preferences.owner_id
                    ids = findall(r'\d+', sbotresp)
                    offer_num = ids[0]
                    trader_id = int(ids[1])
                    trader = self.bot.client.get_user(trader_id)
                    message = message.replace(f" #{offer_num}", "")
                    if trader is not None:
                        message = message.replace(f'Offer from {trader_id} is waiting for review',
                                                  f'An offer (#{offer_num}) sent by ||{trader.name}|| {trader.name} ({trader_id}) is waiting for review')
                        message = message.replace(f" ||{trader.name}||", "")
                        message = message.replace('Summary:', '\n__Summary:__')
                        message = message.replace('Asked:', '- **Asked:**')
                        message = message.replace('Offered:', '- **Offered:**')
                        message = message.replace('Current key selling price:', '\nCurrent key selling price:')
                        embed.set_author(name=f'Offer from: {trader.name}',
                                         url=trader.steam_id.community_url,
                                         icon_url=trader.get_avatar_url())
                    embed.description = message
                    embed.set_footer(text=f'Offer #{offer_num} • {datetime.now().strftime("%c")} UTC',
                                     icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
                    await self.bot.channel_offer_review.send(f'<@!{ownerID}>, check this!')
                
            elif sbotresp.startswith('Declining '):
                embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('Accepting '):
                embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('❌There are '):
                if 'no active offers' in sbotresp:
                    embed = Embed(color=self.bot.color, title='No active offer', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('All trades '):
                embed = Embed(color=self.bot.color, title='Successful trades made statistic:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_trades_statistic.send(embed=embed)
            else:
                embed = Embed(color=self.bot.color, title='New Message:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} UTC', icon_url=self.bot.user.avatar_url)
                await self.bot.owner.send(embed=embed)
            self.bot.sbotresp = 0

    @tasks.loop(minutes=30)
    async def user_message(self):
        embed = Embed(color=Colour.dark_gold())
        if self.bot.messager:
            embed.set_author(name=f'Message from {self.bot.messager.name}',
                             url=self.bot.messager.steam_id.community_url,
                             icon_url=self.bot.messager.get_avatar_url())
        embed.add_field(name='User Message:',
                        value=f'You have a message from a user:\n> {self.bot.user_message.split(":", 1)[1]}'
                              f'\nType {self.bot.prefix}acknowledged if you have dealt with this', inline=False)
        self.bot.message = await self.bot.owner.send(embed=embed)
        if self.first:
            try:
                await self.bot.message.pin()
            except HTTPException:
                pass
            self.first = False

    @commands.command()
    @commands.is_owner()
    async def acknowledged(self, ctx):
        """Used to acknowledge a user message

        This is so user messages don't get lost in the channel history"""
        self.bot.user_message = 0
        self.user_message.stop()
        self.first = True
        try:
            await self.bot.message.unpin()
        except HTTPException:
            pass
        await ctx.send('Acknowledged the user\'s message')

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def add(self, ctx):
        """Add is used to add items from your bot's classifieds don't use an "=" between name and the item
        eg. `{prefix}add name The Team Captain`
        It allows the chaining of commands
        eg. `{prefix}add names This&intent=sell, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')
            await ctx.send_help(ctx.command)

    @add.command(name='name')
    async def a_name(self, ctx, *, name):
        """Handles singular classified additions"""
        name = f'{self.bot.addm}{name}'
        await self.classifieds(ctx, name)

    @add.command(name='names')
    async def a_names(self, ctx, *, name):
        """Handles multiple classified additions"""
        name = name.split(',')
        name = [f'{self.bot.addm}{x.strip()}' for x in name]
        await self.classifieds(ctx, name)

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def update(self, ctx):
        """Update is used to update items from your bot's classifieds don't use an "=" between name and the item
        eg. `{prefix}update name The Team Captain`
        It allows the chaining of commands
        eg. `{prefix}update names This&intent=bank, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')
            await ctx.send_help(ctx.command)

    @update.command(name='name')
    async def u_name(self, ctx, *, name):
        """Handles singular updates"""
        name = f'{self.bot.updatem}{name}'
        await self.classifieds(ctx, name)

    @update.command(name='names')
    async def u_names(self, ctx, *, name):
        """Handles multiple updates"""
        name = name.split(',')
        name = [f'{self.bot.updatem}{x.strip()}' for x in name]
        await self.classifieds(ctx, name)

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def remove(self, ctx):
        """Remove is used to remove items from your bot's classifieds don't use an "=" between item and the item
        eg. `{prefix}remove item The Team Captain`
        It allows the chaining of commands
        eg. `{prefix}remove items This&intent=bank, That, The other&quality=Strange`"""
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to pass in a type of refractory to perform')
            await ctx.send_help(ctx.command)

    @remove.command(name='item')
    async def r_item(self, ctx, *, name):
        """Handles singular removals"""
        name = f'{self.bot.removem}{name}'
        await self.classifieds(ctx, name)

    @remove.command(name='items')
    async def r_items(self, ctx, *, name):
        """Handles multiple removals"""
        name = name.split(',')
        name = [f'{self.bot.removem}{x.strip()}' for x in name]
        await self.classifieds(ctx, name)

    @commands.command(aliases=['p'])
    @commands.is_owner()
    async def profit(self, ctx):
        """Returns your bot's profit as it normally would"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}profit')
            await sleep(5)

    @commands.command()
    @commands.is_owner()
    async def send(self, ctx, *, message):
        """Send is used to send a message to the bot
        eg. `{prefix}send {prefix}message 76561198248053954 Get on steam`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(message)
            await ctx.send(f"Sent `{message}` to the bot")
            await sleep(3)

    @commands.command()
    @commands.is_owner()
    async def accepttrade(self, ctx, *, offerID):
        """accept trade offer that is in review
        eg. `{prefix}accepttrade <offerID>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}accepttrade {offerID}')
            await sleep(3)

    @commands.command()
    @commands.is_owner()
    async def declinetrade(self, ctx, *, offerID):
        """decline trade offer that is in review
        eg. `{prefix}declinetrade <offerID>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}declinetrade {offerID}')
            await sleep(3)

    @commands.command()
    @commands.is_owner()
    async def trade(self, ctx, *, offerID):
        """check trade offer that is in review
        eg. `{prefix}trade <offerID>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}trade {offerID}')
            await sleep(3)

    @commands.command()
    @commands.is_owner()
    async def trades(self, ctx):
        """check active trade offers that are in review
        eg. `{prefix}trades`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}trades')
            await sleep(3)

    @commands.command(aliases=['bp'])
    async def backpack(self, ctx):
        """Get a link to your inventory and your bot's"""
        embed = Embed(title='Backpack.tf', url='https://backpack.tf/',
                      description=f'[Your backpack](https://backpack.tf/profiles/{self.bot.client.user.steam_id})\n'
                                  f'[Your bot\'s backpack](https://backpack.tf/profiles/{self.bot.bot64id})',
                      color=0x58788F)
        embed.set_thumbnail(url='https://backpack.tf/images/tf-icon.png')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def cashout(self, ctx):
        """Want to cash-out all your listings? Be warned this command is quite difficult to fix once you run it"""
        listingsjson = loads(open(f'{self.bot.templocation}/listings.json', 'r').read())
        await ctx.send(f'Cashing out {len(listingsjson)} items, this may take a while')
        for value in listingsjson:
            command = f'{self.bot.updatem}{value["name"]}&intent=sell'
            self.bot.s_bot.send_message(command)
            await ctx.send(command)
            await sleep(3)
        await ctx.send('Completed the intent update')

    @commands.command(aliases=['raw_add', 'add-raw', 'raw-add'])
    @commands.is_owner()
    async def add_raw(self, ctx, *, ending=''):
        """Add lots of items, very volatile `{prefix}add names` is much more likely to be stable"""
        await ctx.send('Paste all the items you want to add on a new line, or attach a text file')
        file = await self.bot.wait_for('message', check=self.check)
        if file.content:
            items = file.content.splitlines()
        elif file.attachments:
            items = await file.attachments[0].read()
            items = items.decode().splitlines()
        else:
            return await ctx.send('What did you send?')
        for item in items:
            self.bot.s_bot.send_message(f'{self.bot.addm}{item}{ending}')
            await sleep(5)
        await ctx.send(f'Done adding {len(items)} items')
        if file.attachments:
            await sleep(10)
            remove(f'{self.bot.templocation}/raw_add_listings.txt')

    @commands.command()
    @commands.is_owner()
    async def scc(self, ctx):
        """SCC - Steam Command Creator is a worse version of Hackerino's command generator tool"""
        ngt1, ngt2, ngt3, ngt4, ngt5, ngt6, ngt7, ngt8, ngt9 = True
        escape = False

        scclist = '\n__You can change the:__\nPrice\nLimit\nQuality\nIntent\nCraftable\nAustralium\n' \
                  'Killstreak\nEffect\nAutopricing'
        intents = 'Bank, Buy or Sell'
        qualities = 'Unique, Strange, Vintage, Genuine, Haunted or Collector\'s'

        await ctx.send('What do you want to do?\nUpdate, Remove or Add?')
        response = 0
        while response == 0:
            choice = await self.bot.wait_for('message', check=self.check)
            choice = choice.content.lower()

            if choice == 'update' or choice == 'u' or choice == 'add' or choice == 'a' or choice == 'remove' or choice == 'r':
                if choice == 'update' or choice == 'u':
                    do = 'update'
                elif choice == 'add' or choice == 'a':
                    do = 'add'
                elif choice == 'remove' or choice == 'r':
                    do = 'remove'
                await ctx.send(f'What item do you want to {do}?')
                item_to_uar = await self.bot.wait_for('message', check=self.check)
                item_to_uar = item_to_uar.content
                steamcommand = item_to_uar

                if do == 'remove':
                    f'{self.bot.removem}{steamcommand}'
                else:
                    await ctx.send('Want to add prefixes?\nType yes or no')
                    while 1:
                        choice = await self.bot.wait_for('message', check=self.check)
                        choice = choice.content.lower()

                        if choice == 'yes' or choice == 'y':
                            await ctx.send(scclist)
                            while escape is False:
                                prefix = await self.bot.wait_for('message', check=self.check)
                                prefix = prefix.content.lower()

                                if prefix == 'price' or prefix == 'p' and ngt1:  # buy price prefix
                                    await ctx.send('Buy price in refined metal')
                                    bp = await self.bot.wait_for('message', check=self.check)
                                    bp = bp.content.lower()
                                    buy1 = f'&buy_metal={bp}'
                                    await ctx.send('Buy price in keys')
                                    bp = await self.bot.wait_for('message', check=self.check)
                                    bp = bp.content.lower()
                                    buy2 = f'&buy_keys={bp}'
                                    steamcommand += f'{buy1}{buy2}'

                                    await ctx.send('Sell price in refined metal')
                                    sp = await self.bot.wait_for('message', check=self.check)
                                    sp = sp.content.lower()
                                    sell1 = f'&sell_metal={sp}'
                                    await ctx.send('Sell price in keys')
                                    sp = await self.bot.wait_for('message', check=self.check)
                                    sp = sp.content.lower()
                                    sell2 = f'&sell_keys={sp}'
                                    steamcommand += f'{sell1}{sell2}'
                                    scclist = scclist.replace('\nPrice', '')
                                    ngt1 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'limit' or prefix == 'l' and ngt2:  # limit prefix
                                    await ctx.send('Max stock is')
                                    limit = await self.bot.wait_for('message', check=self.check)
                                    limit = limit.content.lower()
                                    steamcommand += f'&limit={limit}'
                                    scclist = scclist.replace('\nLimit', '')
                                    ngt2 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'quality' or prefix == 'q' and ngt3:  # quality prefix
                                    await ctx.send(f'Quality (enter {qualities})')
                                    while 1:
                                        quality = await self.bot.wait_for('message', check=self.check)
                                        quality = quality.content.lower()
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
                                    ngt3 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'intent' or prefix == 'i' and ngt4:  # intent prefix
                                    await ctx.send(f'Intent is to ({intents})')
                                    while 1:
                                        intent = await self.bot.wait_for('message', check=self.check)
                                        intent = intent.content.lower()
                                        if intent in intents.lower():
                                            steamcommand += f'&intent={intent}'
                                            break
                                        else:
                                            await ctx.send(f'Try again with a valid value ({intents})')
                                    scclist = scclist.replace('\nIntent', '')
                                    ngt4 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'craftable' or prefix == 'c' and ngt5:  # craftable prefix
                                    await ctx.send('Is the item craftable?')
                                    while 1:
                                        craftable = await self.bot.wait_for('message', check=self.check)
                                        craftable = craftable.content.lower()
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
                                    ngt5 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'australium' or prefix == 'au' and ngt6:  # australium prefix
                                    await ctx.send('Is the item australium?')
                                    while 1:
                                        australium = await self.bot.wait_for('message', check=self.check)
                                        australium = australium.content.lower()
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
                                    ngt6 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'killstreak' or prefix == 'k' and ngt7:  # killstreak prefix
                                    await ctx.send(
                                        'Is the item killstreak (Killstreak (1), Specialized (2) or Professional (3))')
                                    while 1:
                                        killstreak = await self.bot.wait_for('message', check=self.check)
                                        killstreak = killstreak.content.lower()
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
                                    ngt7 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'effect' or prefix == 'e' and ngt8:  # effect suffix
                                    await ctx.send('What is the unusual effect? E.g Burning Flames')
                                    suffix = await self.bot.wait_for('message', check=self.check)
                                    effect = suffix.content
                                    if do == 'update':
                                        steamcommand = f'{effect}{steamcommand}'
                                    elif do == 'add':
                                        steamcommand += f'&effect={effect}'
                                    scclist = scclist.replace('\nEffect', '')
                                    ngt8 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')

                                elif prefix == 'autoprice' or prefix == 'ap' and ngt9:  # effect suffix
                                    await ctx.send('Is autoprice enabled?')
                                    while 1:
                                        suffix = await self.bot.wait_for('message', check=self.check)
                                        autoprice = suffix.content.lower()
                                        if autoprice == 't' or autoprice == 'true' or autoprice == 'y' \
                                                or autoprice == 'yes' or autoprice == 'f' or autoprice == 'false' \
                                                or autoprice == 'n' or autoprice == 'no':
                                            steamcommand += f'&autoprice={autoprice}'
                                            break
                                        else:
                                            await ctx.send('Try again with a valid value (Y/N or T/F)')

                                    scclist = scclist.replace('\nAutopricing', '')
                                    ngt9 = False
                                    await ctx.send(
                                        f'Want to add more options to your command from the list: {scclist}\nIf not type escape')
                                    break

                                elif prefix == 'escape' or prefix == 'esc':
                                    escape = True

                                else:
                                    await ctx.send('Try again this time with something in the list')
                            if do == 'update':
                                steamcommand = f'{self.bot.updatem}{steamcommand}'
                            elif do == 'add':
                                steamcommand = f'{self.bot.addm}{steamcommand}'
                            break

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
                choice = choice.content.lower()

                if choice == 'yes' or choice == 'y':
                    await ctx.send("You have sent the bot a new command")
                    self.bot.s_bot.send_message(steamcommand)
                    return
                elif choice == 'no' or choice == 'n':
                    await ctx.send("You didn't send the command to the bot :(")
                    return
                else:
                    await ctx.send('Please try again with y/n')


def setup(bot):
    bot.add_cog(Steam(bot))
