import os
import sqlite3
import discord
import random
from discord.ext import commands

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

prefix = ["!", "@", "#", "$", "%", "&", "*", "?"]

# The use of the first 2 functions are to constantly update the essential databases of commandprefix and bannedwords.

# This function updates the command prefix everytime it is called. In this case it is called constantly with theclient.command_prefix = command_prefix() line
def command_prefix():
  # Connect to banned words data base
  conn = sqlite3.connect("commandprefix.db")

  # Make a cursor object so we can edit data
  cursor = conn.cursor()
  
  # Create a table to store the banned words if one does not exist already
  cursor.execute("CREATE TABLE IF NOT EXISTS command_prefix (id INTEGER PRIMARY KEY, prefix TEXT)")

  # Select all quotes from the database
  cursor.execute("SELECT prefix FROM command_prefix")
  
  rows = cursor.fetchall()

  # Checks whether there is anything in the dataabase
  if rows:
    # Reformat SQL data
    rows[0] = str(rows[0]).replace("('","")
    rows[0] = str(rows[0]).replace("',)","")
    command_prefix = rows[0]
  # Basically if there is not already something in the database make the command_prefix default
  else:
    command_prefix = "!"
  
  return command_prefix

client.command_prefix = command_prefix()


# This function updates the banned words everytime it is called. In this case it is called constantly with the banned_words = banned_words() line
def banned_words():
  # Connect to banned words data base
  conn = sqlite3.connect("bannedwords.db")

  # Make a cursor object so we can edit data
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute('CREATE TABLE IF NOT EXISTS banned_words (id INTEGER PRIMARY KEY, word TEXT)')

  # Select all quotes from the database
  cursor.execute("SELECT word FROM banned_words")

  # Get all the data from the file
  rows = cursor.fetchall()
  
  # Make banned_words an empty list
  banned_words = []

  # Reformat rows because SQL makes the output weird
  if rows:
    i = 0

    while i < len(rows):
      # Reformat SQL data
      rows[i] = str(rows[i]).replace("('","")
      rows[i] = str(rows[i]).replace("',)","")
      banned_words.append(rows[i])
      print(banned_words)
      i += 1
  else:
    return ""

  # Close connection
  conn.close()
  return banned_words

banned_words = banned_words()

@client.command(name="randomquote")
async def random_quote(ctx):
  # Connect to the database
  conn = sqlite3.connect("quotes.db")

  # Create a cursor object
  cursor = conn.cursor()

  # Create a table to store the quotes if one does not exist already
  cursor.execute('CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)')

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
  bad_word_found = False
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
  else:
    for word in banned_words:
      if quote.lower() in word:
        bad_word_found = True
    
    if bad_word_found == True:
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

      # Get the last row's id
      cursor.execute("SELECT last_insert_rowid()")

      # Get the information stored in the cursor object
      row = cursor.fetchone()

      # Since there's only one bit of data get the value first row of the cursor object (being the id associated with the quote)
      last_id = row[0]
      
      # Closes the database connection
      conn.close()
      await ctx.channel.send(f"'{quote}' has been successfully added to the database and its number is {last_id}")


@client.command(name="quote")
async def quote(ctx, num=None):
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
      # Checks if the quote number exists
      if len(rows) < (num - 1):
        conn.close()
        await ctx.channel.send("That is not a current quote number.")
      else:
        # Send the quote
        conn.close()
        await ctx.channel.send(rows[num - 1][0])


@client.command(name="addbannedwords")
async def add_banned_word(ctx, *, new_banned_words=None):
  # Checks whether the message sender has administrative permissions
  if ctx.message.author.guild_permissions.administrator:
    # Checks whether the user has inputed any new banned words
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


@client.command(name="info")
async def info(ctx):
  if ctx.message.author.guild_permissions.administrator:
    await ctx.channel.send(f"{client.command_prefix}randomquote - This is a command where the bot says a random quote\n{client.command_prefix}addquote (quote) - This is a command where the user can add their own quotes \n{client.command_prefix}quote (num) - This is a command where you can get a specific quote from the database\n{client.command_prefix}allquotes - This command gets all of the quotes and their number\n{client.command_prefix}addbannedwords (banned_words) - This is a command where a moderator can add a banned word or list of banned words separated by commas where a user cannot add a quote if it has it in it.\n{client.command_prefix}changeprefix - This command allows the moderator to change the command prefix")  # INFORMATION ABOUT ALL COMMANDS INCLUDING MODERATOR COMMANDS
  else:
    await ctx.channel.send(f"{client.command_prefix}randomquote - This is a command where the bot says a random quote\n{client.command_prefix}addquote (quote) - This is a command where the user can add their own quotes \n{client.command_prefix}quote (num) - This is a command where you can get a specific quote from the database\n{client.command_prefix}allquotes - This command gets all of the quotes and their number")  # INFORMATION ABOUT ALL COMANNDS EXCEPT MODERATOR COMMANDS


@client.command(name="changeprefix")
async def command_prefix(ctx, new_command_prefix=None):
  # Checks whether the message sender has administartor permissions or not
  if ctx.message.author.guild_permissions.administrator:

    # Checks whether the new prefix is in a list of acceptable prefixes
    if new_command_prefix in prefix:
      # Connects to database
      conn = sqlite3.connect("commandprefix.db")

      # Create a cursor object
      cursor = conn.cursor()

      # Insert the word into the database
      cursor.execute('UPDATE command_prefix SET id=?, prefix=? WHERE id=1', ('1', new_command_prefix))

      # Commit the changes to the file
      conn.commit()

      # Close database connection
      conn.close()

      client.command_prefix = new_command_prefix

      await ctx.channel.send(f"'{new_command_prefix}' is your new command prefix.")

    # Checks whether the user has inputed a new prefix
    elif new_command_prefix == None:
      await ctx.channel.send("You need to add a new prefix after that command")
    else:
      await ctx.channel.send("That is not a valid prefix")
  else:
    await ctx.channel.send("You do not have permissions to use that command")


@client.command(name="allquotes")
async def all_quotes(ctx):
  quotes = ""
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
  
  # Checks whether there are i rows in the database, in other words, len(rows) is bigger than i because of the nature of i being the elements of the list which starts at 0
  if rows:
    i = 0
    print(rows)
    print(rows[0])

    while i < len(rows):
      # Reformat SQL data
      rows[i] = str(rows[i]).replace("('","")
      rows[i] = str(rows[i]).replace("',)","")
      
      # Assign a variable to the output
      quote = f"{i+1}. {rows[i]}\n"

      # Make the code go onto the next row in the database
      i +=1
      
      # Add to variable with collection of quotes
      quotes += quote

    await ctx.channel.send(quotes)
  
  else:
    await ctx.channel.send("There are no quotes in the database")


client.run(TOKEN)
