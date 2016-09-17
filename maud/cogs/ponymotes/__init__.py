import aiohttp
import re
import os
import subprocess
import json
import io

from PIL import Image, ImageFilter
import tempfile

import discord
from discord.ext.commands.bot import Bot


def setup(bot: Bot):
    bot.add_cog(PonymoteResponse(bot))


class PonymoteResponse:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        result = re.search(r'\[]\((/[a-z0-9!-]+?)?\)', message.content, re.IGNORECASE)
        if result is not None:
            specifier = result.group(1).split('-')
            emote = specifier[0]
            flags = specifier[1:]

            if 'nomaud' in flags:
                return

            with open(os.path.join(os.path.dirname(__file__), 'mlp.json')) as f:
                mlp = json.load(f)
            if emote in mlp:
                data = mlp[emote]['Emotes']['']
                result = await aiohttp.get('http:%s' % data['Image'])
                input_png = await result.read()
                img = Image.open(io.BytesIO(input_png))
                if 'Size' in data:
                    offset = [-x for x in data.get('Offset', (0, 0))]
                    img = img.crop((offset[0], offset[1], offset[0] + data['Size'][0], offset[1] + data['Size'][1]))
                transform = data.get('CSS', {}).get('transform', '')

                # Modifiers
                xflip = 'scaleX(-1)' in transform or 'r' in flags
                if xflip:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)

                yflip = 'scaleY(-1)' in transform or 'f' in flags
                if yflip:
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)

                if 'invert' in flags:
                    img = img.point([255 - x for x in range(256)] * 3 + list(range(256)))

                angle = [x for x in flags if x in ('45', '90', '135', '180', '225', '270', '315')]
                if angle:
                    img = img.rotate(-int(angle[-1]), resample=Image.BICUBIC, expand=True)

                blur = [x for x in flags if re.match(r'^blur(\d+)?$', x)]
                if blur:
                    blur = blur[-1]
                    blur = re.match(r'blur(\d+)?', blur).group(1)
                    if not blur:
                        blur = 2
                    blur = int(blur)
                    new_img = Image.new(img.mode, (img.width+blur*3, img.height+blur*3))
                    new_img.paste(img, (blur, blur))
                    img = new_img.filter(ImageFilter.GaussianBlur(blur))

                if 'mono' in flags:
                    channels = img.split()
                    img = img.convert('L')
                    if len(channels) == 4:
                        img = Image.merge("RGBA", (img, img, img, channels[3]))
                    else:
                        img = img.convert('RGBA')


                intensity = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, 1), (1, 0), (1, -1), (1, 1), (1, -1), (-1, 1)]
                output_png = io.BytesIO()
                spin_flags = set(flags) & {'spin', 'zspin', '!zspin'}
                if spin_flags:
                    tmpdir = tempfile.mkdtemp()
                    max_w, max_h = 0, 0
                    flag = spin_flags.pop()
                    direction = 1 if '!' in flag else -1
                    for theta in range(0, 360, 6):
                        w, h = img.rotate(theta, expand=True).size
                        max_w = max(w, max_w)
                        max_h = max(h, max_h)

                    new_img = Image.new(img.mode, (max_w, max_h))
                    new_img.paste(img, ((max_w - img.width) // 2, (max_h - img.height) // 2))
                    for i, theta in enumerate(range(0, 360, 6)):
                        frame = new_img.rotate(direction * theta, resample=Image.BICUBIC)
                        frame.save(os.path.join(tmpdir, '%02d.png' % i))
                    subprocess.check_call(["convert", "-dispose", "previous", "-delay", "3.3", "-loop", "0"] + [os.path.join(tmpdir, '%02d.png' % x) for x in range(60)] + [os.path.join(tmpdir, 'output.gif')])
                    with open(os.path.join(tmpdir, 'output.gif'), 'rb') as f:
                        output_png.write(f.read())
                    ext = 'gif'
                elif 'intensifies' in flags:
                    tmpdir = tempfile.mkdtemp()
                    for i, offset in enumerate(intensity):
                        frame = Image.new(img.mode, (img.width+2, img.height+2))
                        frame.paste(img, (offset[0] + 1, offset[1] + 1))
                        frame.save(os.path.join(tmpdir, '%s.png' % i))
                    subprocess.check_call(["convert", "-dispose", "previous", "-delay", "2", "-loop", "0"] + [os.path.join(tmpdir, '%s.png' % x) for x in range(10)] + [os.path.join(tmpdir, 'output.gif')])
                    with open(os.path.join(tmpdir, 'output.gif'), 'rb') as f:
                        output_png.write(f.read())
                    ext = 'gif'
                else:
                    img.save(output_png, 'png')
                    ext = 'png'

                output_png.seek(0)
                await self.bot.send_file(message.channel, output_png, filename='%s.%s' % ('-'.join(specifier), ext))
                return
