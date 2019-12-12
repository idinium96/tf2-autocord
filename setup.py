#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIT License
Copyright (c) 2019 James H-B
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from shutil import rmtree
from os import remove
from json import dumps
from setuptools import setup
from platform import python_version


print(f'This is the setup code for tf2-autocord:\nYour python version is {python_version()}\n\n')
print('Do you have your main account\'s shared secret and client secret')
automatic = input('>>> ').lstrip().lower()

if automatic == 'yes' or automatic == 'y':
    automatic = True
else:
    automatic = False

choice = 0
while 1:
    print('Bot\'s Steam ID:\nThis is the 64 ID of your bot\'s steam account')
    BSID = int(input('>>> ').lstrip())
    print('Command Prefix:\nMost people use ! (this will be the same for your discord and steam bot)\n'
          'eg. if you are hackerino you type .profit on discord and it would send .profit to your steam bot')
    CP = input('>>> ').lstrip()
    print('Embed Colour:\nThis is the colour of the accent when you type !help or !info. NO # AT THE START')
    EC = input('>>> ').lstrip()
    print(
        'Path to Temp:\nThis is for the !get command you need it in the format C:/Users/Nicklason/Desktop/all the '
        'code for the bots/temp')
    PTT = input('>>> ').lstrip()

    preferences = {
        "Bot's Steam ID": BSID,
        "Command Prefix": CP,
        "Embed Colour": EC,
        "Path to Temp": PTT
    }

    print(preferences)
    choice = input('Are you happy with these? (you can change them later)\n>>> ').lstrip().lower()
    if choice == 'yes' or choice == 'y':
        break

choice = 0
while 1:
    BT = input("Bot Token:\nCopy this from discord.app and the bot section in your application\n>>> ").lstrip()
    U = input("Username:\nThis is your steam username\n>>> ").lstrip()
    P = input("Password:\nThis is your steam password\n>>> ").lstrip()
    if automatic:
        IS = input("Identity Secret:\nThis is your steam identitiy secret\n>>> ").lstrip()
        SS = input("Shared Secret:\nThis is your steam shared secret\n>>> ").lstrip()
        sensitives = {
            "Bot Token": BT,
            "Username": U,
            "Password": P,
            "Identity Secret": IS,
            "Shared Secret": SS
        }
    else:
        sensitives = {
            "Bot Token": BT,
            "Username": U,
            "Password": P
        }
    print(sensitives)
    print('Are you happy with these? (you can change them later)')
    choice = input('\n>>> ')
    if choice == 'yes' or choice == 'y':
        break

print('Beginning to install necessary modules, please wait.')

setup(
    name='tf2autocord',
    version='1.3.1',
    url='https://github.com/Gobot1234/tf2-autocord',
    license='MIT',
    author='James H-B',

    description='A discord bot used to forward your tf2automatic bot\'s messages from steam to discord.',
    long_description='README',
    project_urls={
        'Install guid': 'https://github.com/Gobot1234/tf2autocord',
        'Code': 'https://github.com/Gobot1234/tf2autocord',
        'Issue tracker': 'https://github.com/Gobot1234/tf2autocord/issues'
    },

    install_requires=["discord.py", "steam", "psutil", "matplotlib", "ago", "humanize"],
    python_requires='>=3.6.0',
    keywords='tf2autocord tf2automatic discord.py discord',
    scripts=['Cogs/discord.py', 'Cogs/steam.py', 'Cogs/help.py', 'Cogs/loader.py']
)

print('Done downloading/updating appropriate modules\nAbout to make the login details directory')
path = f'/Login details/'

rmtree('build')
rmtree('dist')
rmtree('tf2autocord.egg-info')
if automatic:
    remove('Main_-_cli_login.py')
else:
    remove('Main_-_Automatic_Login.py')
print(f"Successfully created the directory {path}")
open(f'{path}preferences.json', 'w+').write(dumps(preferences, indent=4))
open(f'{path}sensitive_details.json', 'w+').write(dumps(sensitives, indent=4))
open(f'{path}profit_graphing.json', 'w+').write(dumps('{}'))
print('Setup complete feel free to close this window')
remove('setup.py')
