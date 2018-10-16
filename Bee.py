import discord
import sqlite3
import asyncio
import random
import os
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
from sqlite3 import Error

DBF = "C:\\Users\\Thorn\\Desktop\\BOTS\\Beeees\\DB\\Money.db"
INIT_BEES = 25
client = commands.Bot(command_prefix=commands.when_mentioned_or('hey bee bot ', '!', '?'), description='The Willy Wonka of Bees!')


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print('DB Connected v(' + sqlite3.version + ')')
    except Error as e:
        print(e)
    finally:
        conn.close()


def create_user(conn, users):
    sql = ''' INSERT INTO users(name,bees)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, users)
    return cur.lastrowid


def select_user_by_id(conn, id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (id,))
    rows = cur.fetchall()


def select_user_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    rows = cur.fetchall()


def select_all_users(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()


def update_user_by_id(conn, users):
    sql = ''' UPDATE users
              SET bees = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def update_user_by_name(conn, users):
    sql = ''' UPDATE users
              SET bees = ? 
              WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, users)


def delete_user_by_id(conn, id):
    sql = 'DELETE FROM users WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))


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
    total = cur_bees - bees
    if total <= 0:
        total = 0
    args = (total, name)
    update_user_by_name(conn, args)


#add on react event
#add balance command
#add give command
#add release command
#change command start


@client.command(name='roll', description='Rolls a NdN dice.', brief='Answers from Entropy.', aliases=['dice'], pass_context=True)
async def roll_dice(context, dice='none'):
    proc = str(dice)
    try:
        rolls, limit = map(int, proc.split('d'))
    except Exception:
        await client.say('Format has to be in NdN!')
        return
    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await client.say(result)


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
        print("Error! cannot create the database connection.")


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
                endtimes = 'RAGNAROK!...  It is done...'
                await client.send_message(message.channel, endtimes)
            #Process commands.
            message.content = message.content.lower()
            await client.process_commands(message)
            #Tell bot off...
            if message.content.startswith('shut up'):
                msg = 'Awwww... *sadly bumbles to the corner*'
                await client.send_message(message.channel, msg)
    else:
        print("Error! cannot create the database connection.")


@client.event
async def on_ready():
    await client.change_presence(game=Game(name="the Hive", type=3))
    print('\n--------------------------')
    print(client.user.name + ' logging in...')
    print('Bot ID: ' + client.user.id)
    print('--------------------------')


os.system('title BOT CONSOLE')
os.system('cls')
client.run('NOT_IN_GIT')


###==== Refrence ====###
# {0.author.mention} @Name
# {0.author.name} Name
# {0.author} Name+number  <-- Use for account matching
# pass_context=True + context peram = usable message refrence in function --> context.message.author.mention
