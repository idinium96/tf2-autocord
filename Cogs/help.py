from asyncio import TimeoutError
from datetime import datetime
from os import popen, system, getcwd

from discord import Embed, Colour, errors
from discord.ext import commands, tasks

from .loader import LoaderCog


class HelpCommand(commands.HelpCommand):
    """Custom help command my ass"""

    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Shows help about the bot, a command, or a cog\n\neg. `!help Steam` (There should be 4 cogs and 27 commands)'
        })

    def get_command_signature(self, command):
        if len(command.signature) == 0:
            return f'`{self.clean_prefix}{command.name}`'
        else:
            return f'`{self.clean_prefix}{command.name}` `{command.signature}`'

    def get_command_aliases(self, command):
        if len(command.aliases) == 0:
            return ''
        else:
            return f'command aliases are [`{"`, `".join([alias for alias in command.aliases])}`]'

    def get_command_description(self, command):
        if len(command.short_doc) == 0:
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc

    def get_full_command_description(self, command):
        if len(command.help) == 0:
            return 'There is no documentation for this command currently'
        else:
            return command.help

    async def bot_help_paginator(self, page: int):
        ctx = self.context
        bot = ctx.bot

        all_commands = [command.name for command in await self.filter_commands(bot.commands)]
        current_cog = bot.get_cog(self.all_cogs[page])
        cog_n = current_cog.qualified_name

        if cog_n == 'Help':
            color = bot.color
            emoji = '<:tf2autocord:624658299224326148>'
        elif cog_n == 'Discord':
            color = 0x7289da
            emoji = '<:discord:626486432793493540>'
        elif cog_n == 'Steam':
            color = 0x00adee
            emoji = '<:steam:622621553800249364>'
        else:
            emoji = '<:tf2autocord:624658299224326148>'
            color = bot.color

        embed = Embed(title=f'Help with {current_cog.qualified_name} ({len(all_commands)} commands) {emoji}',
                      description=current_cog.description, color=color)
        embed.set_author(name=f'We are currently on page {page + 1}/{len(self.all_cogs)}',
                         icon_url=ctx.author.avatar_url)
        try:
            for c in current_cog.walk_commands():
                if await c.can_run(ctx) and c.hidden is False:
                    signature = self.get_command_signature(c)
                    description = self.get_command_description(c)
                    if c.parent:
                        embed.add_field(name=f'╚╡`{signature[2:]}', value=description, inline=False)
                    else:
                        embed.add_field(name=signature, value=description, inline=False)
        except:
            pass
        return embed

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        page = 0
        self.all_cogs = [cog for cog in bot.cogs]

        def check(reaction, user):
            return user == ctx.author

        embed = await self.bot_help_paginator(page)
        help_embed = await ctx.send(embed=embed)
        await help_embed.add_reaction('\U000025c0')
        await help_embed.add_reaction('\U000023f9')
        await help_embed.add_reaction('\U000025b6')
        await help_embed.add_reaction('\U00002139')

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=30, check=check)
            except TimeoutError:
                try:
                    await help_embed.clear_reactions()
                except errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)
                except errors.Forbidden:
                    pass
                if str(reaction.emoji) == '◀':
                    page -= 1
                    if page == -1:
                        page = len(self.all_cogs) - 1
                    embed = await self.bot_help_paginator(page)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '▶':
                    page += 1
                    if page == len(self.all_cogs):
                        page = 0
                    embed = await self.bot_help_paginator(page)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':
                    all_cogs = '`, `'.join([cog for cog in self.all_cogs])
                    embed = Embed(title=f'Help with {bot.user.name}\'s commands', description=bot.description,
                                  color=bot.color)
                    embed.add_field(
                        name=f'Currently you have {len([cog for cog in self.all_cogs])} cogs loaded, which are (`{all_cogs}`) :gear:',
                        value='`<...>` indicates a required argument,\n`[...]` indicates an optional argument.\n\n'
                              '**Don\'t however type these around your argument**')
                    embed.add_field(name='What do the emojis do:',
                                    value=':arrow_backward: goes to the previous page\n'
                                          ':arrow_forward: goes to the next page\n'
                                          ':stop_button: stops the interactive pagination session\n'
                                          ':information_source: shows this message')
                    embed.set_author(name=f'You were on page {page + 1}/{len(self.all_cogs)} before',
                                     icon_url=ctx.author.avatar_url)

                    embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '⏹':
                    await help_embed.delete()
                    break

    async def send_cog_help(self, cog):
        ctx = self.context
        bot = ctx.bot

        cog_commands = [command for command in await self.filter_commands(cog.walk_commands())]
        cog_n = cog.qualified_name

        if cog_n == 'Help':
            color = bot.color
            emoji = '<:tf2autocord:624658299224326148>'
        elif cog_n == 'Discord':
            color = 0x7289da
            emoji = '<:discord:626486432793493540>'
        elif cog_n == 'Steam':
            color = 0x00adee
            emoji = '<:steam:622621553800249364>'
        else:
            emoji = '<:tf2autocord:624658299224326148>'
            color = bot.color
        embed = Embed(title=f'Help with {cog_n} ({len(cog_commands)} commands) {emoji}',
                      description=cog.description, color=color)
        embed.set_author(name=f'We are currently looking at the module {cog.qualified_name} and its commands',
                         icon_url=ctx.author.avatar_url)
        _commands = [c for c in cog_commands if await c.can_run(ctx) and c.hidden is False]
        for c in _commands:
            signature = self.get_command_signature(c)
            aliases = self.get_command_aliases(c)
            description = self.get_command_description(c)
            if c.parent:
                embed.add_field(name=f'╚╡`{signature[2:]}', value=description, inline=False)
            else:
                embed.add_field(name=f'{signature} {aliases}',
                                value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        bot = ctx.bot
        cog_n = command.cog.qualified_name
        if cog_n == 'Help':
            color = bot.color
            emoji = '<:tf2autocord:624658299224326148>'
        elif cog_n == 'Discord':
            color = 0x7289da
            emoji = '<:discord:626486432793493540>'
        elif cog_n == 'Steam':
            color = 0x00adee
            emoji = '<:steam:622621553800249364>'
        else:
            emoji = '<:tf2autocord:624658299224326148>'
            color = bot.color

        if await command.can_run(ctx):
            embed = Embed(title=f'Help with `{command.name}` {emoji}', color=color)
            embed.set_author(name=f'We are currently looking at the {cog_n} cog and its command {command.name}',
                             icon_url=ctx.author.avatar_url)
            signature = self.get_command_signature(command)
            description = self.get_full_command_description(command)
            aliases = self.get_command_aliases(command)

            if command.parent:
                embed.add_field(name=f'╚╡`{signature[2:]}', value=description, inline=False)
            else:
                embed.add_field(name=f'{signature} {aliases}', value=description, inline=False)
            embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
            await ctx.send(embed=embed)

    async def send_group_help(self, group):
        ctx = self.context
        bot = ctx.bot

        embed = Embed(title=f'Help with `{group.name}`', color=bot.color)
        embed.set_author(
            name=f'We are currently looking at the {group.cog.qualified_name} cog and its command {group.name}',
            icon_url=ctx.author.avatar_url)
        for command in group.walk_commands():
            if await command.can_run(ctx):
                signature = self.get_command_signature(command)
                description = self.get_command_description(command)
                aliases = self.get_command_aliases(command)

                if command.parent:
                    embed.add_field(name=f'╚╡`{signature[2:]}', value=description, inline=False)
                else:
                    embed.add_field(name=f'{signature} {aliases}', value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
        await ctx.send(embed=embed)

    async def send_error_message(self, error):
        pass

    async def command_not_found(self, string):
        embed = Embed(title='Error!', description=f'**Error 404:** Command or cog "{string}" not found ¯\_(ツ)_/¯',
                      color=Colour.red())
        await self.context.send(embed=embed)


class HelperCog(commands.Cog, name='Help'):
    """Help yourself to do stuff with the bot's commands"""

    def __init__(self, bot):
        self.bot = bot
        self.githubupdate.start()
        self.bot.launch_time = datetime.utcnow()
        self._original_help_command = bot.help_command
        commands.HelpCommand.verify_checks = False
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    @tasks.loop(hours=24)
    async def githubupdate(self):
        """A tasks loop to check if there has been an update to the GitHub repo"""
        system(f'cd {getcwd()}')
        updateable = popen('git checkout').read()
        await self.bot.owner.send(updateable)
        print(f'updateable = "{updateable}"')
        if 'Your branch is up to date with' in updateable:
            pass
        elif 'fatal: not a git repository (or any of the parent directories): .git' in updateable:
            await self.bot.owner.send('This wasn\'t cloned from GitHub')
        else:
            await self.bot.owner.send(f'There is an update to the repo. Do you want to install it? (Type '
                                      f'{self.bot.prefix}updaterepo to install it)')

    @commands.command()
    @commands.is_owner()
    async def updaterepo(self, ctx):
        """Used to update to the newest version of the code

        This will overwrite any changes you have made locally"""
        await ctx.send('Attempting to update to the latest version of the code')
        system(f'cd {getcwd()}')
        system('git reset --hard HEAD')
        updateable = popen('git pull').read()
        if 'Already up to date.' in updateable:
            await ctx.send('No updates to be had?')
        elif updateable == 'fatal: not a git repository (or any of the parent directories): .git':
            await ctx.send('This wasn\'t cloned from GitHub')
        else:
            await ctx.trigger_typing()
            await ctx.send('Updating from the latest GitHub push\nYou will need to restart for the update to take effect')

    @commands.command()
    async def github(self, ctx):
        """Shows the GitHub repo and some info about it"""
        system(f'cd {getcwd()}')
        updateable = popen('git checkout').read()
        if 'Your branch is up to date with' in updateable:
            emoji = '<:tick:626829044134182923>'
        elif updateable == 'fatal: not a git repository (or any of the parent directories): .git':
            emoji = 'This wasn\'t cloned from GitHub'
        else:
            emoji = '<:goodcross:626829085682827266>'
        embed = Embed(title='GitHub Repo Infomation', color=0x2e3bad)
        embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
        embed.add_field(name='Current Version', value=f'Version: {LoaderCog.__version__}. Up to date: {emoji}',
                        inline=True)
        embed.add_field(name='GitHub Stats', value='https://github.com/Gobot1234/tf2-autocord/pulse')
        embed.add_field(name='Link to the repo', value='[Repository](https://github.com/Gobot1234/tf2-autocord)')
        embed.add_field(name='Want to check for an update?', value=f'{self.bot.prefix}updaterepo')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        """Suggest a feature to <@340869611903909888>

         eg. `!suggest update the repo`"""
        embed = Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name=f'Message from {ctx.author}')
        try:
            await self.bot.get_user(340869611903909888).send(embed=embed)
        except:
            await ctx.send('I could not deliver your message. ¯\_(ツ)_/¯, probably as your bot '
                           'isn\'t in the server send {self.bot.user.id} to <@340869611903909888>')
        else:
            await ctx.send('I have delivered your message to <@340869611903909888> (I may be in contact), '
                           'this command is limited to working every 2 hours so you can\'t spam me')

    @commands.command()
    async def ping(self, ctx):
        """Check if your bot is online on both Steam and Discord"""
        if self.bot.client.logged_on:
            message = f'You are logged in as {self.bot.client.user.name}'
        else:
            message = 'You aren\'t logged into steam'
        await ctx.send(f'Pong! {self.bot.user.name} is online. Latency is {round(self.bot.latency, 2)} ms. {message}')

    @commands.command()
    async def uptime(self, ctx):
        """See how long the bot has been online for"""
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f'{self.bot.user.mention} has been online for `{days}d, {hours}h, {minutes}m, {seconds}s`')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        :ctx: Context
        :error: Exception"""
        if isinstance(error, commands.MissingRequiredArgument):
            title = 'Missing a required argument'
        elif isinstance(error, commands.CommandOnCooldown):
            title = 'Command is on cooldown'
        elif isinstance(error, commands.BadArgument):
            title = 'Bad argument'
        elif isinstance(error, commands.MissingRequiredArgument):
            title = 'Missing argument'
        elif isinstance(error, commands.NotOwner):
            title = 'You aren\'t the owner of the bot'
        elif isinstance(error, commands.MissingPermissions):
            title = 'You don\'t have the necessary permissions'
        elif isinstance(error, commands.CommandNotFound):
            title = 'Command not found'
        elif isinstance(error, commands.CommandInvokeError):
            title = 'Invoke error I probably messed up'
            embed = Embed(title=f':warning: **{title}**', description=str(error.original),
                          color=Colour.red())
            embed.add_field(name='\u200b',
                            value='Please try again, and maybe send <@340869611903909888> '
                                  'the error outputted in the shell')
            await ctx.send(embed=embed)
            raise error.original
        else:
            title = 'Unspecified error'
            error = 'Please try again, and maybe send <@340869611903909888> the error outputted in the shell'
        embed = Embed(title=f':warning: **{title}**', description=str(error), color=Colour.red())
        await ctx.send(embed=embed)
        raise error


def setup(bot):
    bot.add_cog(HelperCog(bot))
