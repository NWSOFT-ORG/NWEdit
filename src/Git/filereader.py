import os
import configparser


class NotGitRepoError(Exception):
    def __init__(self):
        super().__init__('Error: Not a Git Repository')


def read_config(path: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(os.path.join(path, '.git/config'))
    return config


def read_gitignore(path: str) -> list:
    """This method reads a .gitignore file"""
    try:
        with open(os.path.join(path, '.gitignore')) as f:
            ignored_items = f.readlines()
        ignored_items = [i[:-1] for i in ignored_items]
        return ignored_items
    except FileNotFoundError:
        raise NotGitRepoError


def read_branches(path: str) -> list:
    """This method reads the branches"""
    branches_list = os.listdir(os.path.join(path, '.git/refs/heads'))
    return branches_list


def read_remotes(path: str) -> dict:
    config = read_config(path)
    remotes_list = {}
    for section in config.sections():
        if section.startswith('remote'):
            remote = eval(section.split()[1])
            url = config.get(section, 'url')
            remotes_list[remote] = url
    return remotes_list
