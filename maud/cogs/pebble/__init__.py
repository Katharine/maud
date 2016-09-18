import html
import os
import re

import aiohttp
import discord
import discord.ext.commands as commands
from discord.ext.commands.bot import Bot


def setup(bot: Bot):
    bot.add_cog(Pebble(bot))


class Pebble:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.symbols = None

    async def on_message(self, message: discord.Message):
        result = re.search(r'system://images/([A-Z_]+)', message.content)
        if result is not None:
            path = os.path.join(os.path.dirname(__file__), 'images', result.group(1)) + '.png'
            print(os.getcwd(), path)
            if os.path.exists(path):
                await self.bot.send_file(message.channel, path)
                return

    @commands.command()
    async def api(self, symbol: str):
        """
        Looks up a symbol in the pebble API.
        """
        await self._get_symbols()
        if symbol in self.symbols:
            symbol = self.symbols[symbol]
            if symbol['kind'] == 'fn':
                signature = '{} {}({});'.format(symbol['returns'], symbol['name'],
                                               'void' if len(symbol['params']) == 0 else ', '.join(
                                                   '{} {}'.format(x['type'], x['name']) for x in symbol['params']))
                description = self._clean_html(symbol['description'])
                if len(symbol['params']) > 0:
                    params = "\n\n**Parameters**\n" + '\n'.join('`{}`: {}'.format(
                        x['name'], self._code(x['description'])) for x in symbol['params'])
                else:
                    params = ''
                if symbol['return_desc']:
                    ret_desc = "\n\n**Returns:** " + self._code(symbol['return_desc'])
                else:
                    ret_desc = ''
                await self.bot.say("```c\n{}\n```{}{}{}".format(signature, description, params, ret_desc))
            else:
                await self.bot.say("`{}`: {}".format(symbol['name'], self._clean_html(symbol['description'])))
        else:
            await self.bot.say("No such symbol.")

    async def _get_symbols(self):
        if self.symbols is None:
            async with aiohttp.get("https://cloudpebble.net/static/ide/documentation.json") as response:
                self.symbols = await response.json()

    @classmethod
    def _code(cls, string: str):
        return re.sub(r'(([A-Z][a-z]+[A-Z]\w*)|(\w+_\w+)|true|false|null)', r'`\1`', cls._clean_html(string))

    @classmethod
    def _clean_html(cls, html_str: str):
        md = re.sub(r'\*_~`\\', r'\\\1', html_str)
        md = re.sub(r'<code>(.+?)</code>', r'`\1`', md)
        md = re.sub(r'<pre>(.+?)</pre>', r'```c\n\1```', md, flags=re.DOTALL)
        md = re.sub(r'<ul>(.+?)</ul>', r'\n\1\n', md)
        md = re.sub(r'<li>(.+?)</li>[\s\r\n]*', r'* \1\n', md, flags=re.DOTALL)
        md = re.sub(r'<p>(.+?)</p>', r'\1\n\n', md, flags=re.DOTALL)
        md = html.unescape(md)
        md = re.sub(r'\n+', '\n', md)
        # Hack because we fail on any nesting because regex
        md = re.sub(r'<.+?>', '', md)
        return md.strip()
