# Fun commannds

import discord
from discord.ext import commands

import random

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def isNerot(self, ctx):
        if ctx.author.id != 131486383230550016:
            await ctx.send('Command not available')
            return False
        else: return True

    @commands.command(name='sadge')
    async def fin_cest_sad_quoi(self,ctx):
        print(f'{ctx.author} est Sadge')
        await ctx.message.delete()
        await ctx.send(content="'fin c'est sad quoi. . . ",
                       file=discord.File('sad.png'))

    @commands.command(name='menfou')
    async def menfou(self,ctx):
        print(f"{ctx.author} s\'ENFOU")
        await ctx.message.delete()
        await ctx.send(content="MENFOU",
                       file=discord.File('menfou.png'))

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