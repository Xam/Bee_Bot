import discord
import sqlite3
import asyncio
import random
import os
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
from sqlite3 import Error

DBF = 'C:\\Users\\Thorn\\Desktop\\BOTS\\Beeees\\DB\\Money.db'
DBE = 'Error! cannot create the database connection.'
INIT_BEES = 25

help_attrs = dict(hidden=True, description='Help Command')
client = commands.Bot(command_prefix=commands.when_mentioned_or('hey bee bot please ', 'hey bee bot whats my ', 'hey bee bot show ', 'hey bee bot ', '!', '?'), description='== Professor of Bee-conomics ==', help_attrs=help_attrs)


class BeeVars:
    inst = False
    wilt = False
    balance_low = ['..Oh I\'m so sorry..', '..Well THIS is embarrassing.', '..Ouch', '.. Ohh-- that stings.']
    balance_med = ['Don\'t spend them all in one place..', 'Saving up for a BEE-MW?', 'Well aren\'t you just a... swell.. person..']
    balance_high = ['Damn you\'re rollin in it!', 'Do you need ointment?', 'Please don\'t put them in a vault and dive in..']

BV = BeeVars()


#### ---==== User DB ====--- ####

def create_user(conn, users):
    sql = ''' INSERT INTO Users(name,bees) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, users)
    return cur.lastrowid


def select_user_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE name=?", (name,))
    rows = cur.fetchall()


def update_user_by_name(conn, users):
    sql = ''' UPDATE Users SET bees = ? WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def delete_all_users(conn):
    sql = 'DELETE FROM Users'
    cur = conn.cursor()
    cur.execute(sql)


def user_exists(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE name=?", (name,))
    row = cur.fetchone()
    if str(row) == 'None':
        return 0
    return 1


def get_bees(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE name=?", (name,))
    bees = cur.fetchone()
    if str(bees) == 'None':
        return -1
    return bees[2]


def add_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    if cur_bees == -1:
        return -1
    total = cur_bees + bees
    args = (total, name)
    update_user_by_name(conn, args)


def sub_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    if cur_bees == -1:
        return -1
    if cur_bees == 0:
        return 0
    total = cur_bees - abs(bees)
    if total < 0:
        return 0
    args = (total, name)
    update_user_by_name(conn, args)
    return 1


#### ---==== Channel_Vars DB ====--- ####

def create_channel(conn, channel):
    sql = ''' INSERT INTO Channel_Vars(channel,bees) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, channel)
    return cur.lastrowid


def select_channel_by_name(conn, channel):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Channel_Vars WHERE channel=?", (channel,))
    rows = cur.fetchall()


def update_channel_by_name(conn, channel):
    sql = ''' UPDATE Channel_Vars SET bees = ? WHERE channel = ?'''
    cur = conn.cursor()
    cur.execute(sql, channel)


def delete_channel_by_name(conn, channel):
    sql = 'DELETE FROM Channel_Vars WHERE channel=?'
    cur = conn.cursor()
    cur.execute(sql, (channel,))


def delete_all_channels(conn):
    sql = 'DELETE FROM Channel_Vars'
    cur = conn.cursor()
    cur.execute(sql)


def get_channel_bees(conn, channel):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Channel_Vars WHERE channel=?", (channel,))
    bees = cur.fetchone()
    return bees[2]


def add_channel_bees(conn, channel, bees):
    cur_bees = get_channel_bees(conn, channel)
    total = cur_bees + bees
    args = (total, channel)
    update_channel_by_name(conn, args)


def sub_channel_bees(conn, channel, bees):
    cur_bees = get_channel_bees(conn, channel)
    if cur_bees == 0:
        return 0
    total = cur_bees - abs(bees)
    if total < 0:
        return 0
    args = (total, channel)
    update_channel_by_name(conn, args)
    return 1


@client.command(name='roll', description='Rolls a NdN dice.', brief=': Answers from Entropy.', aliases=['dice'], ignore_extra=True, enabled=True)
async def roll_com(dice='NdN'):  # limit each number
    proc = str(dice)
    try:
        rolls, limit = map(int, proc.split('d'))
    except Exception:
        await client.say('Format has to be in NdN!')
        return
    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await client.say(result)


@roll_com.error
async def roll_com_error(ctx, error):
    print('\nI dont understand.. [error in roll]')


@client.command(name='give', description='Gives a user # Bees. No Nicknames please.', brief=': Give a lucky someone some Bees.', aliases=['pass'], ignore_extra=True, enabled=True, pass_context=True)
async def give_com(ctx, user, bees):  #PM confirmation.
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            bees_int = int(bees)
            reciever = user.capitalize()
            server = ctx.message.server
            reciever_member = server.get_member_named(reciever)
            giver = ctx.message.author.name
            exists = user_exists(conn, reciever)
            if exists == 1:
                can_add = sub_bees(conn, giver, bees_int)
                if can_add == 1:
                    add_bees(conn, reciever, bees_int)
                    print('\nGiving ' + bees + ' bees, from ' + giver + ' to ' + reciever)
                    if bees_int > 1:
                        snd = 'You have given {0} {1} bees!'.format(reciever, bees)
                        rcv = '{0} has given you {1} bees!'.format(giver, bees)
                    else:
                        snd = 'You have given {0} a bee!'.format(reciever)
                        rcv = '{0} has given you a bee!'.format(giver)
                    await client.send_message(ctx.message.author, snd)
                    await client.send_message(reciever_member, rcv)
                else:
                    print('\nNot enough bees to give...')
            else:
                msg = 'Uhh.. Who is {0}?  I don\'t understand nicknames.'.format(reciever)
                await client.send_message(ctx.message.channel, msg)
    else:
        print(DBE)


@give_com.error
async def give_com_error(ctx, error):
    print('\nI dont understand.. [error in give]') #unpack context and error


async def balance_main(ctx):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            name = ctx.message.author.name
            bees = get_bees(conn, name)
            random.seed()
            if bees <= 5:
                extra = random.choice(BV.balance_low)
            elif bees <= 50:
                extra = random.choice(BV.balance_med)
            else:
                extra = random.choice(BV.balance_high)
            if bees == 1:
                msg = 'Hello {0}! You have {1} Bee!  {2}'.format(name, bees, extra)
            else:
                msg = 'Hello {0}! You have {1} Bees!  {2}'.format(name, bees, extra)
            if bees == -1:
                msg = 'Uhh.. Who is {0}?  I think something went wrong.'.format(name)
            await client.send_message(ctx.message.channel, msg)
    else:
        print(DBE)


@client.command(name='balance', description='Get your Bee balance.', brief=': See how many Bees you have.', aliases=['account'], ignore_extra=True, enabled=True, pass_context=True)
async def balance_com(ctx):
    await balance_main(ctx)


@client.command(name='balance?', description='Get your Bee balance.', brief=': See how many Bees you have.', aliases=['account?'], ignore_extra=True, enabled=True, hidden=True, pass_context=True)
async def balance2_com(ctx):
    await balance_main(ctx)


@client.command(name='release', description='Free # Bees into the channel.', brief=': Free some Bees!.', aliases=['free'], ignore_extra=True, enabled=True, pass_context=True)
async def release_com(ctx, bees):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            bees_int = int(bees)
            channel = str(ctx.message.channel)
            name = ctx.message.author.name
            can_add = sub_bees(conn, name, bees_int)
            if can_add == 1:
                ct = str(ctx.message.channel.type)
                if ct == 'text':
                    msg = '{0} has released {1} Bees into the channel!'.format(name, bees)
                    add_channel_bees(conn, channel, bees_int)
                    print('\nReleasing ' + bees + ' bees into ' + channel)
                else:
                    msg = 'Oops you are not in a public text channel...'
            else:
                print('\nNot enough bees to release...')
                msg = 'Not enough bees to release...'
            if bees_int >=30:
                await client.send_file(ctx.message.channel, 'MEDIA\\Oprah.gif')
                msg += ' O.o Oh god they\'re everywhere!'
            await client.send_message(ctx.message.channel, msg)
    else:
        print(DBE)


@client.command(name='stats', description='You shouldn\'t be able to see this...', brief=': Display debug stats.', aliases=['debug'], ignore_extra=True, enabled=True, hidden=True, pass_context=True)
async def stats_com(ctx):
    os.system('cls')
    print('\n=== CURRENT INFO ===')
    print('\nReleased Bees:')
    # Fill info



@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user:
        BV.inst = True
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        return
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            if reaction.emoji == '\U0001F41D': #BEE
                can_add = sub_bees(conn, user.name, 1)
                if can_add == 1:
                    print('\nSubing 1 bee from ' + user.name)
                    add_bees(conn, reaction.message.author.name, 1)
                    print('Adding 1 bee to ' + reaction.message.author.name)
                else:
                    print('\nNo bees to add.. removing reaction.')
                    BV.inst = True
                    await client.remove_reaction(reaction.message, reaction.emoji, user)

            if reaction.emoji == '\U0001F33B': #SUNFLOWER
                ct = str(reaction.message.channel.type)
                if ct == 'text':
                    channel = str(reaction.message.channel)
                    channel_bees = get_channel_bees(conn, channel)
                    if channel_bees > 0:
                        if channel_bees <= 3:
                            rand = channel_bees
                        else:
                            rand = random.randint(0, channel_bees)
                        sub_channel_bees(conn, channel, rand)
                        print('\nSubing ' + str(rand) + ' bees from ' + channel)
                        add_bees(conn, reaction.message.author.name, rand)
                        print('Adding them to ' + reaction.message.author.name)
                        if rand > 1:
                            msg = '{0} bees have been attracted to you via a {1} in {2}!'.format(rand, reaction.emoji, channel)
                        else:
                            msg = 'A bee has been attracted to you via a {0} in {1}!'.format(reaction.emoji, channel)
                        await client.send_message(reaction.message.author, msg)
                    else:
                        print('\nNo bees in channel to add..')
                        BV.wilt = True
                        await client.remove_reaction(reaction.message, reaction.emoji, user)

            await client.process_commands(reaction.message, True)
    else:
        print(DBE)


@client.event
async def on_reaction_remove(reaction, user):
    if BV.inst == True:
        BV.inst = False
        return
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            if reaction.emoji == '\U0001F41D': #BEE
                can_add = sub_bees(conn, reaction.message.author.name, 1)
                if can_add == 1:
                    print('\nSubing 1 bee from ' + reaction.message.author.name)
                    add_bees(conn, user.name, 1)
                    print('Adding 1 bee to ' + user.name)
                else:
                    await client.add_reaction(reaction.message, '\U0001F480') #SKULL
                    print('\nNo bees to add.. It turned into a ZOM-Bee!')

            if reaction.emoji == '\U0001F33B': #SUNFLOWER
                if BV.wilt == True:
                    BV.wilt = False
                    await client.add_reaction(reaction.message, '\U0001F940') #WILTEDFLOWER
                    print('...So the flower wilted')

            await client.process_commands(reaction.message, True)
    else:
        print(DBE)


@client.event
async def on_member_join(member):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            user_data = (member.name, INIT_BEES)
            create_user(conn, user_data)
            server = member.server
            num = str(INIT_BEES)
            msg = 'Welcome {0.name} to {1.name}! Take your {2} bees.'.format(member, server, num)
            for channel in member.server.channels:
                if channel.name == 'general':
                    await client.send_message(channel, msg)
    else:
        print(DBE)


@client.event
async def on_channel_create(channel):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            ct = str(channel.type)
            if ct == 'text':
                ch = str(channel)
                channel_data = (ch, 0)
                create_channel(conn, channel_data)
                print(ch + ' added...')
    else:
        print(DBE)


@client.event
async def on_channel_delete(channel):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            ct = str(channel.type)
            if ct == 'text':
                ch = str(channel)
                delete_channel_by_name(conn, ch)
                print(ch + ' removed...')
    else:
        print(DBE)


@client.event
async def on_message(message):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            #No Respond to self.
            if message.author == client.user:
                return

            #Initialize databases.
            if message.content.startswith('~InitMemberList'):
                if str(message.author) == 'Thorn#6213':
                    delete_all_users(conn)
                    print('\nFormatting User DB:')
                    x = message.server.members
                    for member in x:
                        if member.name != client.user.name:
                            user_data = (member.name, INIT_BEES)
                            create_user(conn, user_data)
                            print(member.name + ' added...')
                    endtimes = 'Initialization complete...'
                    await client.send_message(message.channel, endtimes)
                else:
                    msg = 'You aren\'t the boss of me!'
                    await client.send_message(message.channel, msg)

            if message.content.startswith('~InitChannelList'):
                if str(message.author) == 'Thorn#6213':
                    delete_all_channels(conn)
                    print('\nFormatting Channel_Vars DB:')
                    for channel in client.get_all_channels():
                        ct = str(channel.type)
                        if ct == 'text':
                            ch = str(channel)
                            channel_data = (ch, 0)
                            create_channel(conn, channel_data)
                            print(ch + ' added...')
                    endtimes = 'Initialization complete...'
                    await client.send_message(message.channel, endtimes)
                else:
                    msg = 'You aren\'t the boss of me!'
                    await client.send_message(message.channel, msg)

            #Process commands.
            message.content = message.content.lower()
            await client.process_commands(message)

            #Tell bot off...
            if message.content.startswith('shut up bee'):
                msg = 'Awwww... *sadly bumbles to the corner*'
                await client.send_file(message.channel, 'MEDIA\\Sad.gif')
                await client.send_message(message.channel, msg)
    else:
        print(DBE)


@client.event
async def on_ready():
    await client.change_presence(game=Game(name='the Hive', type=3))
    print('\n--------------------------')
    print(client.user.name + ' logging in...')
    print('Bot ID: ' + client.user.id)
    print('--------------------------\n')
    print('=== Ready ===\n')


os.system('title BOT CONSOLE')
os.system('cls')
client.run('NOT_IN_GIT')


###==== Refrence ====###
# {0.author.mention} @Name
# {0.author.name} Name
# {0.author} Name+number  <-- Use for account matching
# pass_context=True + context peram = usable message refrence in function --> context.message.author.mention
# channel = reaction.message.channel
# bees_caught = BV.free_bees.get('general', 0)
