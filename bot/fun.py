# Fun commannds

import random

import discord
from discord.ext import commands


class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def isNerot(self, ctx):
        if ctx.author.id != 131486383230550016:
            await ctx.send('Command not available')
            return False
        else:
            return True

    @commands.command(name='sadge')
    async def fin_cest_sad_quoi(self, ctx, *arg):
        print(f'{ctx.author} est Sadge')
        await ctx.message.delete()
        msg = "'fin c'est sad quoi. . . "
        if arg:
            for x in arg:
                msg = msg + ' ' + str(x)

        await ctx.send(content=f'{msg}',
                       file=discord.File('sad.png'))
        # https://cdn.betterttv.net/emote/5e0fa9d40550d42106b8a489/3x

    @commands.command(name='menfou')
    async def menfou(self, ctx):
        print(f"{ctx.author} s\'ENFOU")
        await ctx.message.delete()
        await ctx.send(content="MENFOU",
                       file=discord.File('menfou.png'))
        # https://cdn.frankerfacez.com/emoticon/323585/4

    @commands.command(name='anyone')
    async def comm_anyone(self, ctx):
        if await self.isNerot(ctx):
            try:
                yeet = []
                for member in ctx.message.guild.members:
                    yeet.append(member.id)
                msg = f"<@{random.choice(yeet)}>"
                await ctx.send(msg)

            except (ValueError, TypeError):
                pass


def setup(bot):
    bot.add_cog(FunCommands(bot))
