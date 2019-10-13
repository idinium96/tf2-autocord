import discord
from discord.ext import commands, tasks

import os

from .loader import LoaderCog


class HelperCog(commands.Cog, name='Help'):
    """Help yourself to do stuff with the bot's commands"""

    def __init__(self, bot):
        self.bot = bot
        self.githubupdate.start()

    @tasks.loop(hours=24)
    async def githubupdate(self):
        os.system('cd ' + os.getcwd())
        updateable = os.popen('git checkout').read()
        if 'Your branch is up to date with' in updateable:
            pass
        else:
            await self.bot.get_user(self.bot.owner_id).send(
                'There is an update to the repo. Do you want to install it? '
                f'(Type {self.bot.command_prefix}updaterepo to install it)')

    @commands.command()
    @commands.is_owner()
    async def updaterepo(self, ctx):
        """Used to update to the newest version of the code

        This will overwrite any changes you have made locally"""
        await ctx.send('Attempting to update to the latest version of the code')
        os.system(f'cd {os.getcwd()}')
        os.system('git reset --hard HEAD')
        updateable = os.popen('git pull').read()
        if 'Already up to date.' in updateable:
            await ctx.send('No updates to be had?')
        else:
            await ctx.send('Updating from the latest GitHub push\n'
                           'You will need to restart for the update to take effect')

    @commands.command()
    async def github(self, ctx):
        """Shows the GitHub repo and some info about it"""
        os.system(f'cd {os.getcwd()}')
        updateable = os.popen('git checkout').read()
        if 'Your branch is up to date with' in updateable:
            emoji = '<:tick:626829044134182923>'
        else:
            emoji = '<:goodcross:626829085682827266>'
        embed = discord.Embed(title='GitHub Repo Infomation', color=0x2e3bad)
        embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
        embed.add_field(name='Current Version', value=f'Version: {LoaderCog.__version__}. Up to date: {emoji}',
                        inline=True)
        embed.add_field(name='GitHub Stats', value='https://github.com/Gobot1234/tf2-autocord/pulse')
        embed.add_field(name='Link to the repo', value='[Repository](https://github.com/Gobot1234/tf2-autocord)')
        embed.add_field(name='Want to check for an update?', value=f'{self.bot.command_prefix}updaterepo')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        """Suggest a feature to <@340869611903909888>

        :suggestion [required]
         eg. `!suggest update the repo`"""
        author = ctx.message.author
        embed = discord.Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name=f'Message from {str(author)}')
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
    async def help(self, ctx, help = None):
        """Get help with a cog or command

        :help [required]
        eg. `!help Steam` (There should be 4 cogs and 22 commands)"""
        help = help or 'Help'
        help = help.captialize()
        if 'Help' in help:
            color = self.bot.color
            emoji = '<:tf2autocord:624658299224326148>'
            helper = 'cogs'
        elif 'Discord' in help:
            color = 0x7289da
            emoji = '<:discord:626486432793493540>'
            helper = 'cogs'
        elif 'Steam' in help:
            color = 0x00adee
            emoji = '<:steam:622621553800249364>'
            helper = 'cogs'
        elif 'Loader' in help:
            await ctx.send('Nothing interesting happens in the loader cog')
            return
        else:
            helper = 'commands'
            emoji = '<:tf2autocord:624658299224326148>'
            color = self.bot.color

        allcogs = ''
        for x in self.bot.cogs:
            allcogs += f'`{x}`, '
            allcogs = allcogs.replace('`Loader`, ', '')

        found = False
        if helper == 'cogs':
            for x in self.bot.cogs:
                for y in help:
                    if x == y:
                        halp = discord.Embed(title=f'Help with {help} commands {emoji}',
                                             description=self.bot.cogs[help].__doc__, color=color)
                        halp.add_field(name='**Bot description:**', value=self.bot.description)
                        halp.add_field(name=f'The current loaded cogs are ({allcogs[:-2]}) :gear:', value='​')
                        for c in self.bot.get_cog(y).get_commands():
                            if len(c.signature) == 0:
                                command = f'`{self.bot.command_prefix}{c.name}`'
                            else:
                                command = f'`{self.bot.command_prefix}{c.name} {c.signature}`'
                            halp.add_field(name=command, value=c.short_doc,
                                           inline=False)
                        found = True
        elif helper == 'commands':
            commandlist = []
            for command in self.bot.commands:
                commandlist.append(command.name)
            helpl = help.lower()
            if helpl in commandlist:
                halp = discord.Embed(
                    title=f'Help with the `{self.bot.command_prefix}{self.bot.get_command(helpl)}` command {emoji}',
                    color=color)
                halp.add_field(name='**Bot description:**', value=self.bot.description)
                if len(self.bot.get_command(helpl).signature) != 0:
                    args = f'Arguments = `{self.bot.get_command(helpl).signature}`'
                else:
                    args = '\u200b'
                halp.add_field(name=args, value=self.bot.get_command(helpl).help)
                found = True
        if not found:
            halp = discord.Embed(title='Error!',
                                 description=f'**Error 404:** Command or Cog \"{help}\" not found ¯\_(ツ)_/¯',
                                 color=discord.Color.red())

            halp.add_field(name=f'Current loaded Cogs are ({allcogs[:-2]}) :gear:', value='​')

        halp.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435",
                        icon_url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.webp?size=1024')
        await ctx.send(embed=halp)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""
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
        else:
            title = 'Unspecified error'
            error = 'Please try again, and maybe send <@340869611903909888> the error outputted in the shell'
        embed = discord.Embed(title=f':warning: **{title}**', description=str(error), color=discord.Colour.red())
        await ctx.send(embed=embed)
        raise error


def setup(bot):
    bot.add_cog(HelperCog(bot))
