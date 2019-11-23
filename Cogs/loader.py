import json
from asyncio import sleep
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from os import remove, execv
from platform import python_version
from sys import argv, executable, stderr
from textwrap import indent
from traceback import print_exc, format_exc

from discord import Activity, ActivityType, Colour, Embed
from discord.ext import commands


class LoaderCog(commands.Cog, name='Loader'):
    """This cog just stores all of your variables nothing particularly interesting and a few commands for development"""
    __version__ = '1.2.5'  # hey that's the same as d.py spooky

    def __init__(self, bot):
        """Setting all of your bot vars to be used by other cogs/commands"""
        self.bot = bot
        self._last_result = None
        self.sessions = set()

        login = json.loads(open("Login details/sensitive details.json", "r").read())
        bot.username = login["Username"]
        bot.password = login["Password"]
        try:
            bot.secrets = {
                "identity_secret": login["Identity Secret"],
                "shared_secret": login["Shared Secret"]
            }
        except:
            pass

        preferences = json.loads(open('Login details/preferences.json', 'r').read())
        bot.owner_id = int(preferences["Discord ID"])
        bot.bot64id = int(preferences["Bot's Steam ID"])
        bot.prefix = preferences["Command Prefix"]
        bot.color = int(preferences["Embed Colour"], 16)
        bot.templocation = preferences["Path to Temp"]

        bot.sbotresp = 0
        bot.usermessage = 0
        bot.logged_on = 0
        bot.togglepremium = 0
        bot.dsdone = 0
        bot.trades = 0

        bot.updatem = f'{bot.prefix}update name='
        bot.removem = f'{bot.prefix}remove item='
        bot.addm = f'{bot.prefix}add name='
        bot.currenttime = datetime.now().strftime("%H:%M")

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.Cog.listener()
    async def on_ready(self):
        """Setting your status, printing your bot's id to send to me,
        seeing if the bot was restarted and stored your number of trades,
        finally checking if you are logged onto steam"""
        self.bot.owner = self.bot.get_user(self.bot.owner_id)

        await self.bot.change_presence(activity=Activity(
            name=f'{self.bot.owner.name}\'s trades | V{LoaderCog.__version__} | Command Prefix \"{self.bot.prefix}\"',
            type=ActivityType.watching))
        print('-' * 30)
        print(f'\033[92m{self.bot.user.name} is ready\033[92m')
        print(
            f'Send this id: \033[95m"{self.bot.user.id}"\033[95m\033[92m to Gobot1234 to add your bot to the server to use the custom emojis)')
        print('This is: \033[95m' + f'Version {LoaderCog.__version__}\033[95m')
        self.bot.dsdone = True
        try:
            self.bot.trades = int(open('trades.txt', 'r').read())
        except:
            pass
        await sleep(15)
        try:
            remove('trades.txt')
        except:
            pass
        while self.bot.logged_on is False:
            if self.bot.cli_login:
                await self.bot.owner.send('You aren\'t currently logged into your Steam account\nTo do that type in '
                                          'your 2FA code into the console.')
            await sleep(60)
        await self.bot.owner.send('I\'m online both Steam and Discord dealing with your Steam messages')
        print('-' * 30)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, extension):
        """You probably don't need to use this, however it can be used to reload a cog

        eg. `!reload loader`"""
        if 'Cogs.' not in extension:
            extension = f'Cogs.{extension.lower()}'
        if '.py' in extension:
            extension = extension[:-3]
        if extension == 'Cogs.all':
            async with ctx.typing():
                reloaded = ''
                for extension in self.bot.initial_extensions:
                    try:
                        self.bot.reload_extension(f'Cogs.{extension}')
                    except Exception as e:
                        reloaded += f'<:goodcross:626829085682827266> `{extension}`\n'
                        await ctx.send(
                            f'**`ERROR:`** {ctx.author.name}, `{extension}` `{type(e).__name__}` - {e}')
                        print(f'Failed to load extension {extension}.', file=stderr)
                        print_exc()
                    else:
                        reloaded += f'<:tick:626829044134182923> `{extension}`\n'
                return await ctx.send(f'**`SUCCESS`** {ctx.author.name} finished reloading {len(self.bot.initial_extensions)} cogs \n{reloaded}')
        try:
            self.bot.reload_extension(extension)
        except commands.ExtensionNotLoaded as e:
            await ctx.send(
                f'**`ERROR:`** <:goodcross:626829085682827266> {ctx.author.name}, `{extension}` `{type(e).__name__}` - {e} hasn\'t been loaded\nI\'m going to load it now.')
            try:
                self.bot.load_extension(extension)
            except Exception as e:
                await ctx.send(f'**`ERROR:`** <:goodcross:626829085682827266> `{type(e).__name__}` - {e}')
                print(f'Failed to load extension {extension}.', file=stderr)
                print_exc()
        else:
            await ctx.send(f'**`SUCCESS`** <:tick:626829044134182923> {ctx.author.name}, `{extension}` has been reloaded')

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Used to reset the bot

        This won't work use this if you use `cli_login`, try not to use this"""
        if self.bot.cli_login:
            await ctx.send('You really really shouldn\'t do this')
        else:
            open('trades.txt', 'w+').write(str(self.bot.trades))
            await ctx.send(f'**Restarting the bot** {ctx.author.mention}, don\'t use this often')
            execv(executable, ['python'] + argv)

    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """This will evaluate your code-block if type some python code.
        **PLEASE BE AWARE THIS IS A POTENTIALLY DANGEROUS COMMAND TO USE IF YOU DON'T KNOW WHAT YOU'RE DOING**

        Input is interpreted as newline separated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `channel`: the channel the eval command was used in
          - `author`: the author of the eval command!
          - `server`: the server that eval command was used in
          - `message`: the message that was used to invoke the command (`!eval...`)
          - `client`: the SteamClient instance
          - `bot`: the bot instance
          - `discord`: the discord module
          - `commands`: the discord.ext.commands module
          - `ctx`: the invokation context

        eg. `!eval` ```py
        await ctx.send(f'Hello my name is {bot.user.name} :wave:. Type !help to see what I can do')```
        """
        async with ctx.typing():
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                'client': self.bot.client,
                'commands': commands,
            }

            env.update(globals())

            body = self.cleanup_code(body)
            stdout = StringIO()

            to_compile = f'async def func():\n{indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                await ctx.message.add_reaction('\U0000274c')
                embed = Embed(title=f':x: {e.__class__.__name__}',
                              description=f'```py\n{format_exc()}{e}```',
                              color=Colour.red())
                return await ctx.send(embed=embed)
            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                await ctx.message.add_reaction('\U0000274c')
                value = stdout.getvalue()
                await ctx.message.add_reaction('\U0000274c')
                embed = Embed(title=f':x: {e.__class__.__name__}',
                              description=f'```py\n{value}{format_exc()}{e}```',
                              color=self.bot.color)
                return await ctx.send(embed=embed)
            else:
                value = stdout.getvalue()
                await ctx.message.add_reaction('\U00002705')
                embed = Embed(title=f'Evaluation completed {ctx.author.display_name} :white_check_mark:',
                              color=Colour.purple())
                if ret is None:
                    if value:
                        embed.add_field(name='Eval returned', value=f'```py\n{value}```')
                else:
                    self._last_result = ret
                    embed.add_field(name='Eval returned', value=f'```py\n{value}{ret}```')
                embed.set_footer(text=f'Python {python_version()}',
                                 icon_url='https://www.python.org/static/apple-touch-icon-144x144-precomposed.png')
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LoaderCog(bot))
