import traceback
from json import dumps, loads
from contextlib import redirect_stdout
from inspect import getsource, getsourcelines
from io import StringIO
from platform import python_version
from subprocess import getoutput
from sys import stderr
from textwrap import indent
from traceback import print_exc
from time import perf_counter

from discord import Embed, Colour, File
from discord.ext import commands, buttons
from .loader import __version__


class Development(commands.Cog):
    """Custom commands for <@340869611903909888> and tf2autocord's development, you probably shouldn't have these"""

    def __init__(self, bot):
        self.bot = bot
        self.todo_loc = 'Login_details/todo.json'
        self._last_result = None

    def read(self, file):
        """Read sterilized info from a json file"""
        return loads(open(file, 'r').read())

    def dump(self, file, dump):
        """Dump info to a json file"""
        open(file, 'w').write(dumps(dump, indent=4))

    def format_exec(self, exc):
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def failed(self, ctx, extension, error):
        await ctx.send(f'**`ERROR:`** `{extension}` {self.format_exec(error)}')
        print(f'Failed to load extension {extension}.', file=stderr)
        print_exc(f'{extension} {type(error).__name__} - {error}')
        raise error

    @commands.group(invoke_without_command=True, aliases=['t'])
    @commands.is_owner()
    async def todo(self, ctx):
        """Command parent for todo command, if no subocommand is passed it will show your todo list"""
        if ctx.invoked_subcommand is None:
            file = self.read(self.todo_loc)
            to_send = '\n'.join([f'{num}. {todo}' for num, todo in enumerate(file, start=1)])
            embed = Embed(color=self.bot.color, description=to_send)
            embed.set_author(name=f'{len(file)} Reminders Total {ctx.author.name}:', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @todo.command()
    async def add(self, ctx, *, todo):
        """Add something to your todo list"""
        todos = self.read(self.todo_loc)
        todos.append(todo)
        self.dump(self.todo_loc, todos)
        await ctx.send(f'> Added reminder, to index number {len(todos)} - `{todo}` to your todo list')

    @todo.command()
    async def remove(self, ctx, *index: int):
        """Remove something from your todo list"""
        removed = []
        todos = self.read(self.todo_loc)
        for to_remove in index:
            try:
                removed.append(todos[to_remove - 1])
                todos.pop(to_remove - 1)
            except IndexError:
                await ctx.send(f'There is no `{to_remove}` in your todo list')
            else:
                self.dump(self.todo_loc, todos)
        await ctx.send(f'> Removed index number: `{", ".join(str(to_remove) for to_remove in index)}` - '
                       f'`{", ".join(removed)}`, from your todo list')

    @todo.command()
    async def edit(self, ctx, index: int, *, edit):
        """Edit a todo using its index"""
        todos = self.read(self.todo_loc)
        before = todos[index - 1]
        todos[index - 1] = edit
        self.dump(self.todo_loc, todos)
        await ctx.send(f'> Edited index number: `{index}` - before it was `{before}`, now it is `{edit}`')

    @commands.command()
    @commands.is_owner()
    async def embed(self, ctx, colour=None, fields: dict = None, title=None, desc=None, image=None, author=None,
                    icon_url=None, footer=None, footer_icon=None):
        colour = self.bot.color or int(colour, 16)
        embed = Embed(title=title, description=desc, color=colour)
        for name, value in fields.items():
            if value == '':
                value = '\u200b'
            embed.add_field(name=name, value=value)
        if image:
            embed.set_image(url=image)
        if author and icon_url:
            embed.set_author(name=author, icon_url=icon_url)
        if footer and footer_icon:
            embed.set_footer(text=footer, icon_url=footer_icon)
        await ctx.send(embed=embed)

    @commands.command(aliases=['r'])
    @commands.is_owner()
    async def reload(self, ctx, *, extension=None):
        """You probably don't need to use this, however it can be used to reload a cog

        eg. `{prefix}reload loader`"""
        await ctx.trigger_typing()
        if extension is None:
            reloaded = ''
            for extension in self.bot.initial_extensions:
                try:
                    self.bot.reload_extension(f'Cogs.{extension}')
                except commands.ExtensionNotLoaded:
                    try:
                        self.bot.load_extension(f'Cogs.{extension}')
                    except Exception as e:
                        await self.failed(ctx, extension, e)
                except Exception as e:
                    reloaded += f'<:goodcross:626829085682827266> `{extension}`\n'
                    await self.failed(ctx, extension, e)

                else:
                    reloaded += f'<:tick:626829044134182923> `{extension}`\n'
            return await ctx.send(f'**`SUCCESS`** reloaded {len(self.bot.initial_extensions)} cogs \n{reloaded}')

        extension = f'Cogs.{extension}'
        try:
            self.bot.reload_extension(extension)
        except commands.ExtensionNotLoaded:
            if extension[-5] in self.bot.initial_extensions:
                try:
                    self.bot.load_extension(f'Cogs.{extension}')
                except Exception as e:
                    await self.failed(ctx, extension, e)
                else:
                    await ctx.send(f'**`SUCCESS`** <:tick:626829044134182923> `{extension}` has been reloaded')
        except Exception as e:
            await self.failed(ctx, extension, e)
        else:
            await ctx.send(f'**`SUCCESS`** <:tick:626829044134182923> `{extension}` has been reloaded')

    @commands.command(name='eval', aliases=['e'])
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """This will evaluate your code-block if type some python code.
        **PLEASE BE AWARE THIS IS A POTENTIALLY DANGEROUS COMMAND TO USE IF YOU DON'T KNOW WHAT YOU'RE DOING**

        Input is interpreted as newline separated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `client`: the SteamClient instance
          - `bot`: the bot instance
          - `commands`: the discord.ext.commands module
          - `ctx`: the invocation context

        eg. `{prefix}eval` ```py
        await ctx.send(f'Hello my name is {bot.user.name} :wave:. Type {bot.prefix}help to see what I can do')```
        """
        async with ctx.typing():
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'client': self.bot.client,
                'commands': commands,
                'self': self,
            }

            env.update(globals())
            body = self.cleanup_code(body)
            stdout = StringIO()
            to_compile = f'async def func():\n{indent(body, "  ")}'

            try:
                start = perf_counter()
                exec(to_compile, env)
            except Exception as e:
                end = perf_counter()

                await ctx.message.add_reaction(':goodcross:626829085682827266')
                embed = Embed(title=f'<:goodcross:626829085682827266> {e.__class__.__name__}',
                              description=f'```py\n{self.format_exec(e)}```',
                              color=Colour.red())
                embed.set_footer(
                    text=f'Python: {python_version()} • Process took {round((end - start) * 1000, 2)} ms to run',
                    icon_url='https://www.python.org/static/apple-touch-icon-144x144-precomposed.png')
                return await ctx.send(embed=embed)
            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                end = perf_counter()

                await ctx.message.add_reaction(':goodcross:626829085682827266')
                embed = Embed(title=f'<:goodcross:626829085682827266> {e.__class__.__name__}',
                              description=f'```py\n{value}{self.format_exec(e)}```',
                              color=Colour.red())
                embed.set_footer(
                    text=f'Python: {python_version()} • Process took {round((end - start) * 1000, 2)} ms to run',
                    icon_url='https://www.python.org/static/apple-touch-icon-144x144-precomposed.png')
                return await ctx.send(embed=embed)
            else:
                value = stdout.getvalue()
                end = perf_counter()

                await ctx.message.add_reaction(':tick:626829044134182923')
                if isinstance(ret, File):
                    await ctx.send(file=ret)
                elif isinstance(ret, Embed):
                    await ctx.send(embed=ret)
                else:
                    if not isinstance(value, str):
                        # repr all non-strings
                        value = repr(value)

                    embed = Embed(title=f'Evaluation completed {ctx.author.display_name} <:tick:626829044134182923>',
                                  color=Colour.green())
                    if ret is None:
                        if value:
                            embed.add_field(name='Eval complete', value='\u200b')
                    else:
                        self._last_result = ret
                        embed.add_field(name='Eval returned', value=f'```py\n{value}{ret}```')
                    embed.set_footer(
                        text=f'Python: {python_version()} • Process took {round((end - start) * 1000, 2)} ms to run',
                        icon_url='https://www.python.org/static/apple-touch-icon-144x144-precomposed.png')
                    await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx, *, command=None):
        """Get the source code for any command"""
        source_url = 'https://github.com/Gobot1234/tf2-autocord'
        if command is None:
            return await ctx.send(source_url)

        cmd = self.bot.get_command(command)

        try:
            source = getsource(cmd.callback)
        except AttributeError:
            return await ctx.send(f"Could not find command `{command}`.")
        if len(source) + 8 <= 2000:
            await ctx.send(f'```py\n{source}\n```')
        else:
            branch = 'master'
            obj = self.bot.get_command(command.replace('.', ' '))

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__

            lines, firstlineno = getsourcelines(src)
            location = module.replace('.', '/') + '.py'

            final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
            await ctx.send(
                f"Source was too long to post on discord, so here's the url to the source on GitHub:\n{final_url}")

    @commands.group()
    @commands.is_owner()
    async def git(self, ctx):
        pass

    @git.command()
    async def push(self, ctx, version=__version__, *, commit_msg='None given'):
        await ctx.message.add_reaction('\U000023f3')
        add = await self.bot.loop.run_in_executor(None, getoutput, 'git add .')
        commit = await self.bot.loop.run_in_executor(None, getoutput, f'git commit -m "{version}" -m "{commit_msg}"')
        push = await self.bot.loop.run_in_executor(None, getoutput, 'git push')
        if 'error: failed' in push:
            await ctx.message.add_reaction(':goodcross:626829085682827266')
        else:
            await ctx.message.add_reaction(':tick:626829044134182923')
        out = buttons.Paginator(title=f'GitHub push output', colour=self.bot.color, embed=True, timeout=90,
                                entries=[f'**Add:** {add}', f'**Commit:** {commit}', f'**Push:** {push}'])
        await out.start(ctx)


def setup(bot):
    bot.add_cog(Development(bot))
