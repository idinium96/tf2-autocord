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

# read details ---------------------------------------------------------------------------------------------------------

with open("Login details/sensitive details.txt", "r") as f:  # reads your details
    login = f.read()
    login = login.replace("Token:\n", "")
    login = login.replace(" # put your bot's token here\nUsername:\n", "")
    login = login.replace(" # put your steam username here\nPassword:\n", "")
    login = login.replace(" # put your steam password here", "")
    login = login.split(' ')
    token = login[0]
    global username
    global password
    username = login[1]
    password = login[2]

with open('Login details/preferences.txt', 'r') as f:
    preferences = f.read()
    preferences = preferences.replace("Discord ID:\n", "")
    preferences = preferences.replace(" # put your discord id here\nBot'a steam 64 ID:\n", "")
    preferences = preferences.replace(" # put your bot's steam id here\nOwner name:\n", "")
    preferences = preferences.replace(" # add your name\nDiscord command prefix:\n", "")
    preferences = preferences.replace(" # change your command prefix\nSteam bot command prefix:\n", "")
    preferences = preferences.replace(" # don't change this unless you are hackerino\nEmbed color:\n", "")
    preferences = preferences.replace(" # hex code here (no #)\nPath to temp:\n", "")
    preferences = preferences.split(" ")
    owner_id = int(preferences[0])
    global bot64id
    bot64id = preferences[1]
    owner_name = preferences[2]
    command_prefix = preferences[3]
    global sbotcommand_prefix
    sbotcommand_prefix = preferences[4]
    color = int(preferences[5], 16)

# main program ---------------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix=command_prefix)
bot.remove_command('help')

updatem = sbotcommand_prefix + 'update name='
removem = sbotcommand_prefix + 'remove item='
addm = sbotcommand_prefix + 'add name='

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


global storeresp
global sbotresp
global sendmessage
global message
global botresp
sbotresp = 0
storeresp = 0


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
    print('Logged in as', bot.user.name)
    await bot.get_user(owner_id).send('I\'m Online and dealing with your trade notifications :)')


@tasks.loop(seconds=10, count=None)
async def bgcheck():
    global sbotresp
    if sbotresp != 0:
        await bot.get_user(owner_id).send(sbotresp)
        sbotresp = 0
    else:
        pass

# help -----------------------------------------------------------------------------------------------------------------


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=" ", color=color)
    embed.set_author(name='Help')
    embed.add_field(name=command_prefix + 'help', value='Brings up this message', inline=True)
    embed.add_field(name=command_prefix + 'info',
                    value='Gives important information about the bot', inline=True)
    embed.add_field(name=command_prefix + 'add/update/remove/profit',
                    value='Send commands to your bot', inline=False)
    embed.add_field(name=command_prefix + 'send [message to send]',
                    value='Allows you to send anything to your Steam bot', inline=False)
    embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
    await ctx.send(embed=embed)


@bot.command()
async def info(ctx):
    embed = discord.Embed(title=" ", color=color)
    embed.set_author(name="Info about this bot - Free")
    embed.add_field(name='Command prefix', value='Your command prefix is (' + command_prefix + '). Type '
                                                 + command_prefix + 'help to list the commands you can use',
                    inline=False)
    embed.add_field(name='About the bot',
                    value='It was coded in python to help you manage your tf2automatic bot. DM me with any '
                          'suggestions or features you would like on this bot, The premium version of this code is 2 keys, again feel free to DM me for me info', inline=False)
    embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
    await ctx.send(embed=embed)

# normal ---------------------------------------------------------------------------------------------------------------


@bot.command()
async def add(ctx, *, content: str):
    client.get_user(bot64id).send_message(addm + content)
    await ctx.send('Sent ' + addm + ' ' + content + 'to the bot')


@bot.command()
async def update(ctx, *, content: str):
    client.get_user(bot64id).send_message(updatem + content)
    await ctx.send('Sent ' + updatem + ' ' + content + 'to the bot')


@bot.command()
async def remove(ctx, *, content: str):
    client.get_user(bot64id).send_message(removem + content)
    await ctx.send('Sent ' + removem + ' ' + content + 'to the bot')


@bot.command()
async def profit(ctx):
    global botresp
    botresp = False
    while botresp is False:
        async with ctx.typing():
            global storeresp
            storeresp = 1
            client.get_user(bot64id).send_message(sbotcommand_prefix + 'profit')
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
