import discord
from discord.ext import commands

import logs

logger = logs.setup("main")

modules_list = ["fun", "crypto"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='*', description="crytponero", intents=intents)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} ({bot.user.id})\n------------')


if __name__ == "__main__":
    for module in modules_list:
        try:
            bot.load_extension(module)
        except Exception:
            logger.exception(f"Failed to load {module}")

    bot.run(open('.env').readline())
