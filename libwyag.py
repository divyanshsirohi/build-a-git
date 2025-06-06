import argparse
import configparser
from datetime import datetime
import grp,pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib


#argparse - argparser to parse command line options arguments and subcommands
argparser = argparse.ArgumentParser(description="Git clone")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        case "check-ignore" : cmd_check_ignore(args)
        case "checkout"     : cmd_checkout(args)
        case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        case "log"          : cmd_log(args)
        case "ls-files"     : cmd_ls_files(args)
        case "ls-tree"      : cmd_ls_tree(args)
        case "rev-parse"    : cmd_rev_parse(args)
        case "rm"           : cmd_rm(args)
        case "show-ref"     : cmd_show_ref(args)
        case "status"       : cmd_status(args)
        case "tag"          : cmd_tag(args)
        case _              : print("Bad argument passed!")


class GitRepository(object):
    """A git repo"""
    
    worktree = None
    gitdir = None                                                           #.git file
    conf = None                                                             #.git/config file
    
    def __init__(self,path,force=False):                                    #constructor class
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")
        
        if not (force or os.path.isdir(self.gitdir)):                       #checks if the directory is a valid git repo 
            raise Exception(f"Not a Git repository {path}")

         # read configuration file in .git/config
        self.conf = configparser.ConfigParser()                             
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:                                                     #handles the missing .git/config file
            raise Exception("Configuration file missing")

        if not force:                                                       #checks for formatversion to be equal to 0 since its new
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion: {vers}")


def repo_path(repo, *path):                                             #'*' in path allows for a variable number of arguments
    """computes paths and missing dir"""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """Same as repo_path, but create dirname(*path) if absent.  For
    example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will create
    .git/refs/remotes/origin."""

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=False):
        """Same as repo_path, but mkdir *path if absent if mkdir."""

        path = repo_path(repo, *path)

        if os.path.exists(path):
            if (os.path.isdir(path)):
                return path
            else:
                raise Exception(f"Not a directory {path}")

        if mkdir:
            os.makedirs(path)
            return path
        else:
            return None

    
def repo_create(path):
    """Create a new repository at path."""

    # Create the repository with force=True to bypass validation checks
    # since we're creating a new repository
    repo = GitRepository(path, True)

    # Check if the worktree exists and is valid
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory!")
        # Check if .git directory exists and is not empty
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is already a git repository!")
    else:
        # Create the worktree directory if it doesn't exist
        os.makedirs(repo.worktree)

    # Create the necessary directory structure
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # Create the description file
    with open(repo_file(repo, "description", mkdir=True), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # Create the HEAD file pointing to master branch
    with open(repo_file(repo, "HEAD", mkdir=True), "w") as f:
        f.write("ref: refs/heads/master\n")

    # Create the config file with default settings
    with open(repo_file(repo, "config", mkdir=True), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret

#creating the git init[path] command

argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")
                   
def repo_find(path=".", required=True):
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    # If we haven't returned, recurse in parent, if w
    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # Bottom case
        # os.path.join("/", "..") == "/":
        # If parent==path, then path is root.
        if required:
            raise Exception("No git directory.")
        else:
            return None

    # Recursive case
    return repo_find(parent, required)

def cmd_init(args):
    repo_create(args.path)




