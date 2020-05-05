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
                    message = message.replace('Offer Summary:', '__Offer Summary:__')
                    message = message.replace('Asked:', '- **Asked:**')
                    message = message.replace('Offered:', '- **Offered:**')
                    message = message.replace('Current key selling price:', '- **Current key selling price:**')
                    embed.set_author(name=f'Trade from: {trader.name}',
                                     url=trader.steam_id.community_url,
                                     icon_url=trader.get_avatar_url())
                embed.description = message
                embed.set_footer(text=f'Trade #{trade_num} • {datetime.now().strftime("%c")} {preferences.yourTimeZone}',
                                 icon_url=self.bot.user.avatar_url)
                await self.bot.channel_live_trades.send(embed=embed)
            
            elif sbotresp.startswith('Offer '):
                if 'not active' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
                elif 'not exist' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
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
                    embed.set_footer(text=f'Offer #{offer_num} • {datetime.now().strftime("%c")} {preferences.yourTimeZone}',
                                     icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
                    await self.bot.channel_offer_review.send(f'<@!{ownerID}>, check this!')

            elif sbotresp.startswith("You've got "):
                embed = Embed(color=self.bot.color)
                ownerID = preferences.owner_id
                ids = findall(r'\d+', sbotresp)
                trader_id = int(ids[0])
                trader = self.bot.client.get_user(trader_id)
                message = message.replace(f" # {trader_id} :", "")
                if trader is not None:
                    message = message.replace(f"You've got a message from ",f"💬||{trader.name}|| {trader.name}: ")
                    message = message.replace(f"||{trader.name}||", "")
                    embed.set_author(name=f'Message from: {trader.name}',
                                     url=trader.steam_id.community_url,
                                     icon_url=trader.get_avatar_url())
                embed.description = message
                embed.set_footer(text=f'Steam ID - #{trader_id} • {datetime.now().strftime("%c")} {preferences.yourTimeZone}',
                                 icon_url=self.bot.user.avatar_url)
                await self.bot.channel_message.send(embed=embed)
                await self.bot.channel_message.send(f'<@!{ownerID}>, New Message!')

            elif sbotresp.startswith ('Other admins'):
                if 'sent a message' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Message system info', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_message.send(embed=embed)

            elif sbotresp.startswith ('Your '):
                if 'message has been' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Message system info', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_message.send(embed=embed)
            
            elif sbotresp.startswith ('I am not '):
                if 'friends with the user' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Message system info', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_message.send(embed=embed)
            
            elif sbotresp.startswith('Declining '):
                embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('Accepting '):
                embed = Embed(color=self.bot.color, title='Offer review status:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('🧾There is '):
                if 'can review' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Active offer(s):', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('There is '):
                if 'can review' in sbotresp:
                    embed = Embed(color=self.bot.color, title='Active offer(s):', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
            
            elif sbotresp.startswith('❌There are '):
                if 'no active offers' in sbotresp:
                    embed = Embed(color=self.bot.color, title='No active offer', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)

            elif sbotresp.startswith('There are '):
                if 'no active offers' in sbotresp:
                    embed = Embed(color=self.bot.color, title='No active offer', description=sbotresp)
                    embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                    await self.bot.channel_offer_review.send(embed=embed)
            
            elif sbotresp.startswith('All trades '):
                embed = Embed(color=self.bot.color, title='Successful trades made statistic:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                await self.bot.channel_trades_statistic.send(embed=embed)
            else:
                embed = Embed(color=self.bot.color, title='New Message:', description=sbotresp)
                embed.set_footer(text=f'• {datetime.now().strftime("%c")} {preferences.yourTimeZone}', icon_url=self.bot.user.avatar_url)
                await self.bot.owner.send(embed=embed)
            self.bot.sbotresp = 0

    @tasks.loop(minutes=10)
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

    @commands.command()
    @commands.is_owner()
    async def get(self, ctx, *, sku):
        """Get raw information about a pricelist entry
        eg. `{prefix}get sku=<item's sku>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}get {sku}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, *, skuAndParameter):
        """Add a pricelist entry
        eg. `{prefix}add sku=<item's sku>&intent=bank`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}add {skuAndParameter}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, *, sku):
        """Remove a pricelist entry
        eg. `{prefix}remove sku=<item's sku>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}remove {sku}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx, *, skuAndParameter):
        """Update a pricelist entry
        eg. `{prefix}update sku=<item's sku>&intent=bank`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}update {skuAndParameter}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def pricecheck(self, ctx, *, sku):
        """Requests an item to be priced by PricesTF
        eg. `{prefix}pricecheck sku=<item's sku>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}pricecheck {sku}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def expand(self, ctx, *, craftableFalseOrTrue):
        """Uses Backpack Expanders to increase the inventory limit
        eg. `{prefix}expand craftable=false|true`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}expand {craftableFalseOrTrue}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def stop(self, ctx):
        """Stop the bot
        eg. `{prefix}stop`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}stop')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Restart the bot
        eg. `{prefix}restart`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}restart')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def version(self, ctx):
        """Get version that the bot is running
        eg. `{prefix}version`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}version')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def avatar(self, ctx, *, avatarURL):
        """Change avatar
        eg. `{prefix}avatar <avatar_url>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}avatar {avatarURL}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def name(self, ctx, *, newName):
        """Change name
        eg. `{prefix}name <New name>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}name {newName}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def stats(self, ctx):
        """Get statistics for accepted trades
        eg. `{prefix}stats`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}stats')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def message(self, ctx, *, steamID, yourMessage):
        """Send a message to a user
        eg. `{prefix}message <steamID> <your Message>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}message {SteamID} {yourMessage}')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def rate(self, ctx):
        """Get current key prices
        eg. `{prefix}rate`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}rate')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def stock(self, ctx):
        """Get a list of items that the bot has
        eg. `{prefix}stock`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}stock')
            await sleep(3)
    
    @commands.command()
    @commands.is_owner()
    async def price(self, ctx, *, itemName):
        """Get the price and stock of an item
        eg. `{prefix}price <Item Name>`"""
        async with ctx.typing():
            self.bot.s_bot.send_message(f'{self.bot.prefix}price {itemName}')
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

def setup(bot):
    bot.add_cog(Steam(bot))
