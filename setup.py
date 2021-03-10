from setuptools import setup

APP = ['PyPlus.py']
DATA_FILES = ['Settings/cmd-settings.json']
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
