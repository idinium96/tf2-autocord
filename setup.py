import os

# define the name of the directory to be created
path = "Login details/"

try:
    os.mkdir(path)
except OSError:
    print("Creation of the directory %s failed" % path)
else:
    print("Successfully created the directory %s " % path)
    with open(path + "sensitive details.txt", "w+") as f:
        f.write("Token:\n  # put your bot's token here\nUsername:\n  # put your steam username here\nPassword:\n  # put your steam password here")
    with open(path + "preferences.txt", "w+") as f:
        f.write("Discord ID:\n  # put your discord id here\nBot's steam 64 ID:\n  # put your bot's steam id here\nOwner name:\n  # add your name\nDiscord command prefix:\n  # change your command prefix\nSteam bot command prefix:\n  # don't change this unless you are hackerino\nEmbed Color:\n  # hex code here (no #)")
    os.remove('setup.py')
