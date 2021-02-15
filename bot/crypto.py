import datetime
import locale
import random
import re

import discord
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

import logs
from errors import *

logger = logs.setup("crypto")

locale.setlocale(locale.LC_ALL, 'en_US')


class CryptoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cg = CoinGeckoAPI()
        self.coinlist = self.cg.get_coins_list()
        self.top300coins = self.cg.get_coins_markets('usd', per_page=250) + self.cg.get_coins_markets('usd',
                                                                                                      per_page=50,
                                                                                                      page=6)

    @staticmethod
    def isNumber(arg):
        """
        Check if the argument is a number (different from isnumeric() builtin method)
        :param arg: the number to check.
        :return: True if the arg is a number. Else False.
        """
        if arg == "nan":  # float() considers "nan" is a number
            return False  # but i dont want it.
        try:
            float(arg)
            return True
        except ValueError:
            return False

    @staticmethod
    def localizeNB(arg):
        """
        Format the number to be more easily readable.
        :param arg: the integer to format.
        :return: a string.
        """
        return locale.format_string("%d", arg, grouping=True)

    def get_coin_by_regex(self, arg):
        """
        Search the id or name or symbol in the list of coins provided by the API.
        :param arg: the string to search.
        :return:  either a list or raise an error if the query provided by the user is invalid.
        """
        coin = {}
        for x in self.coinlist:
            for s in x.values():
                r = re.search(f'(?<!\S){arg}(?!\S)', s)
                if r is not None:
                    return self.cg.get_coin_by_id(x['id'])

        if len(coin) == 0:
            raise InvalidCoinID

    @commands.command(name='ath')
    async def comm_get_ath(self, ctx, arg):
        """
        Return the ATH of the coin
        :param ctx: Discord context
        :param arg: the coin
        :return: Discord embed
        """
        logger.info(f'{ctx.author} asked {ctx.command} with {arg}')
        try:
            coin = self.get_coin_by_regex(arg)

            date = coin['market_data']['ath_date']['eur']
            day = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", date).group()
            time = re.search("[0-9]{2}:[0-9]{2}:[0-9]{2}", date).group()
            diff = datetime.datetime.today() - datetime.datetime.strptime(day, "%Y-%m-%d")

            embed = discord.Embed(
                title=f"{coin['name']} ATH",
                color=discord.Color.blurple(),
                url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
            )

            embed.set_thumbnail(url=coin['image']['small'])
            embed.add_field(name='USD', value=coin['market_data']['ath']['usd'], inline=True)
            embed.add_field(name='EUR', value=coin['market_data']['ath']['eur'], inline=True)
            embed.add_field(name='Date', value=f'{day} {time} ({diff.days} days ago)', inline=False)
            embed.set_footer(text=f'Powered by coingecko.com')

            await ctx.send(embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='mcsim', aliases=['sim'])
    async def comm_get_mcsim(self, ctx, *args):
        """
        Simulate the market cap of a coin with the given price
        :param ctx: Discord context
        :param args: the coin then the wanted price
        :return: Discord embed
        """
        if len(args) != 2:
            await ctx.send("Not enough parameters provided (2 required).")
            return
        logger.info(f'{ctx.author} asked {ctx.command} with {args[0]}/{args[1]}')

        try:
            if not str(args[0]).isalpha():
                await ctx.send("Parameter 1 has to be a string.")
                return
            if not self.isNumber(args[1]):
                await ctx.send("Parameter 2 has to be number.")
                return

            coin = self.get_coin_by_regex(args[0])

            embed = discord.Embed(
                title=f"{coin['name']} simulated market cap (USD)",
                color=discord.Color.blurple(),
                url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
            )

            wantedSimPrice = float(args[1])

            mcSimmed = coin['market_data']['circulating_supply'] * wantedSimPrice
            if coin['market_data']['total_supply']:
                mcMaxSimmed = self.localizeNB(coin['market_data']['total_supply'] * wantedSimPrice)
            else:
                mcMaxSimmed = "infinite supply"
            # marketcap = coin['market_data']['market_cap']['usd']

            leng = len(self.top300coins) - 1
            estimatedRank = 301
            while mcSimmed > self.top300coins[leng]['market_cap'] and leng > 0:
                leng -= 1
                estimatedRank = self.top300coins[leng]['market_cap_rank']

            if estimatedRank == 301:
                estimatedRank = "300+"

            currentPrice = coin['market_data']['current_price']['usd']

            currentPrice = round(currentPrice, 6) if currentPrice < 10 else self.localizeNB(currentPrice)

            simmedprice = round(wantedSimPrice, 6) if wantedSimPrice < 10 else self.localizeNB(wantedSimPrice)

            marketcap = self.localizeNB(coin['market_data']['market_cap']['usd'])

            mcSimmed = self.localizeNB(mcSimmed)

            embed.set_thumbnail(url=coin['image']['small'])
            embed.add_field(name='Current price', value=f"{currentPrice}", inline=True)
            embed.add_field(name='Current market cap', value=f"{marketcap}", inline=True)
            embed.add_field(name='_ _', value='_ _', inline=True)
            embed.add_field(name='Simulated price', value=f"{simmedprice}", inline=True)
            embed.add_field(name='Simulated market cap', value=f"{mcSimmed}", inline=True)
            embed.add_field(name='_ _', value='_ _', inline=True)
            embed.add_field(name='Simulated market cap with max supply', value=f"{mcMaxSimmed}", inline=False)
            embed.add_field(name='Simulated market cap rank', value=f"{estimatedRank}", inline=False)

            embed.set_footer(text=f'Powered by coingecko.com')

            await ctx.send(embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='trending')
    async def comm_get_trending(self, ctx):
        """
        Return the seven trending coins on CoinGecko
        :param ctx: Discord context
        :return: Discord embed
        """
        logger.info(f'{ctx.author} asked {ctx.command}')
        try:
            trending = self.cg.get_search_trending()

            embed = discord.Embed(
                title="Top 7 trending coin in the last 24h 📈",
                color=discord.Color.blurple()
            )

            listcoins = []
            top7_dict = {}

            for coin in trending['coins']:
                listcoins.append(coin['item']['id'])

            for name, prices in self.cg.get_price(ids=listcoins, vs_currencies=['eur', 'usd'],
                                                  include_24hr_change='true').items():
                top7_dict[name] = prices

            for coin in trending['coins']:
                embed.add_field(name=f"Top {coin['item']['score'] + 1}", value=coin['item']['name'], inline=True)
                embed.add_field(name=f"EUR",
                                value=f"{round(top7_dict[coin['item']['id']]['eur'], 2)} ({round(top7_dict[coin['item']['id']]['eur_24h_change'], 2)}%)",
                                inline=True)
                embed.add_field(name=f"USD",
                                value=f"{round(top7_dict[coin['item']['id']]['usd'], 2)} ({round(top7_dict[coin['item']['id']]['usd_24h_change'], 2)}%)",
                                inline=True)

            embed.set_footer(text=f'Powered by coingecko.com')

            await ctx.send(embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='binance')
    async def comm_get_binance(self, ctx, arg):
        """
        Check if the coin is available on Binance exchange platform
        :param ctx: Discord context
        :param arg: the coin
        :return: Discord embed
        """
        logger.info(f'{ctx.author} asked {ctx.command}')
        try:
            coin = self.get_coin_by_regex(arg)

            binance = False
            for x in coin['tickers']:
                if binance is False:
                    if x['market']['name'] == 'Binance':
                        binance = True

            if binance:
                await ctx.send(f"{coin['name']} is avaible on Binance! :white_check_mark:")
            else:
                await ctx.send(f"{coin['name']} is NOT avaible on Binance! :x:")

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='randomcoin')
    async def comm_randomcoin(self, ctx):
        """
        Return a random coin from the 300 market cap coin if the coin is available
        on Binance exchange platform and with the USDT pair.
        :param ctx: Discord context
        :return: Discord embed
        """
        logger.info(f'{ctx.author} asked {ctx.command}')
        try:
            temp = discord.Embed(
                title='Please wait while I find the next Moon shot :rocket::full_moon_with_face:',
                color=discord.Color.blurple(),
            )
            msg = await ctx.send(embed=temp)

            async def get_coin():
                ccoin = self.cg.get_coin_by_id(random.choice(self.top300coins)['id'])
                binance = False
                usdt = False
                for x in ccoin['tickers']:
                    if usdt is False:
                        if x['target'] == "USDT":
                            usdt = True
                    if binance is False:
                        if x['market']['name'] == 'Binance':
                            binance = True

                if False in (binance, usdt):
                    await get_coin()

                return ccoin

            coin = await get_coin()

            embed = discord.Embed(
                title=coin['name'],
                color=discord.Color.blurple(),
                url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
            )

            embed.add_field(name='Available with USDT', value='Yes :white_check_mark:')
            embed.add_field(name='Available on Binance', value='Yes :white_check_mark:')

            embed.add_field(name='\u200B', value='\u200B', inline=True)

            marketcap = await self.localizeNB(coin['market_data']['market_cap']['usd'])
            embed.add_field(name='Market cap', value=f"{marketcap} USD", inline=True)

            embed.add_field(name='USD price', value=coin['market_data']['current_price']['usd'], inline=True)

            embed.add_field(name='\u200B', value='\u200B', inline=True)

            embed.set_thumbnail(url=coin['image']['small'])
            embed.set_footer(text=f'Powered by coingecko.com')
            await msg.edit(content=None, embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='getcurr', aliases=['curr'])
    async def comm_getcurr(self, ctx, arg):
        """
        Return basic infos of the coin
        :param ctx: Discord contect
        :param arg: the coin
        :return: Discord emebed
        """
        logger.info(f'{ctx.author} asked {ctx.command} with {arg}')
        try:
            coin = self.get_coin_by_regex(arg)

            diff = coin['market_data']['price_change_percentage_24h']

            if diff >= 0.00:
                color = discord.Color.green()
                diff = f'+{diff}% :chart_with_upwards_trend:'
            else:
                color = discord.Color.red()
                diff = f'{diff}% :chart_with_downwards_trend:'

            embed = discord.Embed(
                title=coin['name'],
                color=color,
                url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
            )

            marketcap = await self.localizeNB(coin['market_data']['market_cap']['usd'])

            embed.set_thumbnail(url=coin['image']['small'])
            embed.add_field(name='USD', value=coin['market_data']['current_price']['usd'], inline=True)
            embed.add_field(name='EUR', value=coin['market_data']['current_price']['eur'], inline=True)
            embed.add_field(name='24h difference', value=f"{diff}", inline=False)
            embed.add_field(name='Market cap', value=f"{marketcap} USD", inline=False)

            # Check if coin have limited supply
            if coin['market_data']['total_supply']:
                percentSupply = round(
                    (coin['market_data']['circulating_supply'] / coin['market_data']['total_supply']) * 100, 2)
                embed.add_field(name='Circulating supply',
                                value=f"{await self.localizeNB(int(coin['market_data']['circulating_supply']))} ({percentSupply}%)",
                                inline=False)
            else:
                embed.add_field(name='Circulating supply',
                                value=f"{await self.localizeNB(int(coin['market_data']['circulating_supply']))}",
                                inline=False)

            embed.set_footer(text=f'Powered by coingecko.com')

            await ctx.send(embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified ({arg})")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='getcurrmore', aliases=['more'])
    async def comm_getcurrmore(self, ctx, arg):
        """
        Return a bit more infos on the coin
        :param ctx: Discord context
        :param arg: the coin
        :return: Discord embed
        """
        logger.info(f'{ctx.author} asked {ctx.command} with {arg}')
        try:
            coin = self.get_coin_by_regex(arg)

            embed = discord.Embed(
                title=coin['name'],
                color=discord.Color.blurple(),
                url=f'https://www.coingecko.com/en/coins/{coin["id"]}'
            )

            embed.set_thumbnail(url=coin['image']['small'])
            embed.add_field(name='Highest 24h',
                            value=f"{coin['market_data']['high_24h']['eur']}€ / {coin['market_data']['high_24h']['usd']}$",
                            inline=True)
            embed.add_field(name='Lowest 24h',
                            value=f"{coin['market_data']['low_24h']['eur']}€ / {coin['market_data']['low_24h']['usd']}$",
                            inline=True)
            embed.add_field(name='\u200B', value='\u200B', inline=True)
            embed.add_field(name='7 days difference', value=round(coin['market_data']['price_change_percentage_7d'], 2),
                            inline=True)
            embed.add_field(name='14 days difference',
                            value=round(coin['market_data']['price_change_percentage_14d'], 2),
                            inline=True)
            embed.add_field(name='\u200B', value='\u200B', inline=True)

            await ctx.send(embed=embed)

        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")

    @commands.command(name='kill')
    async def comm_kill(self, ctx, arg):
        """
        (Fun command) Return a message stating that the coin have been killed
        :param ctx: Discord context
        :param arg: the coin
        :return: Discord message
        """
        logger.info(f'{ctx.author} asked {ctx.message} with {arg}')
        try:
            coin = self.get_coin_by_regex(arg)

            excla = "!" * random.randrange(2, 12)
            msg = f"{coin['name']} has been killed{excla}"
            await ctx.send(msg)
        except (ValueError, TypeError) as e:
            logger.warning(e)
            await ctx.send(e)
        except InvalidCoinID:
            logger.warning(f"Wrong coin specified.")
            await ctx.send(f"Can not find requested crypto.")


def setup(bot):
    bot.add_cog(CryptoCommands(bot))
