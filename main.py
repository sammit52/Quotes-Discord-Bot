import os
import sqlite3
import discord
import random
from discord.ext import commands

TOKEN = os.environ["TOKEN"]


intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
banned_words = ["Banned word"]


@client.command(name="randomquote")
async def random_quote(ctx):
  # Connect to the database
  conn = sqlite3.connect('quotes.db')

  # Create a cursor object
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute(
    'CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)')

  # Select all quotes from the database
  cursor.execute('SELECT quote FROM quotes')

  # Fetch all quotes
  rows = cursor.fetchall()

  # Initialises quote as a variable that says there is no quotes
  quote = "There are no quotes in the database. Use !addquote followed by your quote to add a quote."

  # Checks whether the are quotes in the database, and if so randomly assigns one to the quote varriable
  if rows:
    i = random.randint(0, len(rows) - 1)
    quote = rows[i][0]
  
  # Close the database connection
  conn.close()

  # Send the quote to the user where row[i][0] is the i value of the last element
  await ctx.channel.send(quote)

@client.command(name="addquote")
async def add_quote(ctx, *, quote = None):
  # Connect to the database
  conn = sqlite3.connect('quotes.db')

  # Create a cursor object
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute(
    'CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)')
  
  # Checks whether the user has put a quote after the message and whether the message contains a banned word or not
  if quote == None:
    # Closes the database connection
    conn.close()
    
    await ctx.channel.send("You need to add a quote after that command")
  elif quote in banned_words:
    # Closes the database connection
    conn.close()
    
    # Deletes the users quote that contains a banned word
    await ctx.message.delete()
    await ctx.channel.send("That quote has a bad word in it.")
  else:
    # This inserts the quote into the quotes table within the database. It assigns it with a value of '?' to prevent against SQL attacks (learnt about this online before endeavouring to create the bot) before defining what to replace the value with in the parameters at the end. We put a comma after quote do communicate that we are only inserting one column into this table.
    cursor.execute("INSERT INTO quotes (quote) VALUES (?)", (quote,))

    # Saves the changes you have made to the data
    conn.commit()

    # Closes the database connection
    conn.close()

    await ctx.channel.send(f"'{quote}' has been successfully added to the database.")
client.run(TOKEN)
