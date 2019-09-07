import discord
from discord.ext import commands
from platform import python_version
import steam
import json
import steam
import os

with open('Login details/preferences.json', 'r') as f:
    preferences = f.read()
    preferences = json.loads(preferences)
    owner_id = int(preferences["Discord ID"])
    bot64id = int(preferences["Bot's Steam ID"])
    owner_name = preferences["Owner Name"]
    command_prefix = preferences["Command Prefix"]
    color = int(preferences["Embed Colour"], 16)
    templocation = preferences["Path to Temp"]

bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), case_insensitive=True)
version = 'V.1.2'
acceptedfiles = ['history', 'history.json', 'inventory', 'inventory.json', 'schema', 'schema.json', 'listings',
                 'listings.json']


def is_owner(ctx):
    return ctx.message.author.id == owner_id


class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_owner)
    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        author = ctx.message.author
        embed = discord.Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name="Message from " + str(author))
        try:
            await bot.get_user(340869611903909888).send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I could not deliver your message. Perhaps it is too long?")
        except:
            await ctx.send("Alas, for reasons yet unknown to me, I could not deliver your message.")
        else:
            await ctx.send("I have delivered your message to Gobot1234#2435 (I may be in contact)"
                           ", this command is limited to working every 2 hours so you can't spam me")

    @commands.command()
    @commands.check(is_owner)
    async def ping(self, ctx):
        await ctx.send('Pong! {0} is online. Latency is {1} ms'.format(bot.user.name, round(bot.latency, 2)))

    @commands.command()
    @commands.check(is_owner)
    async def github(self, ctx):
        url = 'https://github.com/Gobot1234/tf2-autocord/pulse'
        embed = discord.Embed(title='GitHub Repo Infomation', color=0x2e3bad)
        embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
        embed.add_field(name='Current Version', value=version, inline=True)
        embed.add_field(name='GitHub Stats', value=url)
        embed.add_field(name='Link to the repo', value='https://github.com/Gobot1234/tf2-autocord')
        embed.add_field(name='What to check for an update', value=command_prefix + 'updaterepo')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_owner)
    async def updaterepo(self, ctx):
        await ctx.send('Attempting to update to the latest version of the code')
        os.system('cd ' + os.getcwd())
        updateable = os.popen('git pull').read()
        if 'Already up to date.' in updateable:
            await ctx.send('You are using the latest version of the code')
        else:
            await ctx.send('Updating the repo, you need to restart your program for the new update to take effect')

    @commands.command()
    @commands.check(is_owner)
    async def help(self, ctx, page=''):
        page = page.lower()
        if command_prefix in page:
            page.replace(command_prefix, '')
        if page == '' or page == 'help':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name='Help, you can get help with any of these commands individually by typing:'
                                  '\n' + command_prefix + 'help [command]')
            embed.add_field(name=command_prefix + 'help', value='Brings up this message', inline=True)
            embed.add_field(name=command_prefix + 'info',
                            value='Gives important information about the bot', inline=True)
            embed.add_field(name=command_prefix + 'help steam', value='Lists all of the Steam based commands', inline=True)
            embed.add_field(name=command_prefix + 'help discord', value='Lists all of the Discord based commands',
                            inline=True)
            embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
        elif page == 'steam':
            embed = discord.Embed(title=" ", color=0x00adee)
            embed.set_author(name='Steam Bound commands are as follows:')
            embed.add_field(name=command_prefix + 'scc', value='Creates a Steam chat command to send to the bot',
                            inline=False)
            embed.add_field(name=command_prefix + 'togprofit [time]',
                            value='Toggles on or off the  message sent at the end of every day giving the days profit',
                            inline=True)
            embed.add_field(name=command_prefix + 'add/update/remove/profit',
                            value='Send commands to your bot they allow chaining of commands', inline=False)
            embed.add_field(name=command_prefix + 'send [message to send]',
                            value='Allows you to send anything to your Steam bot', inline=False)
        elif page == 'discord':
            embed = discord.Embed(title=" ", color=0x7289da)
            embed.set_author(name='Discord Bound commands are as follows:')
            embed.add_field(name=command_prefix + 'togpremium',
                            value='Toggles on or off the time for alerts for when bp.tf premium is going to run out',
                            inline=True)
            embed.add_field(name=command_prefix + 'get [filename in temp]',
                            value='Gets files from your bot\'s temp folder', inline=False)
            embed.add_field(name=command_prefix + 'acknowledged',
                            value='Acknowledge a user\'s message', inline=False)
            embed.add_field(name=command_prefix + 'github',
                            value='Links you to the GitHub repo', inline=False)
            embed.add_field(name=command_prefix + 'ping',
                            value='Gives your bot\'s ping', inline=False)
            embed.add_field(name=command_prefix + 'get [filename in temp]',
                            value='Gets files from your bot\'s temp folder', inline=False)
            embed.add_field(name=command_prefix + 'suggest',
                            value='Suggest a feature to be implemented', inline=False)
            embed.add_field(name=command_prefix + 'donate',
                            value='Want to feel warm inside? Donations are appreciated', inline=False)
            embed.add_field(name=command_prefix + 'backpack',
                            value='Links you to your bp.tf profile and your bot\'s backpack', inline=False)
        # single commands
        elif page == 'scc':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'scc')
            embed.add_field(name='Usage of scc',
                            value='Scc should be relatively straight forward to use, go through the process like you would normally.',
                            inline=True)
        elif page == 'togprofit':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'togprofit [time]')
            embed.add_field(name='Usage of togprofit',
                            value='Togprofit can have the time that '
                                  + command_prefix + 'profit will be sent to your bot, passed into it in the form of HH:MM.',
                            inline=True)
        elif page == 'add' or page == 'update' or page == 'remove' or page == 'profit':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'add/update/remove/profit')
            embed.add_field(name='Usage of add/update/remove/profit',
                            value='These commands have the exact same functionality as the normally expect,'
                                  ' except you can chain commands by using names/items= and separate items '
                                  'by a comma and space.',
                            inline=True)
        elif page == 'send':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'send [messaage]')
            embed.add_field(name='Usage of send',
                            value='These commands have the exact same functionality as the normally expect,'
                                  ' except you can chain commands by using names/items= and separate items '
                                  'by a comma and space.',
                            inline=True)
        elif page == 'togpremium':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'togpremium')
            embed.add_field(name='Usage of togpremium',
                            value='Togpremium is used to set an alarm for 2 months - 1 day,'
                                  ' mainly to be remind you your bp.tf premium subscription is about to run out.',
                            inline=True)
        elif page == 'get':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'get [file]')
            embed.add_field(name='Usage of get',
                            value='Get is used to retrive files from your bot\'s temp folder, you can request'
                                  ' (' + str(acceptedfiles) + ').', inline=True)
        elif page == 'suggest':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'suggest')
            embed.add_field(name='Usage of suggest',
                            value='Suggest is used to suggest a feature to the developer of the code, '
                                  'it has a two hour message cooldown.', inline=True)
        elif page == 'donate':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'donate')
            embed.add_field(name='Usage of donate',
                            value='Donate is used to donate to support the development of the code, '
                                  'all donations are greatly appreciated', inline=True)
        elif page == 'backpack':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'backpack')
            embed.add_field(name='Usage of backpack',
                            value='Backpack is used to get your backpack and your bot\'s.', inline=True)
        elif page == 'updaterepo':
            embed = discord.Embed(title=" ", color=color)
            embed.set_author(name=command_prefix + 'updaterepo')
            embed.add_field(name='Usage of updaterepo',
                            value='Used to update the repo (only works if you cloned using git).', inline=True)
        else:
            await ctx.send('**Error 404:** Page not found ¯\_(ツ)_/¯')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_owner)
    async def info(self, ctx):
        embed = discord.Embed(title='Version is ' + version, color=color)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.png?size=1024')
        embed.set_author(name="Info about this bot")
        embed.add_field(name='Command prefix', value='Your command prefix is (' + command_prefix + '). Type '
                                                     + command_prefix + 'help to list the commands you can use',
                        inline=False)
        embed.add_field(name='About the bot',
                        value='It was coded in python to help you manage your tf2automtic bot. DM me with any '
                              'suggestions or features you would like on this bot', inline=False)
        embed.add_field(name='Discord.py Version',
                        value=discord.__version__ + ' works with versions 1.1+ of Discord.py',
                        inline=True)
        embed.add_field(name='Python Version',
                        value=python_version() + ' works with versions 3+',
                        inline=True)
        embed.add_field(name='Steam Version',
                        value=steam.__version__ + ' works with versions 3.4+ of python',
                        inline=True)
        embed.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(HelperCog(bot))
