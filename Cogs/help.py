import discord
from discord.ext import commands, tasks

import os, sys

class HelperCog(commands.Cog, name='Help'):
    """Help commands"""
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
            await self.bot.get_user(self.bot.owner_id).send(f'There is an update to the repo. Do you want to install it? '
                                                  f'(Type {self.bot.command_prefix}updaterepo to install it)')

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Used to reset the bot (don't use this if you use cli_login)"""
        await ctx.send('Restarting the bot')
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(aliases=['reconnect', 'logged_on'])
    @commands.is_owner()
    async def relogin(self, ctx):
        """Attempt to reconnect to Steam"""
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
            await ctx.send('Updating from the newest GitHub push')
            os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    async def github(self, ctx):
        """Shows the GitHub repo and some info about it"""
        url = 'https://github.com/Gobot1234/tf2-autocord/pulse'
        embed = discord.Embed(title='GitHub Repo Infomation', color=0x2e3bad)
        embed.set_thumbnail(url='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png')
        embed.add_field(name='Current Version', value=self.bot.version, inline=True)
        embed.add_field(name='GitHub Stats', value=url)
        embed.add_field(name='Link to the repo', value='[Here](https://github.com/Gobot1234/tf2-autocord)')
        embed.add_field(name='Want to check for an update', value=f'{self.bot.command_prefix}updaterepo')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    @commands.cooldown(rate=1, per=7200, type=commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        """Suggest a feature to Gobot1234"""
        author = ctx.message.author
        embed = discord.Embed(color=0x2e3bad, description=suggestion)
        embed.set_author(name=f'Message from {str(author)}')
        try:
            await self.bot.get_user(340869611903909888).send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I could not deliver your message. Perhaps it is too long?")
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
        """Get help with a cog eg. !help Steam"""
        cog = tuple((str(word).capitalize() for word in cog))
        if str(cog) == '()' or 'Help' in cog:
            cog = ('Help',)
            color = self.bot.color
        elif 'Discord' in cog:
            color = int('0x7289da', 16)
        elif 'Steam' in cog:
            color = int('0x00adee', 16)
        try:
            if not cog:

                halp = discord.Embed(title='Cog Listing and Uncatergorized Commands',
                                     description='Use `!help *cog*` to find out more about them')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += f'{x} - {self.bot.cogs[x].__doc__}\n'
                halp.add_field(name='Cogs', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += f'{y.name} - {y.help}\n'
                halp.add_field(name='Uncatergorized Commands', value=cmds_desc[0:len(cmds_desc) - 1], inline=False)
                await ctx.message.author.send('', embed=halp)
            else:
                if len(cog) > 1:
                    halp = discord.Embed(title='Error!', description=f'\"{cog}\" That is too many cogs!',
                                         color=discord.Color.red())
                    await ctx.message.author.send(embed=halp)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                halp = discord.Embed(title=f'Help with {cog[0]} Commands',
                                                     description=self.bot.cogs[cog[0]].__doc__, color=color)
                                allcogs = ''
                                for x in self.bot.cogs:
                                    allcogs += x + ', '
                                halp.set_author(name=f'Current loaded Cogs are ({allcogs[:-2]})')
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        halp.add_field(name=self.bot.command_prefix + c.name, value=c.help, inline=False)
                                found = True
                    if not found:
                        halp = discord.Embed(title='Error!', description=f'**Error 404:** Cog \"{cog[0]}\" not found ¯\_(ツ)_/¯',
                                             color=discord.Color.red())

                    await ctx.message.author.send(embed=halp)
        except:
            pass


def setup(bot):
    bot.add_cog(HelperCog(bot))
