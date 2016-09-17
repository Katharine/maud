import discord.ext.commands as commands

from maud.version import __version__


def setup(bot: commands.Bot):
    bot.add_cog(Meta(bot))


class Meta:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self):
        await self.bot.say("pong!")

    @commands.command()
    async def version(self):
        await self.bot.say("```Maud version {}.```".format(__version__))
