import locale

import discord
from discord.ext import commands

modules_list = ["fun","crypto"]

locale.setlocale(locale.LC_ALL, 'en_US')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', description="crytponero",intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} ({bot.user.id})')
    # if coinlist:
    #     print(f'total coins: {len(coinlist)}')
    print("------------")

if __name__ == "__main__":
    for module in modules_list:
        try:
            bot.load_extension(module)
        except Exception as e:
            print(f"{e}\nFailed to load {module}")

    bot.run(open('.env').readline())
