import gevent.monkey

gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
from steam import guard
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
    username = login["Username"]
    password = login["Password"]
    secrets = {
        "identity_secret": login["identity_secret"],
        "shared_secret": login["shared_secret"]
    }

with open('Login details/preferences.json', 'r') as f:
    preferences = f.read()
    preferences = json.loads(preferences)
    owner_id = int(preferences["Discord ID"])
    global bot64id
    bot64id = int(preferences["Bot's Steam ID"])
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
usermessage = 0
version = 'V.0.3.5'
botresp = False
dsdone = 0

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
    print('Logged in as', bot.user.name,
          '\nYou are using the premium version of this code, thanks ;) This is: ' + version)
    await bot.get_user(owner_id).send('I\'m Online and dealing with your trade notifications :)')
    global dsdone
    dsdone = 1
    await asyncio.sleep(30)
    while logged_on == 0:
        await bot.get_user(owner_id).send('Please remember you aren\'t logged into steam'
                                          '\nTo do that type in your 2FA code into the console.')
        await asyncio.sleep(60)


@tasks.loop(seconds=10)
async def bgcheck():
    global sbotresp
    global usermessage
    global botresp
    if botresp == True:
        await bot.get_user(owner_id).send(sbotresp)
        if usermessage != 0:
            await bot.get_user(owner_id).send(
                'You have a message from a user:\n' + usermessage + '\nType ' + command_prefix + 'acknowledged')
        botresp = False


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
                    value='If you are running this that means you bought the premium version of the code, Thanks',
                    inline=False)
    embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
    await ctx.send(embed=embed)


# normal ---------------------------------------------------------------------------------------------------------------

@bot.command()
async def add(ctx, *, content: str):
    channel = ctx.message.channel
    string = 0
    list = 0
    if 'names=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [addm + x for x in content]
        list = 1

    elif 'name=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = addm + msgs
        string = 1

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
                    await asyncio.sleep(5)
                    nsend = 0
                    if list == 1:
                        while nsend < len(content):
                            client.get_user(bot64id).send_message(content[nsend])
                            nsend += 1
                            await asyncio.sleep(3)
                            await ctx.send(sbotresp)

                    if string == 1:
                        client.get_user(bot64id).send_message(content)
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
    list = 0
    string = 0
    if 'names=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [updatem + x for x in content]
        list = 1

    elif 'name=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = updatem + msgs
        string = 1

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
                    await asyncio.sleep(5)
                    nsend = 0
                    if list == 1:
                        while nsend < len(content):
                            client.get_user(bot64id).send_message(content[nsend])
                            nsend += 1
                            await asyncio.sleep(3)
                            await ctx.send(sbotresp)

                    if string == 1:
                        client.get_user(bot64id).send_message(content)
                        await asyncio.sleep(3)
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
    list = 0
    string = 0
    if 'items=' in content:
        mul = 'these '
        mul2 = ' commands '
        msgs = content[6:]
        content = msgs.split(', ')
        content = [removem + x for x in content]
        list = 1

    elif 'item=' in content:
        mul = 'this '
        mul2 = ' command '
        msgs = content[5:]
        content = removem + msgs
        string = 1

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
                    await asyncio.sleep(5)
                    nsend = 0
                    if list == 1:
                        while nsend < len(content):
                            client.get_user(bot64id).send_message(content[nsend])
                            nsend += 1
                            await asyncio.sleep(3)
                            await ctx.send(sbotresp)

                    if string == 1:
                        client.get_user(bot64id).send_message(content)
                        await asyncio.sleep(3)
                        await ctx.send(sbotresp)

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
            sbotresp = ''
            botresp = True


@bot.command()
async def send(ctx, *, content: str):
    global storeresp
    storeresp = 1
    client.get_user(bot64id).send_message(content)
    await ctx.send("Sent '" + content + "' to the bot")


# threading ------------------------------------------------------------------------------------------------------------


def discordside():
    bot.run(token)


def steamside():
    global dsdone
    while 1:
        while dsdone != 0:
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
                global sbotresp
                global botresp
                global usermessage
                if user.steam_id == bot64id:
                    sbotresp = message_text
                    botresp = True
                    if 'from user' in sbotresp:
                        usermessage = sbotresp
                else:
                    pass

            SA = guard.SteamAuthenticator(secrets).get_code()
            result = client.login(username=username, password=password, two_factor_code=SA)
            if result != EResult.OK:
                LOG.info("Failed to login: %s" % repr(result))
                raise SystemExit

            client.run_forever()


t1 = threading.Thread(target=discordside)
t2 = threading.Thread(target=steamside)

t1.start()
t2.start()
