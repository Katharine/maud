import json
import os


class Settings:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'setup.json')) as f:
            self._settings = json.load(f)

    @property
    def discord_token(self):
        return self._settings['discord_token']

    @property
    def default_cogs(self):
        return self._settings['default_cogs']
