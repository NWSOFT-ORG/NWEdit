import os
from configparser import ConfigParser
from typing import Text


class NotGitRepoError(Exception):
    def __init__(self) -> None:
        super().__init__("Error: Not a Git Repository")


def read_gitignore(path: Text) -> list:
    """This method reads a .gitignore file"""
    try:
        with open(os.path.join(path, ".gitignore")) as f:
            ignored_items = f.readlines()
        ignored_items = [i[:-1] for i in ignored_items]
        return ignored_items
    except FileNotFoundError:
        raise NotGitRepoError


def read_branches(path: Text) -> list:
    """This method reads the branches"""
    branches_list = os.listdir(os.path.join(path, ".git/refs/heads"))
    return branches_list


def read_remotes(path: Text) -> dict:
    remotes = {}
    config = ConfigParser()
    config_file = os.path.join(path, ".git/config")
    config.read(config_file)

    for item in config.sections():
        if item.startswith("remote"):
            remote = eval(item.split()[1])
            url = config.get(item, "url")
            remotes[remote] = url
    return remotes


print(read_remotes("/home/runner/PyPlus"))
