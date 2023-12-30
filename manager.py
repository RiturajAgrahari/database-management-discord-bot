import discord
from MySql import *
from Informations import *

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)

owner = 'your_discord_id'  # Your Discord ID


@client.event
async def on_message(message):
    # Check if message was sent in a private channel
    if message.channel.type == discord.ChannelType.private:
        if message.attachments:
            print(f"Received DM from {message.author}: {message.attachments[0]}")
        else:
            pass

        # Verify that the user is the owner of the bot
        if str(message.author.mention) == owner:

            # To get all the commands that can be used through bot
            if message.content == '/help':
                print("using /help")
                embed = info(message)
                await message.channel.send(embed=embed)

            # To check that the bot is working fine.
            elif message.content == '/test':
                print("received test")
                await message.channel.send('Test completed successfullly!')

            # To setup your MySql
            elif message.content == '/setup':
                print("setting up database...")
                await setup_database(message, '')

            # To start using your mysql database
            elif message.content == '/mysql':
                print(f"{message.author} : Opening MySql...")
                await security_msg(message)

            else:
                print("no commands like that!")

        else:
            pass


# Run the bot
client.run('your_bot_token')
