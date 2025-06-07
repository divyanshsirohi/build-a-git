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


# argparse is a Python module used to handle command line arguments,
# here we create a parser object with a description "Git clone"
argparser = argparse.ArgumentParser(description="Git clone")

# Subparsers allow us to create multiple commands, like 'init', 'add', etc.
# Here we define that the program expects commands, and the chosen command
# will be saved in args.command.
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True  # Makes it mandatory to provide a command

def main(argv=sys.argv[1:]):
    # Parse the command line arguments from argv (default: from sys.argv)
    args = argparser.parse_args(argv)
    
    # Python 3.10+ 'match' statement to call different functions based on command
    match args.command:
        case "add"          : cmd_add(args)          # Add files to staging
        case "cat-file"     : cmd_cat_file(args)     # Display contents of an object
        case "check-ignore" : cmd_check_ignore(args) # Check if files are ignored
        case "checkout"     : cmd_checkout(args)     # Switch branches or restore files
        case "commit"       : cmd_commit(args)       # Commit staged files
        case "hash-object"  : cmd_hash_object(args)  # Hash file contents
        case "init"         : cmd_init(args)          # Initialize a new repo (implemented here)
        case "log"          : cmd_log(args)           # Show commit logs
        case "ls-files"     : cmd_ls_files(args)      # List files in the index
        case "ls-tree"      : cmd_ls_tree(args)       # Show tree objects
        case "rev-parse"    : cmd_rev_parse(args)     # Parse revision references
        case "rm"           : cmd_rm(args)             # Remove files
        case "show-ref"     : cmd_show_ref(args)      # Show refs (branches, tags)
        case "status"       : cmd_status(args)        # Show repository status
        case "tag"          : cmd_tag(args)           # Manage tags
        case _              : print("Bad argument passed!") # Unknown command


class GitRepository(object):
    """Class representing a Git repository on disk"""
    
    worktree = None     # The root directory of the working tree (your project)
    gitdir = None       # The path to the '.git' directory containing git metadata
    conf = None         # Configuration parser object for .git/config file
    
    def __init__(self,path,force=False):
        # Initialize GitRepository with the path to working tree
        self.worktree = path
        
        # Set path to the .git directory inside the working tree
        self.gitdir = os.path.join(path, ".git")
        
        # If not forcing, check if the .git directory exists and is a directory
        if not (force or os.path.isdir(self.gitdir)):
            # If not valid .git directory, raise an exception
            raise Exception(f"Not a Git repository {path}")

        # Create a ConfigParser object to read configuration settings
        self.conf = configparser.ConfigParser()
        
        # Get the path to the config file inside the .git directory
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            # If the config file exists, read it into the ConfigParser
            self.conf.read([cf])
        elif not force:
            # If config file missing and not forcing, raise an exception
            raise Exception("Configuration file missing")

        if not force:
            # Check if the repository format version in the config is 0 (expected for now)
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                # If version unsupported, raise exception
                raise Exception("Unsupported repositoryformatversion: {vers}")


def repo_path(repo, *path):
    """
    Returns the path inside the .git directory by joining multiple parts.
    For example, repo_path(repo, "refs", "heads", "master") returns
    '.git/refs/heads/master'
    """
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """
    Similar to repo_path but ensures the parent directory exists.
    If mkdir=True, it creates the parent directories if they don't exist.
    Returns the full path to the file inside .git.
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):   # Create parent directory if needed
        return repo_path(repo, *path)              # Return full path to the file

def repo_dir(repo, *path, mkdir=False):
    """
    Similar to repo_path but works for directories.
    Checks if the directory exists. If not and mkdir=True, creates it.
    Returns the directory path or None.
    """
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path    # Directory exists, return path
        else:
            # Path exists but it's a file, not a directory
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)  # Create the directory and any missing parents
        return path
    else:
        return None        # Directory does not exist, and mkdir is False


def repo_create(path):
    """
    Creates a new Git repository at the given path.
    It sets up the .git directory structure and default files.
    """
    # Create a GitRepository object for the path with force=True to skip checks
    repo = GitRepository(path, True)

    # Check if the working directory exists
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            # If it exists but is not a directory, error out
            raise Exception(f"{path} is not a directory!")
        # If .git directory exists and is not empty, it's already a repo
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is already a git repository!")
    else:
        # If the worktree directory doesn't exist, create it
        os.makedirs(repo.worktree)

    # Create required directories inside .git (branches, objects, refs/tags, refs/heads)
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # Create a description file with a default message
    with open(repo_file(repo, "description", mkdir=True), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # Create the HEAD file which points to the master branch by default
    with open(repo_file(repo, "HEAD", mkdir=True), "w") as f:
        f.write("ref: refs/heads/master\n")

    # Create the config file with default configuration options
    with open(repo_file(repo, "config", mkdir=True), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo   # Return the newly created GitRepository object


def repo_default_config():
    """
    Returns a ConfigParser object with default Git configuration settings.
    These settings are basic config options needed by Git.
    """
    ret = configparser.ConfigParser()

    ret.add_section("core")                              # Add 'core' section in config
    ret.set("core", "repositoryformatversion", "0")     # Set repo format version to 0
    ret.set("core", "filemode", "false")                 # Don't track file mode changes
    ret.set("core", "bare", "false")                      # Repository is non-bare (has working tree)

    return ret


# Adding the 'init' command to the argument parser, with help message
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",                               # 'path' argument is optional, default '.'
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")
                   
def repo_find(path=".", required=True):
    """
    Find a Git repository by looking for the .git directory starting
    at the given path and moving up parent directories recursively.
    If required=True and repo not found, raises an exception.
    """
    path = os.path.realpath(path)                 # Convert to absolute path

    if os.path.isdir(os.path.join(path, ".git")): # If .git directory exists here, return GitRepository
        return GitRepository(path)

    # Otherwise, try searching the parent directory
    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:                             # If we reached the root directory without finding .git
        if required:
            raise Exception("No git directory.")  # Raise error if repo is required
        else:
            return None                            # Otherwise, return None

    # Recursive call to check parent directory
    return repo_find(parent, required)


"""
    Git is a content adressed file system i.e. the file names arent 
    random but mathematically derived from their contents rather than
    arbritary names. hence, if there is even a small byte level change
    in the file then the name of the file will also change To put it 
    simply: you don’t modify a file in git, you create a new file in a 
    different location. Objects are just that: files in the git repository, 
    whose paths are determined by their contents.
"""

class GitObject(object):

    def __init__(self, data=None):
        if data!=None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        # implement in subclass
        
        raise Exception("Unimplemented")

    def deserialize(self, data):
        raise Exception("Unimplementeda")

    def init(self):
        pass



def cmd_init(args):
    """
    Command handler for 'git init' command.
    Calls repo_create to create a new repository at the given path.
    """
    repo_create(args.path)


