import json, discord, googletrans, asyncio, typing
from discord.ext import commands
from pathlib import Path


def get_local_path(filename):
    return Path(__file__).parents[0] / filename

# All "with open()" are to be used with UTF-8 encoding. 
with open(get_local_path('data.json'), 'r', encoding='utf-8') as f:
    data : typing.Dict = json.load(f)

with open(get_local_path('userdata.json'), 'r', encoding='utf-8') as f2:
    userData : typing.Dict = json.load(f2)

client = commands.Bot('DPF!', case_insensitive=True, help_command=None)
isprocess = False
currentuser = ""
lastranslate = ''
agreementtext = """

a) user ID Will be saved for queueing system
b) be pinged whenever deepfrying is complete
c) Message data will be stored
d) Channel ID will be stored
e) To have your deepfry be put as a status

Data of a-d will not be shared. only data from e will be publicly shared with no context, only final result.
(Example: Playing **Last Deeprfy: 'It has grown' | DPF!Help**)
__You will always be able to clear your data by using `DPF!Clear`__"""
with open(get_local_path('latest.txt'), 'r', encoding='utf-8') as getlatest:
    lastranslate = getlatest.read()

translator = googletrans.Translator()

color = discord.Color.from_rgb(54, 171, 255)
def UpdateLatest(latest):
    with open(get_local_path('latest.txt'), 'w', encoding='utf-8') as update:
        update.write(latest)
        update.close()
    
    
def UpdateUserQueue(ctx):
    with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as updateQueue:
        userData["QueueLength"] += 1
        userData[str(ctx.message.author.id)]["PositionInQueue"] = userData["QueueLength"]
        userData[str(ctx.message.author.id)]["QueueMess"] = ' '.join(ctx.message.content.split()[1:])
        userData[str(ctx.message.author.id)]["IsQueued"] = True
        userData[str(ctx.message.author.id)]["QueueChann"] = str(ctx.message.channel.id)

        json.dump(userData, updateQueue)

def UpdateQueue():
    with open(get_local_path('userdata.json'), 'r', encoding='utf-8') as getfile:
        queue = json.load(getfile)
    
    with open(get_local_path("userdata.json"), 'w', encoding='utf-8') as updatePublicQueue:
        returnvalue = ""
        for x in queue:
            if x != 'QueueLength':
                if userData[x]["PositionInQueue"]-1 == 0 and bool(queue[x]["IsQueued"]):
                        userData[x]["PositionInQueue"] -= 1
                        userData[x]["IsQueued"] = False
                        userData["QueueLength"] -= 1
                        returnvalue = userData[x]
                elif bool(queue[x]["IsQueued"]):
                    userData[x]["PositionInQueue"] -= 1
                else:
                    userData[x]["PositionInQueue"] = 0
                    
        json.dump(userData, updatePublicQueue)
        return returnvalue

async def DeepfryMain(channelID, message, authorID):
    global isprocess
    global translator
    global lastranslate
    global currentuser
    isprocess = True
    currentuser = str(authorID)
    ctx = client.get_channel(channelID)

    current = message
    last = translator.translate(current, dest='en').text
    
    failed = False
    for x in googletrans.LANGUAGES:
        current = translator.translate(last, dest=x)
        last = current.text
        if last == '':
            await ctx.send(f"<@{authorID}> your translation failed! Please try another one / later :(")
            failed = True
            break
        await asyncio.sleep(3)
    if not failed:
        last = translator.translate(current.text, dest='en').text
        await ctx.send(f'<@{authorID}>! Your deepfrying has finished.')
        await ctx.send(f'{message} -> {last}')
        UpdateLatest(last)
        await asyncio.sleep(3)
    authorID = str(authorID)
    userData[authorID]["IsQueued"] = False
    userData[authorID]["QueueChann"] = ""
    userData[authorID]["QueueMess"] = ""
    isprocess = False
    with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as updatequeue2:
        json.dump(userData, updatequeue2)
    lastranslate = last
    return

@client.event
async def on_ready():
    global userData
    global lastranslate
    with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as clearqueue:
        userData["QueueLength"] = 0
        for x in userData:
            if x == "QueueLength":
                continue
            userData[x]["PositionInQueue"] = 0
            userData[x]["IsQueued"] = False
            userData[x]["QueueMess"] = ""
            userData[x]["QueueChann"] = ""
        json.dump(userData, clearqueue)
    print(f"{data['Name']} is online and usable")
    while True:
        for _ in range(6):
            await client.change_presence(activity=discord.Game(name="Queue: {0} | DPF!Help".format(userData["QueueLength"])))
            await asyncio.sleep(10)
        for _ in range(6):
            await client.change_presence(activity=discord.Game(name="{0} Registered users | DPF!Help".format(len(userData)-1)))
            await asyncio.sleep(10)
        for _ in range(6):
            await client.change_presence(activity=discord.Game(name="Last Deepfry: '{0}' | DPF!Help".format(lastranslate)))
            await asyncio.sleep(10)

@client.command()
async def Deepfry(ctx):
    global agreementtext
    global currentuser
    if userData.get(str(ctx.message.author.id)) != None:
        if len(str(ctx.message.content).split()) == 1:
            await ctx.send("Please include sentence to deepfry.")
            return
        if len(ctx.message.mentions) != 0:
            await ctx.send("Please do not mention anyone in your message.")
            return
        if not isprocess:
            await ctx.send("I will deepfry your message right now. Give me about 5min.")
            currentuser = str(ctx.message.author.id)
            await DeepfryMain(ctx.message.channel.id, " ".join(ctx.message.content.split()[1:]), ctx.message.author.id)

            while True:
                queued = UpdateQueue()
            
                if queued != "":
                    start = client.get_channel(int(queued["QueueChann"]))
                    await start.send(f'<@{queued["UID"]}>! I am starting your long awaited deepfry of `{queued["QueueMess"]}`!')
                    await DeepfryMain(start.id, userData[queued["UID"]]["QueueMess"], queued["UID"])
                else:
                    break
                
        else:
            if currentuser == str(ctx.message.author.id):
                await ctx.send("Your message is alreayd being translated.")
            elif bool(userData[str(ctx.message.author.id)]["IsQueued"]):
                await ctx.send(f"Your Queued message has been changed from {userData[str(ctx.message.author.id)]['QueueMess']} -> {' '.join(ctx.message.content.split()[1:])}")
                userData[str(ctx.message.author.id)]["QueueMess"] = ' '.join(ctx.message.content.split()[1:])
                with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as updateQueuedMess:
                    json.dump(userData, updateQueuedMess)
            else:
                UpdateUserQueue(ctx)
                
                await ctx.send("You have successfully been queued into position {0}! Type `DPF!Queue` for your queue info.".format(userData[str(ctx.message.author.id)]["PositionInQueue"]))
    else:
        await ctx.send("You have not accepted to have your data stored. When you accept, you accept that...")
        message = await ctx.send(agreementtext)
        await asyncio.sleep(20)
        await message.edit(content=message.content + "\n use `DPF!Accept` to agree")
    
@client.command()
async def Accept(ctx):
    if userData.get(str(ctx.message.author.id)) == None:
        
        userData[str(ctx.message.author.id)] = {
        "PositionInQueue":0,
        "IsQueued":False,
        "QueueMess": "",
        "QueueChann":"",
        "UID":str(ctx.message.author.id)
        }
        
        with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as f3:
            json.dump(userData, f3)
            
        await ctx.send("Registered!")

    else:
        await ctx.send("You have already registered.")


@client.command()
async def Queue(ctx):
    if userData.get(str(ctx.message.author.id)) == None:
        await ctx.send("You have not yet registered and aren't queued.")
    else:
        if bool(userData[str(ctx.message.author.id)]["IsQueued"]):
            userqueuepos = userData[str(ctx.message.author.id)]["PositionInQueue"]
            await ctx.send(embed=discord.Embed(title="Queue", colour=color)
            .add_field(name="Your Position in queue:", value=str(userqueuepos), inline=False)
            .add_field(name="Total time expectancy:", value=str((int(userqueuepos)*5) + 5) + "min", inline=False)
            .add_field(name="Total queue length:", value=str(userData["QueueLength"]), inline=False)
            .add_field(name="Your Queued Message:", value=userData[str(ctx.message.author.id)]["QueueMess"], inline=False)
            .set_footer(text='English Deepfrier', icon_url="https://media.discordapp.net/attachments/741078845750247445/741410062861467718/Deepfry.png?width=677&height=677"))
        else:
            if currentuser == str(ctx.message.author.id):
                await ctx.send("Your message is curently being deepfried.")
            else:
                await ctx.send("You aren't queued.")
@client.command()
async def Pos(ctx):
    await Queue(ctx)
@client.command()
async def Clear(ctx):
    if userData.get(str(ctx.message.author.id)) == None:
        await ctx.send("You have no data.")
    else:
        if bool(userData[str(ctx.message.author.id)]["IsQueued"]):
            userData["QueueLength"] -= 1
        
        userData.pop(str(ctx.message.author.id))
        with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as cleardata:
            json.dump(userData, cleardata)
        await ctx.send("User data successfuly cleared.")
@client.command()
async def Cancel(ctx):
    if userData.get(str(ctx.message.author.id)) != None:
        if bool(userData[str(ctx.message.author.id)]["IsQueued"]):
            userData[str(ctx.message.author.id)]["IsQueued"] = False
            userData[str(ctx.message.author.id)]["QueueMess"] = ""
            userData[str(ctx.message.author.id)]["QueueChann"] = ""
            userData["QueueLength"] -= 1
            
            for z in userData:
                if z != "QueueLength":
                    if userData[z]["PositionInQueue"] > userData[str(ctx.message.author.id)]["PositionInQueue"]:
                        if bool(userData[z]["IsQueued"]):
                            userData[z]["PositionInQueue"] -= 1
            
            userData[str(ctx.message.author.id)]["PositionInQueue"] = 0
            with open(get_local_path('userdata.json'), 'w', encoding='utf-8') as canceljob:
                json.dump(userData, canceljob)

            await ctx.send("Your queued message has been canceled.")
        else:
            await ctx.send("There is nothing to cancel.")
    else:
        await ctx.send("You aren't registered.")
@client.command()
async def Agreement(ctx):
    await ctx.send(agreementtext)

@client.command()
async def Help(ctx):
    global color
    await ctx.send(embed=discord.Embed(title="Help", colour=color)
    .add_field(name='DPF!Deepfry [word/sentence]', value="Will deepfry the English put in as the\n `word/sentence`", inline=False)
    .add_field(name="DPF!Accept", value="Accept the agreement", inline=False)
    .add_field(name="DPF!Agreement", value="Shows the agreement", inline=False)
    .add_field(name="DPF!Clear", value="Clears user data", inline=False)
    .add_field(name="DPF!Queue / DPF!Pos", value="Gives you your queue info\n (will only send if user is queued.)", inline=False)
    .add_field(name="DPF!Help", value="Gives you this list", inline=False)
    .add_field(name="DPF!Cancel", value="Cancels your item in queue. (if you\n wish to change your sentence, just use\n the DPF!Deepfry command.)\n")
    .add_field(name="Exetra Notes:", value="1. You will get better results with sentences\nrather than words\n2. If you are queued, you can change your\nrequest using the `DPF!Deepfry` command", inline=False)
    .set_footer(text='English Deepfrier', icon_url="https://media.discordapp.net/attachments/741078845750247445/741410062861467718/Deepfry.png?width=677&height=677"))

print("Starting...")
client.run(data["Token"])