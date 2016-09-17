from setuptools import setup, find_packages

__author__ = 'katharine'


requires = [
    'discord.py==0.11',
    'peewee-async==0.5.5',
    'Pillow',
    'apng',
    'images2gif',
]

__version__ = None  # Overwritten by executing version.py.
with open('maud/version.py') as f:
    exec(f.read())

setup(name='maud',
      version=__version__,
      description="Pebble's Discord bot.",
      url='https://github.com/Katharine/maud',
      author='Katharine Berry',
      author_email='katharine@kathar.in',
      license='MIT',
      packages=find_packages(),
      package_data={},
      install_requires=requires,
      entry_points={
          'console_scripts': ['maud=maud:run_bot'],
      })
