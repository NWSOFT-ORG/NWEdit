from setuptools import setup

APP = ['PyPlus.py']
OPTIONS = {'iconfile': 'Images/icon.icns'}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
