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
INIT_BEES = 25

help_attrs = dict(hidden=True, description='Help Command')
client = commands.Bot(command_prefix=commands.when_mentioned_or('hey bee bot please', 'hey bee bot ', '!', '?'), description='== Professor of Bee-conomics ==', help_attrs=help_attrs)


class BeeVars:
    inst = False
    free_bees = {}
    balance_low = ['..Oh I\'m so sorry..', '..Well THIS is embarrassing.', '..Ouch', '.. Ohh-- that stings.']
    balance_med = ['Don\'t spend them all in one place..', 'Saving up for a BEE-MW?', 'Well aren\'t you just a... swell.. person..']
    balance_high = ['Damn you\'re rollin in it!', 'Do you need ointment?', 'Please don\'t put them in a vault and dive in..']


BV = BeeVars()


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print('DB Connected v(' + sqlite3.version + ')')
    except Error as e:
        print(e)
    finally:
        conn.close()


def create_user(conn, users):
    sql = ''' INSERT INTO users(name,bees) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, users)
    return cur.lastrowid


def select_user_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    rows = cur.fetchall()


def select_all_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()


def update_user_by_name(conn, users):
    sql = ''' UPDATE users SET bees = ? WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def delete_user_by_name(conn, name):
    sql = 'DELETE FROM users WHERE name=?'
    cur = conn.cursor()
    cur.execute(sql, (name,))


def delete_all_users(conn):
    sql = 'DELETE FROM users'
    cur = conn.cursor()
    cur.execute(sql)


def get_bees(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    bees = cur.fetchone()
    return bees[2]


def add_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    total = cur_bees + bees
    args = (total, name)
    update_user_by_name(conn, args)


def sub_bees(conn, name, bees):
    cur_bees = get_bees(conn, name)
    if cur_bees == 0:
        return 0
    total = cur_bees - abs(bees)
    if total < 0:
        return 0
    args = (total, name)
    update_user_by_name(conn, args)
    return 1


def add_channel_bees(channel, bees):
    print('ADD BEES')
    print(BV.free_bees)
    BV.free_bees[channel] += bees
    print(BV.free_bees.get(channel, 0)) # TEST
    print(BV.free_bees)


def sub_channel_bees(channel, bees):
    print('SUB BEES')


@client.command(name='roll', description='Rolls a NdN dice.', brief=': Answers from Entropy.', aliases=['dice'], ignore_extra=True, enabled=True)
async def roll_com(dice='NdN'):
    proc = str(dice)
    try:
        rolls, limit = map(int, proc.split('d'))
    except Exception:
        await client.say('Format has to be in NdN!')
        return
    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await client.say(result)


@client.command(name='give', description='Gives a user # Bees.', brief=': Give a lucky someone some Bees.', aliases=['pass'], ignore_extra=True, enabled=True, pass_context=True)
async def give_com(ctx, user, bees):  #Check for errors on default perams,  PM confirmation.
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            bees_int = int(bees)
            reciever = user.capitalize()
            giver = ctx.message.author.name
            can_add = sub_bees(conn, giver, bees_int)
            if can_add == 1:
                print('\nGiving ' + bees + ' bees, from ' + giver + ' to ' + reciever)
                add_bees(conn, reciever, bees_int)
            else:
                print('\nNot enough bees to give...')
    else:
        print('Error! cannot create the database connection.')


@client.command(name='balance', description='Get your Bee balance.', brief=': See how many Bees you have.', aliases=['account'], ignore_extra=True, enabled=True, pass_context=True)
async def balance_com(ctx):
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
            await client.send_message(ctx.message.channel, msg)
    else:
        print('Error! cannot create the database connection.')


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
                    print('\nReleasing ' + bees + ' bees into ' + channel)
                    msg = '{0} has released {1} Bees into the channel!'.format(name, bees)
                    add_channel_bees(channel, bees_int)
                else:
                    msg = 'Not in a text channel...'
            else:
                print('\nNot enough bees to release...')
                msg = 'Not enough bees to release...'
            await client.send_message(ctx.message.channel, msg)
    else:
        print('Error! cannot create the database connection.')


@client.command(name='stats', description='You shouldn\'t be able to see this...', brief=': Display debug stats.', aliases=['debug'], ignore_extra=True, enabled=True, hidden=True, pass_context=True)
async def stats_com(ctx):
    os.system('cls')
    print('\n=== CURRENT INFO ===')
    print('\nReleased Bees:')
    print(BV.free_bees)


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
            await client.process_commands(reaction.message, True)
    else:
        print('Error! cannot create the database connection.')


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
            await client.process_commands(reaction.message, True)
    else:
        print('Error! cannot create the database connection.')


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
        print('Error! cannot create the database connection.')


@client.event
async def on_message(message):
    conn = sqlite3.connect(DBF)
    if conn is not None:
        with conn:
            #No Respond to self.
            if message.author == client.user:
                return
            #Remove altogether? Fill with Silly and not commands? Only special commands?
            if message.content.startswith('yo bee bot'):
                bees = get_bees(conn, message.author.name)
                msg = 'Hello {0.author.name}! You have {1} Bees!'.format(message, bees)
                await client.send_message(message.channel, msg)
            #Initialize database.
            if message.content.startswith('!InitMemberListOnlyDoThisOnce'):
                delete_all_users(conn)
                x = message.server.members
                for member in x:
                    if member.name != client.user.name:
                        user_data = (member.name, INIT_BEES)
                        create_user(conn, user_data)
                        print(member.name + ' added...')
                endtimes = 'Initialization complete...'
                await client.send_message(message.channel, endtimes)
            #Process commands.
            message.content = message.content.lower()
            await client.process_commands(message)
            #Tell bot off...
            if message.content.startswith('shut up'):
                msg = 'Awwww... *sadly bumbles to the corner*'
                await client.send_message(message.channel, msg)
    else:
        print('Error! cannot create the database connection.')


@client.event
async def on_ready():
    await client.change_presence(game=Game(name='the Hive', type=3))
    print('\n--------------------------')
    print(client.user.name + ' logging in...')
    print('Bot ID: ' + client.user.id)
    print('--------------------------\n')
    print('Registering Channels:')
    for channel in client.get_all_channels():
        ct = str(channel.type)
        if ct == 'text':
            ch = str(channel)
            BV.free_bees[ch] = 0
            print('     ' + ch + '...')
    print('\n=== Ready ===\n')


os.system('title BOT CONSOLE')
os.system('cls')
client.run('NOT_IN_GIT')


# Add proper action notifications like give in PM ect.


###==== Refrence ====###
# {0.author.mention} @Name
# {0.author.name} Name
# {0.author} Name+number  <-- Use for account matching
# pass_context=True + context peram = usable message refrence in function --> context.message.author.mention
# channel = reaction.message.channel
# bees_caught = BV.free_bees.get('general', 0)
