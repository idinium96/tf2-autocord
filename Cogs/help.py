import discord
from discord.ext import commands, tasks
from .loader import LoaderCog

import os, sys


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
    async def restart(self, ctx):
        """Used to reset the bot (this won't work use this if you use cli_login)"""
        if self.bot.cli_login:
            await ctx.send('You really shouldn\'t do this')
        else:
            await ctx.send('**Restarting the bot**')
            os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(aliases=['reconnect', 'logged_on'])
    @commands.is_owner()
    async def relogin(self, ctx):
        """Attempt to reconnect to Steam, if you logged out"""
        if self.bot.client.logged_on:
            await ctx.send(f'You are already logged in as {self.bot.client.user.name}')
        else:
            await ctx.send("Reconnecting...")
            async with ctx.typing():
                if self.bot.client.relogin_available:
                    self.bot.client.reconnect(maxdelay=30)
                    await ctx.send('Reconnected to Steam')
                else:
                    await ctx.send('Try again later or restart the program')

    @commands.command()
    @commands.is_owner()
    async def updaterepo(self, ctx):
        """Used to update to the newest version of the code"""
        await ctx.send('Attempting to update to the latest version of the code')
        os.system('cd ' + os.getcwd())
        updateable = os.popen('git pull').read()
        if 'Already up to date.' in updateable:
            await ctx.send('No updates to be had?')
        else:
            await ctx.send('Updating from the newest GitHub push and restarting')
            os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    async def github(self, ctx):
        """Shows the GitHub repo and some info about it"""
        os.system('cd ' + os.getcwd())
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
        """Suggest a feature to Gobot1234 (the developer) eg. `!suggest update the repo`"""
        author = ctx.message.author
        embed = discord.Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name=f'Message from {str(author)}')
        try:
            await self.bot.get_user(340869611903909888).send(embed=embed)
        except:
            await ctx.send("I could not deliver your message. ¯\_(ツ)_/¯")
        else:
            await ctx.send("I have delivered your message to Gobot1234#2435 (I may be in contact)"
                           ", this command is limited to working every 2 hours so you can't spam me")

    @commands.command()
    async def ping(self, ctx):
        """Check if your bot is online"""
        await ctx.send(f'Pong! {self.bot.user.name} is online. Latency is {round(self.bot.latency, 2)} ms')

    @commands.command()
    async def help(self, ctx, *cog):
        """Get help with a cog eg. `!help Steam`"""
        cog = tuple((str(word).capitalize() for word in cog))
        if str(cog) == '()' or 'Help' in cog:
            cog = ('Help',)
            color = self.bot.color
            emoji = '<:tf2autocord:624658299224326148>'
        elif 'Discord' in cog:
            color = int('0x7289da', 16)
            emoji = '<:discord:626486432793493540>'
        elif 'Steam' in cog:
            color = int('0x00adee', 16)
            emoji = '<:steam:622621553800249364>'
        elif 'Loader' in cog:
            await ctx.send('Nothing interesting happens in the loader cog')
            return
        if len(cog) > 1:
            halp = discord.Embed(title='Error!', description=f'\"{cog}\" That is too many cogs!',
                                 color=discord.Color.red())
        else:
            found = False
            for x in self.bot.cogs:
                for y in cog:
                    if x == y:
                        halp = discord.Embed(title=f'Help with {cog[0]} commands {emoji}',
                                             description=self.bot.cogs[cog[0]].__doc__, color=color)
                        allcogs = ''
                        for x in self.bot.cogs:
                            allcogs += '`' + x + '`' + ', '
                            allcogs = allcogs.replace('`Loader`, ', '')
                        halp.add_field(name=f'Current loaded Cogs are ({allcogs[:-2]}) :gear:', value='​')
                        for c in self.bot.get_cog(y).get_commands():
                            if len(c.signature) == 0:
                                command = f'`{self.bot.command_prefix}{c.name}`'
                            else:
                                command = f'`{self.bot.command_prefix}{c.name} {c.signature}`'
                            halp.add_field(name=command, value=c.help,
                                           inline=False)
                        found = True
            if not found:
                halp = discord.Embed(title='Error!',
                                     description=f'**Error 404:** Cog \"{cog[0]}\" not found ¯\_(ツ)_/¯',
                                     color=discord.Color.red())
                allcogs = ''
                for x in self.bot.cogs:
                    allcogs += '`' + x + '`' + ', '
                    allcogs = allcogs.replace('`Loader`, ', '')
                halp.add_field(name=f'Current loaded Cogs are ({allcogs[:-2]}) :gear:', value='​')

        halp.set_footer(text="If you need any help contact the creator of this code @Gobot1234#2435",
                        icon_url='https://cdn.discordapp.com/avatars/340869611903909888/6acc10b4cba4f29d3c54e38d412964cb.webp?size=1024')
        await ctx.send(embed=halp)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please pass in **all** required arguments')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You can\'t use that command for another {round(error.retry_after / 60, 1)} minutes')
        elif isinstance(error, commands.NotOwner):
            await ctx.send('You need to be the **Owner** of the bot to perform this command.')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send('I don\'t know what you mean, **please type "!help"** to see all my commands!')
        else:
            await ctx.send('**Unspecified error.** Please try again.')
        raise error


def setup(bot):
    bot.add_cog(HelperCog(bot))
