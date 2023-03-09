import os
import sqlite3
import discord
import random
from discord.ext import commands

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# This function updates the banned words everytime it is called. In this case it is called as the bot is first started and when it is called so it is constantly keeping up with the changes
def banned_words():
  # Connect to banned words data base
  conn = sqlite3.connect("bannedwords.db")

  # Make a cursor object so we can edit data
  cursor = conn.cursor()

  # Select all quotes from the database
  cursor.execute("SELECT word FROM banned_words")

  # Get all the data from the file
  rows = cursor.fetchall()

  # Print out the data
  for row in rows:
    print(row)

  # Make a list of banned words from file
  banned_words = rows
  print(banned_words)
  
  # Close connection
  conn.close()
  return banned_words


@client.command(name="randomquote")
async def random_quote(ctx):
  # Connect to the database
  conn = sqlite3.connect("quotes.db")

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

  # Send the quote to the user where row[i][0] is the i value of the first and only element
  await ctx.channel.send(quote)


@client.command(name="addquote")
async def add_quote(ctx, *, quote=None):
  # Connect to the database
  conn = sqlite3.connect("quotes.db")

  # Create a cursor object
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)")

  # Checks whether the user has put a quote after the message and whether the message contains a banned word or not
  if quote == None:
    # Closes the database connection
    conn.close()

    await ctx.channel.send("You need to add a quote after that command")
  elif quote.lower() in str(banned_words()).lower():
    # Closes the database connection
    conn.close()

    # Deletes the users quote that contains a banned word
    await ctx.message.delete()
    await ctx.channel.send("That quote has a bad word in it.")
  else:
    # This inserts the quote into the quotes table within the database. It assigns it with a value of '?' to prevent against SQL attacks (learnt about this online before endeavouring to create the bot) before defining what to replace the value with in the parameters at the end. We put a comma after quote do communicate that we are only inserting one column into this table.
    cursor.execute("INSERT INTO quotes (quote) VALUES (?)", (quote, ))

    # Saves the changes you have made to the data
    conn.commit()

    # Closes the database connection
    conn.close()

    await ctx.channel.send(
      f"'{quote}'has been successfully added to the database.")


@client.command(name="quote")
async def quote(ctx, num = None):
  print(num)
  # Connect to the database
  conn = sqlite3.connect("quotes.db")

  # Create a cursor object
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)")
  
  # Select all quotes from the database
  cursor.execute("SELECT quote FROM quotes")

  # Get all the data from the file
  rows = cursor.fetchall()

  if num == None:
    conn.close()
    await ctx.channel.send("You need to add a quote number after that")

  else:
    # Check whether num is an integer
    try:
      num = int(num)
    # If it isn't an integer then tell user
    except:
      conn.close()
      await ctx.channel.send(f"{num} is not a valid quote number")

    else:
      if len(rows) < (num - 1):
        conn.close()
        await ctx.channel.send("That number is out of range")
      else:
        # Send the quote
        conn.close()
        await ctx.channel.send(rows[num-1][0])
    
    
@client.command(name="addbannedwords")
async def add_banned_word(ctx, *, new_banned_words=None):
  if ctx.message.author.guild_permissions.administrator:
    if new_banned_words == None:
      await ctx.channel.send("You need to add a list of new banned words separated by commas after that command.")
    else:
      # Connects to database
      conn = sqlite3.connect("bannedwords.db")

      # Create a cursor object
      cursor = conn.cursor()

      # Create a table to store the banned words if one does not exist already
      cursor.execute("CREATE TABLE IF NOT EXISTS banned_words (id INTEGER PRIMARY KEY, word TEXT)")

      # Reformat user input
      new_banned_words = new_banned_words.replace(" ,", ",").lower()
      new_banned_words = new_banned_words.split(",")
      
      # Split the list into individual strings and insert them into database
      for word in new_banned_words:
        # Test for whether the code works
        print(word)

        # Insert the word into the database
        cursor.execute("INSERT INTO banned_words (word) VALUES (?)", (word, ))

        # Commit the changes to the file
        conn.commit()

        # Close connection
        conn.close()
  else:
    await ctx.channel.send("You do not have permission to use this command")


client.run(TOKEN)

if __name__ == '__main__':
  banned_words()
