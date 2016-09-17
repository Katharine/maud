import os
import re

import discord
from discord.ext.commands.bot import Bot


def setup(bot: Bot):
    bot.add_cog(Timeline(bot))


class Timeline:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        result = re.search(r'system://images/([A-Z_]+)', message.content)
        if result is not None:
            path = os.path.join(os.path.dirname(__file__), 'images', result.group(1)) + '.png'
            print(os.getcwd(), path)
            if os.path.exists(path):
                await self.bot.send_file(message.channel, path)
                return
