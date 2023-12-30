import discord
from discord.ui import Button, View


def info(message):
    embed = discord.Embed(
        title="MYSQL",
        description=f"Hi! I am your personal database managing bot to manage your whole database!",
        color=discord.Color.green(),
    )
    embed.add_field(
        name='/setup',
        value='You have to setup the database before using it.',
        inline=False
    )
    embed.add_field(
        name='/mysql',
        value='To start operating you have to write the above command.',
        inline=False
    )
    embed.add_field(
        name='/test',
        value='To check the working! you have to write the above command!',
        inline=False
    )
    embed.set_footer(text=f"By {message.author.name}")

    return embed