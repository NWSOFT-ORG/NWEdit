"""
This is a build_mac.py script for py2app

Usage:
    python build_mac.py py2app
"""

from setuptools import setup

APP = ["main.py"]
DATA_FILES = []
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
