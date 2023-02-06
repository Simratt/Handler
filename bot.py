import discord
from discord.ext import commands

from game_engine import Player, Game
from config import *

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='`', intents=intents)
members = []
dead = []
roles = []

server = None
game = None
is_over = False
main_channel = None


@bot.event
async def on_ready():
    global server
    global members
    global main_channel
    
    server = bot.get_guild(SERVER_ID) #TODO get dynamically
    main_channel = bot.get_channel(GENERAL_ID) #TODO also get dynamically
    print(f'We have logged in as {bot.user} in Server: {server.name}')
    print(f"General Channel for {server.name} is denoted as: {main_channel.name}\n\n")

    for i in server.members: 
        members.append(Player(i.id,i.name,i.discriminator))
        


@bot.command()
async def complete(ctx):
    '''Checks if the player who is invoking the command is actually terminating the right target''' 
    global game, dead, is_over, main_channel
    if ctx.author in dead: 
        ctx.send('U died, stay dead')
    player = game.completeContract(ctx.message.author.id, ctx.message.content[-3:])
    if player[0].isEmpty(): 
        is_over = True
        await main_channel.send(f"{player[1]} has died")
        await ctx.send(f'Congratulations! You win!!') #dm to winner of the game
        await main_channel.send(f'Game Over, winnner is {player[1]}')
        dead = []

        game = None
        is_over = False
               
    else:
        if player is None:
            await ctx.send("That is not the right player")
        else:
            for m in members: 
                if player[1] == m: 
                    user = bot.get_user(m.getId())
                    await user.send(f"A dead man tells no tales... thanks for playing! Enjoy the rest of the game")
            await main_channel.send(f"{player[1]} has died, {game.active} players left")
            await ctx.send(f"Your new target is {player[0].getTarget()}")


@bot.command() 
async def test(ctx): #start command
    #584825567208144917
    # user = bot.get_user(584825567208144917)
    # await user.send('Uwu')
    # print(members)
    pass

@bot.command()
async def start(ctx): 
    '''only admins are allowed to use this command, also game.players and members are pointing at the same object'''
    global game, members

    if game is None : 
        members.__delitem__(0) #removing the first attribute which is the bot itself

        game = Game(members) 
        members = game.assignContracts()
        
        print(game._contracts())
        
        await ctx.send("Assigning Targets...")
        for m in members: 
            user = bot.get_user(m.getId())
            await user.send(f"Your Secret Token is: {m.getSecret()}\nKeep it secret")
            await user.send(f"Your Target is {str(m.getTarget())}")
        
        await ctx.send("Targets Assigned, Good luck...")
    else: 
        await ctx.send("A game is already in progress")

@bot.command()
async def endgame(ctx): 
    '''only admins are allowed to use this command'''
    global game, dead, is_over

    game, dead, is_over = None, [], False

    await ctx.send("All contracts deactivated, thank you for playing")

@bot.command()
async def add(ctx): 
    '''adds a player to the game'''

    global game, members
    user = bot.get_user(int(ctx.message.content[7:-1]))
    p = Player(user.id, user.name, user.discriminator)

    if p in members: 
        await ctx.send("Player is already in the game!") #change to binary search eventually
    else: 
        game.addPlayer(p)
        await ctx.send(f"Welcome to the game @{user.name}")

        members = game.assignContracts() #TODO this is where things break
        
        print(game._contracts())
        
        await ctx.send("Reassigning Targets...")
        for m in members: 
            user = bot.get_user(m.getId())
            await user.send(f"Your Target is {str(m.getTarget())}")
        
        await ctx.send("Targets Assigned, Good luck...")

@bot.command()
async def remove(ctx): 

    global game, members
    user = bot.get_user(int(ctx.message.content[10:-1]))
    p = Player(user.id, user.name, user.discriminator)

    if p in members: 

        game.removePlayer(p)
        await ctx.send(f"@{user.name} has been removed from the game")

        members = game.assignContracts()
        
        print(game._contracts())
        
        await ctx.send("Reassigning Targets...")
        for m in members: 
            user = bot.get_user(m.getId())
            await user.send(f"Your Target is {str(m.getTarget())}")
        
        await ctx.send("Targets Assigned, Good luck...")

    else: 
        await ctx.send("Player is already removed from the game!")

@bot.command() 
async def debug(ctx):
    '''See all running games and all contracts in the back end'''
    pass 

@bot.command()
async def shuffle(ctx):
    '''Shuffles all the contracts'''
    pass 



bot.run(BOT_TOKEN)