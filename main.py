import sqlite3
import discord
import random
from discord.ext import commands

TOKEN = "MTA4MDk2MDY2MTY2NTg3NDA2MA.GtTPoT.IWvile2TFdYZKkL6r4ZMjvBEPKTtz7E1XgKM-A"

# Connect to the database
conn = sqlite3.connect('quotes.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table to store the quotes
cursor.execute('CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT)')

# Prompt the user to enter a quote
quote = input('Enter a quote: ')

# Insert the quote into the database
cursor.execute('INSERT INTO quotes (quote) VALUES (?)', (quote,))

# Commit changes
conn.commit()

# Select all quotes from the database
cursor.execute('SELECT quote FROM quotes')

# Fetch all quotes
rows = cursor.fetchall()

# Print all quotes
print('All quotes in the database:')
for row in rows:
    print(row[0])

# Close the database connection
conn.close()

print('Quote added successfully!')