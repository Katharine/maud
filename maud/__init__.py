import logging

from discord.ext.commands import Bot

from .util import Settings

logging.basicConfig(level=logging.INFO)

bot = Bot('!')
bot.settings = Settings()


def run_bot():
    for cog in bot.settings.default_cogs:
        bot.load_extension('maud.cogs.{}'.format(cog))
    bot.run(bot.settings.discord_token)
