from discord.ext import commands
import json
from steam.client import SteamClient


class LoaderCog(commands.Cog, name='Loader'):
    """This cog just stores all of your variables nothing particularly interesting"""
    __version__ = '1.1.3'

    def __init__(self, bot):
        self.bot = bot

        login = json.loads(open("Login details/sensitive details.json", "r").read())
        bot.username = login["Username"]
        bot.password = login["Password"]
        bot.secrets = {
            "identity_secret": login["Identity Secret"],
            "shared_secret": login["Shared Secret"]
        }
        preferences = json.loads(open('Login details/preferences.json', 'r').read())
        bot.owner_id = int(preferences["Discord ID"])
        bot.bot64id = int(preferences["Bot's Steam ID"])
        bot.owner_name = preferences["Owner Name"]
        bot.command_prefix = preferences["Command Prefix"]
        bot.color = int(preferences["Embed Colour"], 16)
        bot.templocation = preferences["Path to Temp"]

        bot.sbotresp = 0
        bot.usermessage = 0
        bot.logged_on = 0
        bot.toggleprofit = 0
        bot.botresp = False
        bot.client = SteamClient()
        bot.dsdone = 0

        bot.updatem = bot.command_prefix + 'update name='
        bot.removem = bot.command_prefix + 'remove item='
        bot.addm = bot.command_prefix + 'add name='


def setup(bot):
    bot.add_cog(LoaderCog(bot))
