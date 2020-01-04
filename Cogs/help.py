from asyncio import TimeoutError, sleep
from datetime import datetime
from os import getcwd
from subprocess import getoutput
from time import perf_counter

from discord import Embed, Colour, errors
from discord.ext import commands, tasks

from .loader import __version__


class HelpCommand(commands.HelpCommand):
    """The custom help command class for the bot"""

    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Shows help about the bot, a command, or a cog\neg. `{prefix}help Steam` (There should be 4 cogs '
                    'and 25 commands)'
        })

    def get_command_signature(self, command):
        """Method to return a commands name and signature"""
        if not command.signature and not command.parent:  # checking if it has no args and isn't a subcommand
            return f'`{self.clean_prefix}{command.name}`'
        if command.signature and not command.parent:  # checking if it has args and isn't a subcommand
            return f'`{self.clean_prefix}{command.name}` `{command.signature}`'
        if not command.signature and command.parent:  # checking if it has no args and is a subcommand
            return f'**╚╡**`{command.name}`'
        else:  # else assume it has args a signature and is a subcommand
            return f'**╚╡**`{command.name}` `{command.signature}`'

    def get_command_aliases(self, command):  # this is a custom written method along with all the others below this
        """Method to return a commands aliases"""
        if not command.aliases:  # check if it has any aliases
            return ''
        else:
            return f'command aliases are [`{"` | `".join([alias for alias in command.aliases])}`]'

    def get_command_description(self, command):
        """Method to return a commands short doc/brief"""
        if not command.short_doc:  # check if it has any brief
            return 'There is no documentation for this command currently'
        else:
            return command.short_doc.format(prefix=self.clean_prefix)

    def get_command_help(self, command):
        """Method to return a commands full description/doc string"""
        if not command.help:  # check if it has any brief or doc string
            return 'There is no documentation for this command currently'
        else:
            return command.help.format(prefix=self.clean_prefix)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        page = 0
        cogs = [cog for cog in bot.cogs]
        cogs.sort()

        def check(reaction, user):  # check who is reacting to the message
            return user == ctx.author and help_embed.id == reaction.message.id

        embed = await self.bot_help_paginator(page, cogs)
        help_embed = await ctx.send(embed=embed)  # sends the first help page

        reactions = ('\N{BLACK LEFT-POINTING TRIANGLE}',
                     '\N{BLACK RIGHT-POINTING TRIANGLE}',
                     '\N{BLACK SQUARE FOR STOP}',
                     '\N{INFORMATION SOURCE}')  # add reactions to the message
        bot.loop.create_task(self.bot_help_paginator_reactor(help_embed, reactions))
        # this allows the bot to carry on setting up the help command

        while 1:
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)  # checks message reactions
            except TimeoutError:  # session has timed out
                try:
                    await help_embed.clear_reactions()
                except errors.Forbidden:
                    pass
                break
            else:
                try:
                    await help_embed.remove_reaction(str(reaction.emoji), ctx.author)  # remove the reaction
                except errors.Forbidden:
                    pass

                if str(reaction.emoji) == '◀':  # go to the previous page
                    page -= 1
                    if page == -1:  # check whether to go to the final page
                        page = len(cogs) - 1
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)
                elif str(reaction.emoji) == '▶':  # go to the next page
                    page += 1
                    if page == len(cogs):  # check whether to go to the first page
                        page = 0
                    embed = await self.bot_help_paginator(page, cogs)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == 'ℹ':  # show information help
                    all_cogs = '`, `'.join([cog for cog in cogs])
                    embed = Embed(title=f'Help with {bot.user.name}\'s commands', description=bot.description,
                                  color=bot.color)
                    embed.add_field(
                        name=f'Currently you have {len(bot.cogs)} cogs loaded, which are (`{all_cogs}`) :gear:',
                        value='`<...>` indicates a required argument,\n`[...]` indicates an optional argument.\n\n'
                              '**Don\'t however type these around your argument**')
                    embed.add_field(name='What do the emojis do:',
                                    value=':arrow_backward: Goes to the previous page\n'
                                          ':arrow_forward: Goes to the next page\n'
                                          ':stop_button: Deletes and closes this message\n'
                                          ':information_source: Shows this message')
                    embed.set_author(name=f'You were on page {page + 1}/{len(bot.cogs)} before',
                                     icon_url=ctx.author.avatar_url)
                    embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                                     icon_url=ctx.bot.user.avatar_url)
                    await help_embed.edit(embed=embed)

                elif str(reaction.emoji) == '⏹':  # delete the message and break from the wait_for
                    await help_embed.delete()
                    break

    async def bot_help_paginator_reactor(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def bot_help_paginator(self, page: int, cogs: list):
        ctx = self.context
        bot = ctx.bot
        all_commands = [command for command in
                        await self.filter_commands(bot.commands)]  # filter the commands the user can use
        cog = bot.get_cog(cogs[page])  # get the current cog
        color, emoji = bot.cog_color[cog.qualified_name]

        embed = Embed(title=f'Help with {cog.qualified_name} ({len(all_commands)} commands) {emoji}',
                      description=cog.description, color=color)
        embed.set_author(name=f'We are currently on page {page + 1}/{len(cogs)}', icon_url=ctx.author.avatar_url)
        for c in cog.walk_commands():
            if await c.can_run(ctx) and not c.hidden:
                signature = self.get_command_signature(c)
                description = self.get_command_description(c)
                if c.parent:  # it is a sub-command
                    embed.add_field(name=signature, value=description)
                else:
                    embed.add_field(name=signature, value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        return embed

    async def send_cog_help(self, cog):
        ctx = self.context
        cog_commands = [command for command in await self.filter_commands(cog.walk_commands())]  # get commands
        color, emoji = ctx.bot.cog_color[cog.qualified_name]
        embed = Embed(title=f'Help with {cog.qualified_name} ({len(cog_commands)} commands) {emoji}',
                      description=cog.description, color=color)
        embed.set_author(name=f'We are currently looking at the module {cog.qualified_name} and its commands',
                         icon_url=ctx.author.avatar_url)
        for c in cog_commands:
            signature = self.get_command_signature(c)
            aliases = self.get_command_aliases(c)
            description = self.get_command_description(c)
            if c.parent:
                embed.add_field(name=signature, value=description)
            else:
                embed.add_field(name=f'{signature} {aliases}',
                                value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.',
                         icon_url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        color, emoji = ctx.bot.cog_color[command.cog.qualified_name]

        if await command.can_run(ctx):
            embed = Embed(title=f'Help with `{command.name}` {emoji}', color=color)
            embed.set_author(
                name=f'We are currently looking at the {command.cog.qualified_name} cog and its command {command.name}',
                icon_url=ctx.author.avatar_url)
            signature = self.get_command_signature(command)
            description = self.get_command_help(command)
            aliases = self.get_command_aliases(command)

            if command.parent:
                embed.add_field(name=signature, value=description, inline=False)
            else:
                embed.add_field(name=f'{signature} {aliases}', value=description, inline=False)
            embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
            await ctx.send(embed=embed)

    async def send_group_help(self, group):
        ctx = self.context
        bot = ctx.bot

        embed = Embed(title=f'Help with `{group.name}`', description=bot.get_command(group.name).help,
                      color=bot.color)
        embed.set_author(
            name=f'We are currently looking at the {group.cog.qualified_name} cog and its command {group.name}',
            icon_url=ctx.author.avatar_url)
        for command in group.walk_commands():
            if await command.can_run(ctx):
                signature = self.get_command_signature(command)
                description = self.get_command_description(command)
                aliases = self.get_command_aliases(command)

                if command.parent:
                    embed.add_field(name=signature, value=description, inline=False)
                else:
                    embed.add_field(name=f'{signature} {aliases}', value=description, inline=False)
        embed.set_footer(text=f'Use "{self.clean_prefix}help <command>" for more info on a command.')
        await ctx.send(embed=embed)

    async def send_error_message(self, error):
        pass

    async def command_not_found(self, string):
        embed = Embed(title='Error!',
                      description=f'**Error 404:** Command or cog "{string}" not found ¯\_(ツ)_/¯',
                      color=Colour.red())
        embed.add_field(name='The current loaded cogs are',
                        value=f'(`{"`, `".join([cog for cog in self.context.bot.cogs])}`) :gear:')
        await self.context.send(embed=embed)


class Help(commands.Cog):
    """Help yourself to do stuff with the bot """

    def __init__(self, bot):
        self.bot = bot
        self.githubupdate.start()
        self.bot.launch_time = datetime.utcnow()
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.githubupdate.cancel()

    @tasks.loop(hours=24)
    async def githubupdate(self):
        """A tasks loop to check if there has been an update to the GitHub repo"""
        await self.bot.wait_until_ready()
        result = await self.bot.loop.run_in_executor(None, getoutput, f'git checkout {getcwd()}')
        owner = self.bot.owner
        if 'Your branch is up to date with' in result:
            return
        elif result == 'fatal: not a git repository (or any of the parent directories): .git':
            await owner.send(embed=Embed(
                title=':goodcross:626829085682827266 This version wasn\'t cloned from GitHub, which I advise as it '
                      'allows for automatic updates',
                description='Installing is as simple as typing `git clone '
                            'https://github.com/Gobot1234/tf2-autocord.git Discord` '
                            'into your command prompt of choice, although you need git to be installed',
                color=self.bot.color))
        else:
            def check(m):
                return m.content and m.channel == owner_dm.channel

            async with self.bot.session as cs:
                async with cs.get('https://api.github.com/repos/Gobot1234/tf2-autocord/commits') as r:
                    res = await r.json()
                    version = res[0]['commit']['message']

                async with cs.get(res[0]['comments_url']) as r:
                    res = await r.json()
                    comment = res[0] or 'I didn\'t provide any update info ¯\_(ツ)_/¯'

            owner_dm = await owner.send(
                embed=Embed(title=f'Version {version} has been pushed to the GitHub repo. Do you want to install it?',
                            description=f'__Update info is as follows:__\n```{comment}```', color=self.bot.color))

            choice = await self.bot.wait_for('message', check=check)
            choice = choice.content.lower()
            while 1:
                if choice == 'yes' or choice == 'y':
                    await owner.send(
                        'Updating from the latest GitHub push\nYou will need to restart for the update to take effect')
                    reset = await self.bot.loop.run_in_executor(None, getoutput, f'cd {getcwd()} & git reset --hard HEAD')
                    await owner.send(f'```bash\n{reset}```')
                    update = await self.bot.loop.run_in_executor(None, getoutput, f'git pull {getcwd()}')
                    await owner.send(f'```bash\n{update}```')
                    break

                elif choice == 'no' or choice == 'n':
                    await owner.send('I won\'t update the version yet')
                    break
                else:
                    await owner.send('Please try again with yes or no')

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.cog_color = {
            'Discord': (Colour.blurple(), '<:discord:626486432793493540>'),
            'Help': (self.bot.color, '<:tf2autocord:624658299224326148>'),
            'Loader': (self.bot.color, '<:tf2automatic:624658370447671297>'),
            'Steam': (0x00adee, '<:steam:622621553800249364>'),
            'Development': (self.bot.color, '<:tf2automatic:624658370447671297>')
        }

    @commands.command()
    @commands.is_owner()
    async def updaterepo(self, ctx):
        """Used to update to the newest version of the code

        This will overwrite any changes you have made locally to any cogs"""
        await ctx.send('Attempting to update to the latest version of the code')
        async with ctx.typing():
            result = await self.bot.loop.run_in_executor(None, getoutput, f'git checkout {getcwd()}')

            if 'Already up to date.' in result:
                await ctx.send('No updates to be had?')
            elif result == 'fatal: not a git repository (or any of the parent directories): .git':
                await self.bot.owner.send(embed=Embed(
                    title='<:goodcross:626829085682827266> This version wasn\'t cloned from GitHub, which I advise as '
                          'it allows for automatic updates',
                    description='Instealling is as simple as typing `git clone '
                                'https://github.com/Gobot1234/tf2-autocord.git Discord` '
                                'into your command prompt of choice, although you need git to be installed',
                    color=self.bot.color))
            else:
                await ctx.send(
                    'Updating from the latest GitHub push\nYou will need to restart for the update to take effect')
                reset = await self.bot.loop.run_in_executor(None, getoutput, f'cd {getcwd()} & git reset --hard HEAD')
                await ctx.send(f'```bash\n{reset}```')
                update = await self.bot.loop.run_in_executor(None, getoutput, f'git pull {getcwd()}')
                await ctx.send(f'```bash\n{update}```')

    @commands.command()
    async def github(self, ctx):
        """Shows the GitHub repo and some info about it"""
        result = await self.bot.loop.run_in_executor(None, getoutput, f'git checkout {getcwd()}')
        if 'Your branch is up to date with' in result:
            emoji = '<:tick:626829044134182923>'
        elif result == 'fatal: not a git repository (or any of the parent directories): .git':
            emoji = 'This wasn\'t cloned from GitHub'
        else:
            emoji = '<:goodcross:626829085682827266>'
        embed = Embed(title='GitHub Repo Infomation', color=0x2e3bad)
        embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
        embed.add_field(name='Current Version', value=f'Version: {__version__}. Up to date: {emoji}',
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

         eg. `{prefix}suggest update the repo` your bot needs to be in the tf2autcord server for this to work"""
        embed = Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name=f'Message from {ctx.author}')
        try:
            await self.bot.get_user(340869611903909888).send(embed=embed)
        except:
            await ctx.send(f'I could not deliver your message. ¯\_(ツ)_/¯, probably as your bot isn\'t in the server '
                           f'send {self.bot.user.id} to <@340869611903909888>')
        else:
            await ctx.send('I have delivered your message to <@340869611903909888> (I may be in contact), '
                           'this command is limited to working every 2 hours so you can\'t spam me')

    @commands.command()
    async def ping(self, ctx):
        """Check if your bot is online on both Steam and Discord"""
        start = perf_counter()
        await ctx.trigger_typing()
        end = perf_counter()
        t_duration = (end - start) * 1000

        start = perf_counter()
        m = await ctx.send(embed=Embed(color=self.bot.color).set_author(name='Pong!'))
        end = perf_counter()
        m_duration = (end - start) * 1000

        if self.bot.client.logged_on:
            message = f'<:tick:626829044134182923> You are logged in as: `{self.bot.client.user.name}`'
        else:
            message = '<:goodcross:626829085682827266> You aren\'t logged into steam'

        embed = Embed(description=f'{self.bot.user.mention} is online. {message}', colour=self.bot.color)
        embed.set_author(name='Pong!', icon_url=self.bot.user.avatar_url)
        embed.add_field(name=f'Websocket latency is:', value=f'`{self.bot.latency:.2f}` ms.')
        embed.add_field(name=f'Typing latency is:', value=f'`{t_duration:.2f}` ms.')
        embed.add_field(name=f'Message latency is:', value=f'`{m_duration:.2f}` ms.')

        await m.edit(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def togpremium(self, ctx):
        """Used to remind yourself when your bp.tf premium will run out, probably not very useful"""
        if self.bot.togglepremium == 0:
            self.bot.togglepremium = 1
            await ctx.send(
                'Premium Alerts now toggled on (this will send you a message when 1 months and 29 days have gone past)')
        elif self.bot.togglepremium == 1:
            self.bot.togglepremium = 0
            await ctx.send('Premium Alerts now toggled off')

        while self.bot.togglepremium == 1:
            await sleep((60 * 60 * 24 * 30 * 2) - (60 * 60 * 24))
            await ctx.send('You may wish to renew your premium subscription')

    @commands.command(aliases=['warm-my-insides'])
    @commands.is_owner()
    async def donate(self, ctx):
        """Used to feel warm and fuzzy on the inside"""
        embed = Embed(title='Want to donate?', color=0x2e3bad)
        embed.description = '[Trade link](https://steamcommunity.com/tradeoffer/new/?partner=287788226&token=NBewyDB2)'
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.png?size=1024')
        embed.set_footer(text='Thank you for any donations')
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command"""
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
                            value='Please send <@340869611903909888> the error outputted in the shell and your log')
            await ctx.send(embed=embed)
            raise error.original
        else:
            title = 'Unspecified error'
            error = 'Please try again, and maybe send <@340869611903909888> the error outputted in the shell'
        embed = Embed(title=f':warning: **{title}**', description=str(error), color=Colour.red())
        await ctx.send(embed=embed)
        raise error


def setup(bot):
    bot.add_cog(Help(bot))
