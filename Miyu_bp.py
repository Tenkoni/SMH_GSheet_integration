# Copyright 2019 Tenko(LEMS)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
#and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#OR OTHER DEALINGS IN THE SOFTWARE.

import discord
import os
import operator
import csv
import random
import asyncio
import datetime
import pygsheets
import numpy as np
import re
from shutil import copyfile
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands


BOT_PREFIX = "!!"
CWD = os.getcwd()
TOKEN = "--"
client = Bot(command_prefix = BOT_PREFIX)
gc = pygsheets.authorize()
#open spreadsheet
sh = gc.open_by_key('')
#set worksheets
player_income = sh.worksheet_by_title("Player Income")
income_calc = sh.worksheet_by_title("Income Calculator")
#loottype
typesofloot = "Neidan\nAmethyst\nHekaru\nWhisker\nSkin\nSteel\nShell\nFin\nHorn\nTongue\nJaw\nGoblet\nCoin"
#Current develpment:



@client.command(name = 'clean',
                description = 'Cleans the SMH data',
                pass_context = True)
#@commands.has_any_role('Guild Master')
async def clean_smh(context):
    message = await context.send("Master, please wait while I clean the spreadsheet...")
    player_income.clear(start= 'D2', end = 'Q101')
    await message.delete()
    await context.send("The SMH data has been cleaned.")

#this command will register loot
@client.command(name = 'add',
                brief = "Add Neidan, Amethyst, Hekaru, Whisker, Skin, Steel, Shell, Fin, Horn, Tongue, Jaw, Goblet and Coin drops to your loot",
                description = "Usage: !!add <neidan|amethyst|hekaru|whisker|skin|steel|shell|fin|horn|tongue|jaw|goblet|coin> quantity \n example: .add neidan 550",
                pass_context = True)
#@commands.has_any_role('Guild Member')
async def add_smh(context, loot_type: str, quantity: float, bymention = False):
    #this block will update the file, search for discord id and updates the information
    await adding(context, loot_type, quantity, bymention = False)
@add_smh.error
async def add_smh_error(context, error):
    await context.send("You got the arguments wrong! It must be something like this: `!!add neidan 300 imgur.com/pic.jpg` ")

@client.command(name = 'add_split',
                brief = "Add Neidan, Amethyst, Hekaru, Whisker, Skin, Steel, Shell, Fin, Horn, Tongue, Jaw, Goblet and Coin drops to your loot",
                description = "Usage: !!add_split <neidan|amethyst|hekaru|whisker|skin|steel|shell|fin|horn|tongue|jaw|goblet|coin> quantity <@partner> <70|60|65|50> \n example: !!add_split neidan 550 imgur.com/pic.jpg @fren 70",
                pass_context = True)
async def add_split(context,loot_type: str, quantity: float, mention:str, splitmode:str):
    if float(splitmode) >=100 and float(splitmode)<=0:
        context.send("Just numbers between 0 and 100 are allowed, don't try to cheat.")
    split = float(splitmode)/100
    await adding(context, loot_type, quantity*split)
    await adding(context, loot_type, quantity*(1-split), bymention = True)


@client.command(name = 'show_tiers',
                brief = 'Display the current tiers for smh.',
                pass_context = True)
#@commands.has_any_role('Members')

async def show_tiers_smh(context):
    tiernumbers = '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n'
    tierprofit = ''
    for tier in income_calc.range('L14:L23'):
        tierprofit += '${:10,.0f}'.format(MoneyToInt(tier[0].value)) +'\n'
    embed = discord.Embed(title = 'Current tiers', description="Here are the tiers for this week!", color= 0xff9baa)
    embed.add_field(name= 'Tier', value= tiernumbers, inline = True)
    embed.add_field(name= 'Starting loot', value= tierprofit, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/lxblyj.gif") 
    await context.send(embed = embed)

@client.command(name = 'loot',
                brief = 'Shows the total guildies loot for this week',
                description = 'This will show the current loot gathered by guildies including their participation percentage',
                pass_context = True)
#@commands.has_any_role('Members')
async def loot_smh(context):

    seahunters = []
    total = guildies = 0
    for line in income_calc.range('B2:B101'):
        if(line[0].value != ''):
            mons = MoneyToInt(line[0].neighbour('right').value)
            seahunters.append((line[0].value, mons))
            total += mons
            guildies += 1        
    if(guildies == 0):
        await context.send("There are no registered sailors, please register someone first.")
        return
    seahunters.sort(key = operator.itemgetter(1), reverse = True)
    namestring = profistring = ''
    if not total:
        total = 1
    for hunter in range(guildies):
        namestring = namestring + '{:>8} {:>16}'.format("**"+str(hunter + 1) + ".** ", seahunters[hunter][0]) +"\n"
        profistring = profistring +'${:15,.2f}'.format(float(seahunters[hunter][1])) + " **(%" + "{0:.2f}".format(100*float(seahunters[hunter][1])/total) + ")**\n"
    embed = discord.Embed(title = 'Weekly loot', description="Here's a compendium of this week loot", color= 0xff9baa)
    embed.add_field(name= 'Family Name', value= namestring, inline = True)
    embed.add_field(name= 'Profit', value= profistring, inline = True)
    #embed.add_field(name= 'Tier', value= tierstring, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/lxblyj.gif")
    if total == 1:
        embed.add_field(name= 'Total weekly profit', value= '${:10,.2f}'.format(0))
    else:
        embed.add_field(name= 'Total weekly profit', value= '${:10,.2f}'.format(total))
    ##embed.add_field()
    await context.send(embed=embed)

@client.command(name = 'enrol',
               brief = "Enrols the user that runs this command",
               description = "usage: !!enrol FamilyName, if the user already exist the bot will notify so, otherwise the user will be added to the database.",
               pass_context = True)
#@commands.has_any_role('Members')
async def enrol_me(context, family:str):
    index_save = 2000; #random number above 100
    flagnewentry = True
    for index, line in enumerate(player_income):
        if line[0] == str(context.message.author.id):
            flagnewentry = False
            await context.send(context.message.author.mention+ ", you're already registered")
            break
        elif line[0] == '':
            index_save = index
            break
    #if the family name wasn't registered before, we create a new row
    if (flagnewentry and index <= 100):
        player_income.update_value('A'+str(index_save + 1), str(context.message.author.id))
        player_income.update_value('B'+str(index_save + 1), family)
        await context.send(context.message.author.mention +", I have added you to the database!")
    elif(index >100):
        await context.send("There are already 100 members registered, please contact an officer.")

@enrol_me.error
async def enrol_me_error(context, error):
    await context.send("You got the arguments wrong! It must be like this: `!!enrol familyname` ")

@client.command(name = 'disenrol',
                brief = "Removes the user from the SMH list",
                description = "usage: !!disenrol @user",
                pass_context = True)
#@commands.has_any_role('Sea Director')
async def disenrol_smh(context, mention:str):
    index_save = 2000
    byebye = False
    for index, line in enumerate(player_income):
        if line[0] == str(context.message.mentions[0].id):
            byebye = True
            index_save = index
            break
        elif line[0] == '' and index > 100:
            break
    if byebye:
        msg1= await context.send("Are you sure you want to delete "+context.message.mentions[0].display_name + " from the spreadsheet? [Yes/No]")
        try:
            ans = await client.wait_for('message', timeout = 10.0)
        except asyncio.TimeoutError:
            await context.send('Timeout: The delete has been cancelled.')
            await msg1.delete()
            return
        if ans.content.upper() == "YES":
            player_income.clear(start= 'D'+str(index_save+1), end = 'Q'+str(index_save + 1))
            player_income.update_value('A'+str(index_save + 1), '')
            player_income.update_value('B'+str(index_save + 1), '')
            await msg1.delete()
            await ans.delete()
            await context.send("The traitor has been removed from premises.")
        else:
            await msg1.delete()
            await ans.delete()
            await context.send("The delete has ben cancelled.")

    else:
        await context.send("There's no such person registered, check again please.")

@disenrol_smh.error
async def disenrol_smh_error(context, error):
    print(error)
    await context.send("You got wrong your arguments, remember to mention someone.")

@client.command(name = 'sailors',
                description = 'Shows the Family Name of the people that has contributed.')
#@commands.has_any_role('Members')
async def sailors(context):
    hunters = ''
    membs = -1
    ga = 0
    for index, line in enumerate(player_income):
        if(line[0]!=''):
            membs += 1
            if (MoneyToInt(line[2]) != 0):
                hunters += line[1] + "\n"
                ga += 1
        if(index>100):
            break
    if membs == -1:
        await context.send("There are no registered sailors, please register someone first.")
        return
    await context.send("```" +"The are " + str(ga)+ " active members of "+ str(membs)+" members, this making a participation of %" +"{0:.2f}".format(100*ga/membs) +": \n" + hunters +"```" )

# @client.command(name = 'tracker',
#                 description = 'Give me an id and I will track someone',
#                 context = False)
# async def tracker(trackid : str):
#     await client.say ("Oh... let me see.")
#     user = await client.get_user_info(trackid)
#     await client.say(user.mention + "<- I found this person!")
# @tracker.error
# async def disenrol_smh_error(context, error):
#     await client.say("I-It's a ghost that already left the server!")


@client.command(name = 'sailorloot',
                description = 'Shows the specific loot of the sailor.',
                context = True)
async def sailorloot(context, mentioned : str):
    memb = True
    lootqu = ''
    money = 0
    for index, line in enumerate(player_income):
        if line[0] == str(context.message.mentions[0].id):
            memb = False
            for data in player_income.range('D'+str(index +1)+":P"+str(index+1))[0]:
                lootqu += '{:10,.0f}'.format(MoneyToInt(data.value)) +'\n'
                money = MoneyToInt(player_income.cell('C'+str(index+1)).value)
            embed = discord.Embed(title = 'Loot of '+context.message.mentions[0].display_name, description="Here's the loot this sailor has collected", color= 0xff9baa)
            embed.add_field(name= 'Loot Type', value= typesofloot, inline = True)
            embed.add_field(name= 'Quantity', value= lootqu, inline = True)
            embed.set_thumbnail(url="https://files.catbox.moe/lxblyj.gif")
            embed.add_field(name= 'Total weekly profit', value= '${:10,.2f}'.format(money))
            await context.send(embed = embed)
            break  
    if memb:
        await context.send("The sailor wasn't found.")
        return
@sailorloot.error
async def sailor_loot_error(context, error):
    await context.send("You got wrong your arguments, remember to mention someone.")
 

@client.command(name = 'tiers',
                brief = "Shows the tier distribution and the users in it.",
                description = "usage: !!tiers",
                pass_context = True)
#@commands.has_any_role('Members')
async def tiers_smh(context):
    
    seahunters = []
    for line in income_calc.range('B2:B101'):
        if(line[0].value != ''):
            seahunters.append((line[0].value, MoneyToInt(line[0].neighbour((0,2)).value)))
    if(len(seahunters) == 0):
        await context.send("There are no registered sailors, please register someone first.")
        return
    else:
        seahunters.sort(key = operator.itemgetter(1), reverse = True)
    namestring = tierstring = ''
    for hunter in range(len(seahunters)):
        namestring = namestring + '{:>8} {:>16}'.format("**"+str(hunter + 1) + ".** ", seahunters[hunter][0]) +"\n"
        tierstring = tierstring + str(int(seahunters[hunter][1])) + '\n'    
    embed = discord.Embed(title = 'Weekly tiers', description="Here's a compendium of tiers for this week!", color= 0xff9baa)
    embed.add_field(name= 'Family Name', value= namestring, inline = True)
    embed.add_field(name= 'Tier', value= tierstring, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/m1uzlo.gif") 
    ##embed.add_field()
    await context.send(embed = embed)

@disenrol_smh.error
async def disenrol_smh_error(context, error):
    await context.send("You got wrong your arguments, remember to mention someone.")



@client.command(name = 'about_tier',
                brief = "Shows your current tier and what you need to hit the next tier.",
                description = "usage: !!about_tier",
                pass_context = True)
async def next_tier(context):
    family_name = tier =  ''
    remaining = income_c = 0
    for line in income_calc.range('A2:A101'):
        if(line[0].value == str(context.message.author.id)):
            family_name = line[0].neighbour('right').value
            income_c = MoneyToInt(line[0].neighbour((0,2)).value)
            tier = line[0].neighbour((0,3)).value
    if(not family_name):
        await context.send("You're not registered, please use the enrol command first.")
        return

    for line in income_calc.range('K14:K22'):
        if(line[0].value == tier):
            remaining = MoneyToInt(line[0].neighbour((1,1)).value) - income_c
            break

    embed = discord.Embed(title = 'Tier info', description="Here's more info about your loot.", color= 0xff9baa)
    embed.add_field(name= 'Family Name', value= family_name, inline = True)
    embed.add_field(name= 'Tier', value= str(tier), inline = True)
    embed.add_field(name= 'Income', value= '${:10,.2f}'.format(income_c), inline = True)
    if (remaining):
        embed.add_field(name= 'To hit next tier:', value= '${:10,.2f}'.format(remaining), inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/m1uzlo.gif") 
    await context.send(embed = embed)

#WIP gifting loot
# @client.command(name = 'gift',
#                 description = "Gives a share of your loot to another member, .gift @mention loot_type quantity\n Example: .gift @Myfriend 100m 2",
#                 context = True)
# async def gift_smh(context, who:str, loot_type:str, quantity:int):
#     if (os.path.isfile(CWD +"/"+db) == False):
#         await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
#         return

#     sender_exists, receiver_exists, approved
#     with open (db) as infile:
#         reader = csv.reader(infile.readlines())
#         for line in reader:
#             if line[0] == context.message.author.id:
#                 sender_exists = True
#                 if loot_type.upper() == 'NEIDAN':
#                     approved = (True if (int(line[2])-quantity)>= 0 else False)
#                 elif loot_type.upper() == 'PIRATE':
#                     approved = (True if (int(line[3])-quantity)>= 0 else False)
#                 elif loot_type.upper() == '100M':
#                     approved = (True if (int(line[4])-quantity)>= 0 else False)
#                 else:
#                      await client.say("There's not such a drop named \"" +loot_type +"\", please check what you're writing.")
#                      return
#             elif line[0] == context.message.mentions[0].id:
#                 receiver_exists = True
#         if (not sender_exists):
#             await client.say ("You're not registered in the database.")
#         if (not receiver_exists):
#             await client.say ("The person you're trying to send a gift to is not registered in the database.")
#         if not sender_exists or not receiver_exists: return
#         #loot movement
#         if (approved)

#     infile.close()
#     outfile.close()



@client.command(name = 'alive',
                description = "Test if the bot is working.")
async def hello_msg():
    await client.send("Yes, I'm here!")

##-----------Not command related--------##
def FloatOrZero(value):
    try:
        return float(value)
    except:
        return 0.0

def MoneyToInt(value):
    exp = re.compile('[^0-9eE.]')
    return FloatOrZero(exp.sub('', value))

##----------add function ------------##
async def adding(context, loot_type, quantity, bymention = False):
    flag_existence = goodloot = False
    whois = str(context.message.author.id)
    if bymention:
        whois = str(context.message.mentions[0].id)
    for index, line in enumerate(player_income):
        if line[0] == whois:
            flag_existence = True
            if loot_type.upper() == 'NEIDAN':
                player_income.update_value('D'+str(index + 1), str(FloatOrZero(line[3])+quantity))
                goodloot = True
            elif loot_type.upper() == 'AMETHYST':
                player_income.update_value('E'+str(index + 1), str(FloatOrZero(line[4])+quantity))
                goodloot = True
            elif loot_type.upper() == 'HEKARU':
                player_income.update_value('F'+str(index + 1), str(FloatOrZero(line[5])+quantity))
                goodloot = True
            elif loot_type.upper() == 'WHISKER':
                player_income.update_value('G'+str(index + 1), str(FloatOrZero(line[6])+quantity))
                goodloot = True
            elif loot_type.upper() == 'SKIN':
                player_income.update_value('H'+str(index + 1), str(FloatOrZero(line[7])+quantity))
                goodloot = True
            elif loot_type.upper() == 'STEEL':
                player_income.update_value('I'+str(index + 1), str(FloatOrZero(line[8])+quantity))
                goodloot = True
            elif loot_type.upper() == 'SHELL':
                player_income.update_value('J'+str(index + 1), str(FloatOrZero(line[9])+quantity))
                goodloot = True
            elif loot_type.upper() == 'FIN':
                player_income.update_value('K'+str(index + 1), str(FloatOrZero(line[10])+quantity))
                goodloot = True
            elif loot_type.upper() == 'HORN':
                player_income.update_value('L'+str(index + 1), str(FloatOrZero(line[11])+quantity))
                goodloot = True
            elif loot_type.upper() == 'TONGUE':
                player_income.update_value('M'+str(index + 1), str(FloatOrZero(line[12])+quantity))
                goodloot = True
            elif loot_type.upper() == 'JAW':
                player_income.update_value('N'+str(index + 1), str(FloatOrZero(line[13])+quantity))
                goodloot = True
            elif loot_type.upper() == 'GOBLET':
                player_income.update_value('O'+str(index + 1), str(FloatOrZero(line[14])+quantity))
                goodloot = True
            elif loot_type.upper() == 'COIN':
                player_income.update_value('P'+str(index + 1), str(FloatOrZero(line[15])+quantity))
                goodloot = True
            else:
                await context.send("There's not such a drop named \"" +loot_type +"\", please check what you're writing.")
                goodloot = False
                break
            ##player_income.update_value('Q'+str(index + 1), line[16] + " " + picture)
        if index > 100:
            break
    if (not flag_existence):
            await context.send("Uhm, it appears you're not registered yet, run the .enrol command to register.")
    elif(flag_existence and goodloot and bymention):
        await context.send(context.message.mentions[0].mention +", I have saved your data!")
        return
    elif(flag_existence and goodloot):
        await context.send(context.message.author.mention +", I have saved your data!")



@client.event
async def on_ready():
    await client.change_presence(activity = Game(name = "!!help for info"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('MiyuAssistant up and ready!')
    print('------')
client.run(TOKEN)