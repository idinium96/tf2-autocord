import os
import json

preferences = {
    "Discord ID": "Copy this from yourself by turning on developer mode in appearance and right click and copy ID on yourself",
    "Bot's Steam ID": "You want the 64 ID",
    "Owner Name": "Put the name you want to appear in its status",
    "Command Prefix": "! Most people use this? This is for discord and your steam bot",
    "Embed Colour": "This is the colour of the accent when you type !help or !info. NO # AT THE START",
}

sensitives = {
    "Bot Token": "Copy this from discord.app and the bot section in your application",
    "Username": "This is your steam username",
    "Password": "This is your steam password"
}

path = "Login details/"

os.system('pip install -U steam')
os.system('py -3 -m pip install -U discord.py')
print('Done downloading/updating appropriate modules')

try:
    os.mkdir(path)
except OSError:
    print("Creation of the directory %s failed" % path)
else:
    print("Successfully created the directory %s " % path)
    with open(path + 'preferences.json', 'w+') as f:
        f.write(json.dumps(preferences, indent=2))
    with open(path + 'sensitive details.json', 'w+') as f:
         f.write(json.dumps(sensitives, indent=2))
    os.remove('setup.py')
    print('Setup complete feel free to close this window')
