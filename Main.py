import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
from steam.client import SteamClient
from steam.enums import EResult
import logging
import discord
from discord.ext import commands, tasks
import asyncio
import time
import datetime
import threading
import json

# read details ---------------------------------------------------------------------------------------------------------

with open("Login details/sensitive details.json", "r") as f:  # reads your details
    login = f.read()
    login = json.loads(login)
    token = login["Bot Token"]
    global username
    global password
    username = login["Username"]
    password = login["Password"]

with open('Login details/preferences.json', 'r') as f:
    preferences = f.read()
    preferences = json.loads(preferences)
    owner_id = int(preferences["Discord ID"])
    global bot64id
    bot64id = preferences["Bot's Steam ID"]
    owner_name = preferences["Owner Name"]
    global command_prefix
    command_prefix = preferences["Command Prefix"]
    color = int(preferences["Embed Colour"], 16)

# main program ---------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix=command_prefix)
bot.remove_command('help')

updatem = command_prefix + 'update name='
removem = command_prefix + 'remove item='
addm = command_prefix + 'add name='

sbotresp = 0
logged_on = 0
version = 'V.0.2'

activity = owner_name + "'s trades and for " + command_prefix
activity = discord.Activity(name=activity, type=discord.ActivityType.watching)

tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()  # makes the time zone variable
if 'Summer Time' in tz:
    tz = tz.replace(' Summer Time', '')
elif 'Daylight Saving Time' in tz:
    tz = tz.replace(' Daylight Saving Time', '')
offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
offset = str(offset / 60 / 60 * -1)
offset = '+' + offset[:-2]
tz = tz + offset


def getcurrenttime():
    global currenttime
    currenttime = time.asctime()
    currenttime = currenttime[11:-8]


# DM's -----------------------------------------------------------------------------------------------------------------


@bot.event
async def on_ready():
    await bot.change_presence(activity=activity)
    bgcheck.start()
    print("Bot is ready")
    print('Logged in as', bot.user.name, '\nYou are using the premium version of this code, thanks ;) This is: ' + version)
    await bot.get_user(owner_id).send('I\'m Online and dealing with your trade notifications :)')
    while logged_on == 0:
        await bot.get_user(owner_id).send('Please know you aren\'t logged into steam'
                                          '\nTo do that type in your 2FA code into the console.')
        await asyncio.sleep(60)


@tasks.loop(seconds=10, count=None)
async def bgcheck():
    global sbotresp
    if sbotresp != 0:
        await bot.get_user(owner_id).send(sbotresp)
        sbotresp = 0
    else:
        pass


# toggle commands ------------------------------------------------------------------------------------------------------


toggleprofit = 0
@bot.command()
async def togprofit(ctx, profittime="23:59"):
    global toggleprofit
    if toggleprofit == 0:
        toggleprofit = 1
        await ctx.send('Profit Alerts now toggled on this will send you profit at ' + profittime + ' ' + tz)
    elif toggleprofit == 1:
        toggleprofit = 0
        await ctx.send('Profit Alerts now toggled off')

    while toggleprofit == 1:
        getcurrenttime()
        if profittime == currenttime:
            client.get_user(bot64id).send_message(command_prefix + 'profit')
            await ctx.send('You have made ' + str(sbotresp))
            await asyncio.sleep(61)

        elif currenttime != profittime:
            await asyncio.sleep(5)


@bot.command()
async def togpremium(ctx):
    global togglepremium
    if togglepremium == 0:
        togglepremium = 1
        await ctx.send('Premium Alerts now toggled on (this will send you a message when 1 months and 29 days have gone past)')
    elif togglepremium == 1:
        togglepremium = 0
        await ctx.send('Premium Alerts now toggled off')

    while togglepremium == 1:
        await asyncio.sleep(4654687)  # 2 months in seconds - 1 day = 4654687 seconds
        await ctx.send('You may wish to renew your premium subscription')


# help -----------------------------------------------------------------------------------------------------------------


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=" ", color=color)
    embed.set_author(name='Help')
    embed.add_field(name=command_prefix + 'help', value='Brings up this message', inline=True)
    embed.add_field(name=command_prefix + 'info',
                    value='Gives important information about the bot', inline=True)
    embed.add_field(name=command_prefix + 'scc', value='Creates a Steam chat command to send to the bot', inline=False)
    embed.add_field(name=command_prefix + 'togprofit',
                    value='Toggles on or off the  message sent at the end of every day giving the days profit',
                    inline=True)
    embed.add_field(name=command_prefix + 'togpremium',
                    value='Toggles on or off the time for alerts for when bp.tf premium is going to run out',
                    inline=True)
    embed.add_field(name=command_prefix + 'add/update/remove/profit',
                    value='Send commands to your bot they allow chaining of commands', inline=False)
    embed.add_field(name=command_prefix + 'send [message to send]',
                    value='Allows you to send anything to your Steam bot', inline=False)
    embed.add_field(name=command_prefix + 'get [filename in temp]',
                   value='Gets files from your bot\'s temp folder', inline=False)
    embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
    await ctx.send(embed=embed)


@bot.command()
async def info(ctx):
    embed = discord.Embed(title=version, color=color)
    embed.set_author(name="Info about this bot")
    embed.add_field(name='Command prefix', value='Your command prefix is (' + command_prefix + '). Type '
                                                 + command_prefix + 'help to list the commands you can use',
                    inline=False)
    embed.add_field(name='About the bot',
                    value='It was coded in python to help you manage your tf2automtic bot. DM me with any '
                          'suggestions or features you would like on this bot', inline=False)
    embed.add_field(name='Thanks',
                    value='If you are running this that means you bought the premium version of the code, Thanks', inline=False)
    embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
    await ctx.send(embed=embed)

# normal ---------------------------------------------------------------------------------------------------------------


@bot.command()
async def get(ctx, *, file: str):
    if 'history' or 'listings' in file:
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


@bot.command()
async def add(ctx, *, content: str):
    channel = ctx.message.channel
    if 'names=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [addm + x for x in content]

    elif 'name=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = addm + msgs

    dscontent = str(content)
    dscontent = dscontent.replace('[', '')
    dscontent = dscontent.replace(']', '')
    await ctx.send('Do you want to send ' + mul + dscontent + mul2 + 'to the bot?')
    response = 0
    while response == 0:
        def check(m):
            return m.content and m.channel == channel

        choice = await bot.wait_for('message', check=check)
        choice = choice.clean_content.lower()

        if choice == 'y' or choice == 'yes':
            response = 1
            await ctx.send('Sent ' + mul + 'messages to the bot ' + dscontent)
            global botresp
            botresp = False
            while botresp == False:
                async with ctx.typing():
                    global storeresp
                    storeresp = 1
                    await asyncio.sleep(5)
                    nsend = 0
                    while nsend < len(content):
                        client.get_user(bot64id).send_message(content[nsend])
                        nsend += 1
                        await asyncio.sleep(3)
                        await ctx.send(sbotresp)

                    botresp = True


        elif choice == 'n' or choice == 'no':
            await ctx.send("The command hasn't been sent")
            response = 1
        else:
            await ctx.send('Try Again')


@bot.command()
async def update(ctx, *, content: str):
    channel = ctx.message.channel
    if 'names=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [updatem + x for x in content]

    elif 'name=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = updatem + msgs

    dscontent = str(content)
    dscontent = dscontent.replace('[', '')
    dscontent = dscontent.replace(']', '')
    await ctx.send('Do you want to send ' + mul + dscontent + mul2 + 'to the bot?')
    response = 0
    while response == 0:
        def check(m):
            return m.content and m.channel == channel

        choice = await bot.wait_for('message', check=check)
        choice = choice.clean_content.lower()

        if choice == 'y' or choice == 'yes':
            response = 1
            await ctx.send('Sent ' + mul + 'messages to the bot ' + dscontent)
            global botresp
            botresp = False
            while botresp == False:
                async with ctx.typing():
                    global storeresp
                    storeresp = 1
                    await asyncio.sleep(5)
                    nsend = 0
                    while nsend < len(content):
                        client.get_user(bot64id).send_message(content[nsend])
                        nsend += 1
                        while sbotresp is not None:
                            await ctx.send(sbotresp)
                    botresp = True

        elif choice == 'n' or choice == 'no':
            response = 1
            await ctx.send("The command hasn't been sent")

        else:
            await ctx.send('Try Again')


@bot.command()
async def remove(ctx, *, content: str):
    channel = ctx.message.channel
    if 'items=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [removem + x for x in content]

    elif 'item=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = removem + msgs
    dscontent = str(content)
    dscontent = dscontent.replace('[', '')
    dscontent = dscontent.replace(']', '')
    await ctx.send('Do you want to send ' + mul + dscontent + mul2 + 'to the bot?')
    response = 0
    while response == 0:
        def check(m):
            return m.content and m.channel == channel

        choice = await bot.wait_for('message', check=check)
        choice = choice.clean_content.lower()

        if choice == 'y' or choice == 'yes':
            await ctx.send('Sent ' + mul + 'messages to the bot ' + dscontent)
            global botresp
            botresp = False
            while botresp == False:
                async with ctx.typing():
                    global storeresp
                    storeresp = 1
                    await asyncio.sleep(5)
                    nsend = 0
                    while nsend < len(content):
                        client.get_user(bot64id).send_message(content[nsend])
                        nsend += 1
                        await asyncio.sleep(3)
                        await ctx.send(sbotresp)
                        sbotresp = None

                    botresp = True


        elif choice == 'n' or choice == 'no':
            await ctx.send("The command hasn't been sent")
            response = 1
        else:
            await ctx.send('Try Again')


@bot.command()
async def profit(ctx):
    global botresp
    botresp = False
    while botresp is False:
        async with ctx.typing():
            global storeresp
            storeresp = 1
            client.get_user(bot64id).send_message(command_prefix + 'profit')
            await asyncio.sleep(3)
            await ctx.send(sbotresp)
            sbotresp = None
            botresp = True


@bot.command()
async def send(ctx, *, content: str):
    global storeresp
    storeresp = 1
    client.get_user(bot64id).send_message(content)
    await ctx.send("Sent '" + content + "' to the bot")

# scc ------------------------------------------------------------------------------------------------------------------


@bot.command()
async def scc(ctx):
    channel = ctx.message.channel
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

    scclist = '\n__You can change the:__\nPrice\nLimit\nQuality\nIntent\nCraftable\nAustralium\nKillstreak\nEffect\nAutopricing'
    intents = 'Bank, Buy or Sell'
    qualities = 'Unique, Strange, Vintage, Genuine, Haunted or Collector\'s'

    def check(m):
        return m.content and m.channel == channel

    await ctx.send('What do you want to do?\nUpdate, Remove or Add?')
    response = 0
    while response == 0:
        choice = await bot.wait_for('message', check=check)
        choice = choice.clean_content.lower()

# remove ---------------------------------------------------------------------------------------------------------------

        if choice == 'remove' or choice == 'r':
            response = 1
            do = 'remove '
            await ctx.send('What do you want to remove?')
            item_to_uar = await bot.wait_for('message', check=check)
            item_to_uar = item_to_uar.clean_content
            steamcommand = removem + item_to_uar

# update ---------------------------------------------------------------------------------------------------------------

        elif choice == 'update' or choice == 'u':
            do = 'update '
            await ctx.send('What items do you want to update?')
            item_to_uar = await bot.wait_for('message', check=check)
            item_to_uar = item_to_uar.clean_content
            steamcommand = item_to_uar
            await ctx.send('Want to add prefixes?\nType yes or no')
            response = 0
            while response == 0:
                choice = await bot.wait_for('message', check=check)
                choice = choice.clean_content.lower()

                if choice == 'yes' or choice == 'y':
                    response = 1
                    await ctx.send(scclist)
                    prefixes = 0
                    while prefixes != 9:
                        response = 0
                        while response == 0:
                            prefix = await bot.wait_for('message', check=check)
                            prefix = prefix.clean_content.lower()

                            if prefix == 'price' or prefix == 'p' and notgonethrough is True:  # buy price prefix
                                await ctx.send('Buy price in refined metal')
                                bp = await bot.wait_for('message', check=check)
                                bp = bp.clean_content.lower()
                                buy1 = '&buy_metal=' + bp
                                await ctx.send('Buy price in keys')
                                bp = await bot.wait_for('message', check=check)
                                bp = bp.clean_content.lower()
                                buy2 = '&buy_keys=' + bp
                                steamcommand = steamcommand + buy1 + buy2

                                await ctx.send('Sell price in refined metal')
                                sp = await bot.wait_for('message', check=check)
                                sp = sp.clean_content.lower()
                                sell1 = '&sell_metal=' + sp
                                await ctx.send('Sell price in keys')
                                sp = await bot.wait_for('message', check=check)
                                sp = sp.clean_content.lower()
                                sell2 = '&sell_keys=' + sp
                                steamcommand = steamcommand + sell1 + sell2
                                prefixes += 1
                                scclist = scclist.replace('\nPrice', '')
                                notgonethrough1 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'limit' or prefix == 'l' and notgonethrough1 is True:  # limit prefix
                                await ctx.send('Max stock is')
                                limit = await bot.wait_for('message', check=check)
                                limit = limit.clean_content.lower()
                                limit = '&limit=' + limit
                                steamcommand = steamcommand + limit
                                prefixes += 1
                                scclist = scclist.replace('\nLimit', '')
                                notgonethrough1 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'quality' or prefix == 'q' and notgonethrough2 is True:  # quality prefix
                                await ctx.send('Quality (enter ' + qualities + ')')
                                response = 0
                                while response == 0:
                                    quality = await bot.wait_for('message', check=check)
                                    quality = quality.clean_content.lower()
                                    if quality in qualities.replace(',', '').lower():
                                        steamcommand = quality + ' ' + steamcommand
                                        response = 1
                                    else:
                                        await ctx.send('Try again with a valid value (' + qualities + ')')
                                prefixes += 1
                                scclist = scclist.replace('\nQuality', '')
                                notgonethrough2 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'intent' or prefix == 'i' and notgonethrough3 is True:  # intent prefix
                                await ctx.send('Intent is to (' + intents + ')')
                                response = 0
                                while response == 0:
                                    intent = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'craftable' or prefix == 'c' and notgonethrough4 is True:  # craftable prefix
                                await ctx.send('Is the item craftable?')
                                response = 0
                                while response == 0:
                                    craftable = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'australium' or prefix == 'au' and notgonethrough5 is True:  # australium prefix
                                await ctx.send('Is the item australium?')
                                response = 0
                                while response == 0:
                                    australium = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'killstreak' or prefix == 'k' and notgonethrough6:  # killstreak prefix
                                await ctx.send(
                                    'Is the item killstreak (Killstreak (1), Specialized (2) or Professional (3))')
                                response = 0
                                while response == 0:
                                    killstreak = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'effect' or prefix == 'e' and notgonethrough7:  # effect suffix
                                await ctx.send('What is the unusual effect? E.g Burning Flames')
                                suffix = await bot.wait_for('message', check=check)
                                effect = suffix.clean_content
                                steamcommand = effect + steamcommand
                                scclist = scclist.replace('\nEffect', '')
                                notgonethrough7 = False
                                prefixes += 1
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif prefix == 'autoprice' or prefix == 'ap' and notgonethrough8:  # effect suffix
                                await ctx.send('Is autoprice enabled')
                                response = 0
                                while response == 0:
                                    suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')


                            elif prefix == 'escape' or prefix == 'esc':
                                response = 1
                                steamcommand = updatem + steamcommand
                                prefixes = 9

                            else:
                                await ctx.send('Try again this time with something in the list')

                elif choice == 'no' or choice == 'n':
                    steamcommand = updatem + steamcommand
                    response = 1

                else:
                    await ctx.send('Please try again')

# add ------------------------------------------------------------------------------------------------------------------

        elif choice == 'add' or choice == 'a':
            do = 'add '
            await ctx.send('What item do you want to add to your classifieds?')
            response = 0
            while response == 0:
                item_to_uar = await bot.wait_for('message', check=check)
                item_to_uar = item_to_uar.clean_content
                steamcommand = item_to_uar

                await ctx.send('Want to add suffixes?\nType yes or no')

                choice = await bot.wait_for('message', check=check)
                choice = choice.clean_content.lower()
                if choice == 'yes' or choice == 'y':
                    await ctx.send(scclist)
                    suffixes = 0
                    while suffixes != 9:
                        response = 0
                        while response == 0:
                            suffix = await bot.wait_for('message', check=check)
                            suffix = suffix.clean_content

                            if suffix == 'p' or suffix == 'price' and notgonethrough is True:  # buy price suffix
                                await ctx.send('Buy price in refined metal')
                                suffix = await bot.wait_for('message', check=check)
                                bp = suffix.clean_content
                                buy1 = '&buy_metal=' + bp
                                await ctx.send('Buy price in keys')
                                bp = await bot.wait_for('message', check=check)
                                bp = bp.clean_content
                                buy2 = '&buy_keys=' + bp
                                steamcommand = steamcommand + buy1 + buy2

                                await ctx.send('Sell price in refined metal')
                                sp = await bot.wait_for('message', check=check)
                                sp = sp.clean_content
                                sell1 = '&sell_metal=' + sp
                                await ctx.send('Sell price in keys')
                                sp = await bot.wait_for('message', check=check)
                                sp = sp.clean_content
                                sell2 = '&sell_keys=' + sp
                                steamcommand = steamcommand + sell1 + sell2
                                suffixes += 1
                                scclist = scclist.replace('\nPrice', '')
                                notgonethrough = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'limit' or suffix == 'l' and notgonethrough1 is True:  # limit suffix
                                await ctx.send('Max stock is (enter a number)')
                                suffix = await bot.wait_for('message', check=check)
                                limit = suffix.clean_content
                                limit = '&limit=' + limit
                                steamcommand = steamcommand + limit
                                suffixes += 1
                                scclist = scclist.replace('\nLimit', '')
                                notgonethrough1 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'quality' or suffix == 'q' and notgonethrough2 is True:  # quality suffix
                                await ctx.send('Quality (enter ' + qualities + ')')
                                response = 0
                                while response == 0:
                                    suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'intent' or suffix == 'i' and notgonethrough3 is True:  # intent suffix
                                await ctx.send('Intent (enter ' + intents + ')')
                                response = 0
                                while response == 0:
                                    suffix = await bot.wait_for('message', check=check)
                                    intent = suffix.clean_content
                                    if intent in intents.lower():
                                        intent = '&intent=' + intent
                                        steamcommand = steamcommand + intent
                                    else:
                                        await ctx.send('Try again with a valid value (' + intents + ')')
                                suffixes = suffixes + 1
                                scclist = scclist.replace('\nIntent', '')
                                notgonethrough3 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'craftable' or suffix == 'c' and notgonethrough4 is True:  # craftable suffix
                                await ctx.send('Is the item craftable?')
                                suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'australium' or suffix == 'au' and notgonethrough5 is True:  # australium suffix
                                await ctx.send('Is the item australium (True or False)')
                                suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'killstreak' or suffix == 'k' and notgonethrough6 is True:  # killstreak suffix
                                await ctx.send('Is the item killstreak/specialized/professional?')
                                response = 0
                                while response == 0:
                                    suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'effect' or suffix == 'e' and notgonethrough7 is True:  # effect suffix
                                await ctx.send('What is the unusual effect? E.g Burning Flames')
                                suffix = await bot.wait_for('message', check=check)
                                effect = suffix.clean_content
                                effect = '&effect=' + effect
                                steamcommand = steamcommand + effect
                                suffixes += 1
                                scclist = scclist.replace('\nEffect', '')
                                notgonethrough7 = False
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'autoprice' or suffix == 'ap' and notgonethrough8 is True:  # effect suffix
                                await ctx.send('Is autoprice enabled')
                                response = 0
                                while response == 0:
                                    suffix = await bot.wait_for('message', check=check)
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
                                await ctx.send('Want to add more prefixes from the list:' + scclist + '\nIf not type escape')

                            elif suffix == 'escape' or suffix == 'esc':
                                steamcommand = addm + steamcommand
                                response = 1
                                suffixes = 9

                            else:
                                await ctx.send('Try again this time with something in the list' + scclist)

                elif choice == 'no' or choice == 'n':
                    response = 1
                    steamcommand = addm + steamcommand

                else:
                    await ctx.send('Please try again')

        else:
            await ctx.send('Please try again with Update/Add/Remove')

# sending msgs ---------------------------------------------------------------------------------------------------------

        await ctx.send('Command to ' + do + item_to_uar + ' is `' + steamcommand + '`')
        await ctx.send('Do you want to send the command to the bot?\nType yes or no')
        response = 0
        while response == 0:
            choice = await bot.wait_for('message', check=check)
            choice = choice.clean_content.lower()

            if choice == 'yes' or choice == 'y':
                response = 1
                await ctx.send("You have sent the bot a new command")
                await ctx.send("The bot sent back:")
                global botresp
                botresp = False
                while botresp == False:
                    async with ctx.typing():
                        client.get_user(bot64id).send_message(steamcommand)
                        while sbotresp is not None:
                            await ctx.send(sbotresp)
                            sbotresp = None
                            botresp = True
            elif choice == 'no' or choice == 'n':
                response = 1
                await ctx.send("You didn't send the command to the bot :(")
            else:
                await ctx.send('Please try again with Y/N')

# threading ------------------------------------------------------------------------------------------------------------


def discordside():
    bot.run(token)


def steamside():
    logging.basicConfig(format="%(asctime)s | %(message)s", level=logging.INFO)
    LOG = logging.getLogger()

    global client
    client = SteamClient()
    client.set_credential_location("Login Details/")  # where to store sentry files and other stuff  

    @client.on("error")
    def handle_error(result):
        LOG.info("Logon result: %s", repr(result))

    @client.on("connected")
    def handle_connected():
        LOG.info("Connected to %s", client.current_server_addr)

    @client.on("reconnect")
    def handle_reconnect(delay):
        LOG.info("Reconnect in %ds...", delay)

    @client.on("disconnected")
    def handle_disconnect():
        LOG.info("Disconnected.")

        if client.relogin_available:
            LOG.info("Reconnecting...")
            client.reconnect(maxdelay=30)

    @client.on("logged_on")
    def handle_after_logon():
        global logged_on
        logged_on = 1
        LOG.info("-" * 30)
        LOG.info("Logged on as: %s", client.user.name)
        LOG.info("Community profile: %s", client.steam_id.community_url)
        LOG.info("Last logon: %s", client.user.last_logon)
        LOG.info("Last logoff: %s", client.user.last_logoff)
        LOG.info("-" * 30)

    @client.on("chat_message")
    def handle_message(user, message_text):
        if user.steam_id == bot64id:
            global sbotresp
            global botresp
            global usermessage
            sbotresp = message_text
            botresp = True
        else:
            pass

    result = client.cli_login(username=username, password=password)
    if result != EResult.OK:
        LOG.info("Failed to login: %s" % repr(result))
        raise SystemExit

    client.run_forever()


t1 = threading.Thread(target=discordside)
t2 = threading.Thread(target=steamside)

t1.start()
t2.start()
