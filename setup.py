from setuptools import setup

APP = ['PyPlus.py']
OPTIONS = {'iconfile': 'icon.icns'}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
