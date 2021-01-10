import os
from pycoingecko import CoinGeckoAPI
import discord
from discord.ext import commands
from keepalive import keepalive

cg = CoinGeckoAPI()

bot = commands.Bot(command_prefix='*', description="crytponero")
coinlist = cg.get_coins_list()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name.upper()}#{bot.user.discriminator} ({bot.user.id})')
    print("------------")


@bot.command(name='trending')
async def comm_get_trending(ctx):
    print(f'{ctx.author} asked {ctx.command}')
    try:
        trending = cg.get_search_trending()

        embed = discord.Embed(
            title="Top 7 trending coin in the last 24h 📈",
            color=discord.Color.blurple()
        )

        embed.set_footer(text=f'Powered by coingecko.com')

        listcoins = []
        top7_dict = {}

        for coin in trending['coins']:
            listcoins.append(coin['item']['id'])

        for name, prices in cg.get_price(ids=listcoins, vs_currencies=['eur', 'usd'], include_24hr_change='true').items():
            top7_dict[name] = prices

        for coin in trending['coins']:
            embed.add_field(name=f"Top {coin['item']['score'] + 1}", value=coin['item']['name'], inline=True)
            embed.add_field(name=f"EUR", value=f"{round(top7_dict[coin['item']['id']]['eur'],2)} ({round(top7_dict[coin['item']['id']]['eur_24h_change'],2)}%)", inline=True)
            embed.add_field(name=f"USD", value=f"{round(top7_dict[coin['item']['id']]['usd'],2)} ({round(top7_dict[coin['item']['id']]['usd_24h_change'],2)}%)", inline=True)

        await ctx.send(embed=embed)

    except (ValueError, TypeError) as e:
        await ctx.send(f"{e}")


@bot.command(name='getcurr')
async def comm_get_embed(ctx, arg):
    print(f'{ctx.author} asked {ctx.command} with {ctx.args[1]}')
    try:
        coin = cg.get_coin_by_id(arg.lower())
        diff = coin['market_data']['price_change_percentage_24h']

        if diff >= 0.00:
            color = discord.Color.green()
            diff = f'{diff} :chart_with_upwards_trend:'
        else:
            color = discord.Color.red()
            diff = f'{diff} :chart_with_downwards_trend:'

        embed = discord.Embed(
            title=coin['name'],
            color=color,
            url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
        )

        embed.set_thumbnail(url=coin['image']['small'])
        embed.add_field(name='USD', value=coin['market_data']['current_price']['usd'], inline=True)
        embed.add_field(name='EUR', value=coin['market_data']['current_price']['eur'], inline=True)
        embed.add_field(name='24h difference', value=diff, inline=False)
        embed.set_footer(text=f'Powered by coingecko.com')

        await ctx.send(embed=embed)

    except (ValueError, TypeError) as e:
        await ctx.send(f'{e.args}')


@bot.command(name='getcurrmore')
async def comm_get_embed_more(ctx,arg):
    print(f'{ctx.author} asked {ctx.command} with {ctx.args[1]}')
    try:
        coin = cg.get_coin_by_id(arg.lower())

        embed = discord.Embed(
            title=coin['name'],
            color=discord.Color.blurple(),
            url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
        )

        embed.set_thumbnail(url=coin['image']['small'])
        embed.add_field(name='Highest 24h', value=f"{coin['market_data']['high_24h']['eur']}€ / {coin['market_data']['high_24h']['usd']}$", inline=True)
        embed.add_field(name='Lowest 24h', value=f"{coin['market_data']['low_24h']['eur']}€ / {coin['market_data']['low_24h']['usd']}$", inline=True)
        embed.add_field(name='\u200B',value='\u200B',inline=True)
        embed.add_field(name='7 days difference',value=round(coin['market_data']['price_change_percentage_7d'],2),inline=True)
        embed.add_field(name='14 days difference',value=round(coin['market_data']['price_change_percentage_14d'],2),inline=True)
        embed.add_field(name='\u200B', value='\u200B', inline=True)

        await ctx.send(embed=embed)
    except (ValueError, TypeError) as e:
        await ctx.send(f'{e.args}')

keepalive()
bot.run(os.getenv('TOKEN'))
