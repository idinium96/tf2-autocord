import os
import json

print('This is the setup code for tf2-autocord')
choice = 0
while choice != 'yes':
    DID = int(input("Discord ID:\nCopy this from yourself by turning on developer mode in appearance and right click and copy ID on yourself\n>>> "))
    BSID = int(input("Bot's Steam ID:\nThis is the 64 ID of your bot's steam account\n>>> "))
    ON = input("Owner Name:\nThis is your name, this will show up in your bot's status\n>>> ")
    CP = input("Command Prefix:\nMost people use ! (this will be the same for your discord and steam bot)\neg. if you are hackerino you type .profit on discord and it would send .profit to your steam bot\n>>> ")
    EC = input("Embed Colour:\nThis is the colour of the accent when you type !help or !info. NO # AT THE START\n>>> ")
    PTT = input("Path to Temp:\nThis is for the !get command you need it in the format C:/Users/Nicklason/Desktop/all the code for the bots/temp\n>>> ")


    preferences = {
        "Discord ID": DID,
        "Bot's Steam ID": BSID,
        "Owner Name": ON,
        "Command Prefix": CP,
        "Embed Colour": EC,
        "Path to Temp": PTT
    }

    print(preferences)
    choice = input('Are you happy with these? (you can change them later)\n>>> ')

choice = 0
while choice != 'yes':
    BT = input("Bot Token:\nCopy this from discord.app and the bot section in your application\n>>> ")
    U = input("Username:\nThis is your steam username\n>>> ")
    P = input("Password:\nThis is your steam password\n>>> ")

    sensitives = {
        "Bot Token": BT,
        "Username": U,
        "Password": P
    }
    print(sensitives)
    choice = input('Are you happy with these? (you can change them later)\n>>> ')

path = "Login details/"

print('Beginning to install necessary modules')
os.system('pip install -U steam')
os.system('py -3 -m pip install -U discord.py')
print('Done downloading/updating appropriate modules\nAbout to make the login details directory')

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
