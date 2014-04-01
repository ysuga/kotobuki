"""
en_US:
 brief : |
  Package administration command.
 description : |
  This command will do package  administration.
  You can find your package by list subcommand.
  You can create your package by create subcommand, 
  and you can clone your package from repository.
  Fork command will create your own repository in your own upstream repository,
  this will be useful if you want to modify the package for your own purpose.
  Your package will be automatically registered into your system setting,
  if yours is not, do register.
  If you purge the registration, do unregister.
 subcommands :
  list : |
   Show the packages in your platform.
  create : |
   Create New Package. ex., $ wasanbon-admin.py package create YOUR_PACKAGE_NAME
  register : |
   Register the package to the pacakge database.
   ex.,  $ wasanbon-admin.py package register YOUR_PACKAGE_NAME
  unregister : |
   Unregister the package from the package database
   ex.,  $ wasanbon-admin.py package unregister YOUR_PACKAGE_NAME
  repository : |
   Show the package list in the repository
  clone      : |
   Clone the package from internet. 
   This create directory in your current directory.
   ex., $ wasanbon-admin.py package clone YOUR_TARGET_REPOSITORY_NAME
  fork      : |
   Fork the package from internet. 
   This create directory in your current directory.
   ex., $ wasanbon-admin.py package clone YOUR_TARGET_REPOSITORY_NAME
"""

import os, sys, optparse, getpass
import wasanbon
import wasanbon.core.package as pack
from  wasanbon.core.package import workspace
from wasanbon.core import repositories


def alternative(argv=None):

    return_repo_cmd = ['clone', 'fork']
    files_cmd = ['register', 'unregister']
    all_cmd = ['create', 'list', 'directory', 'repository', 'diff'] + files_cmd + return_repo_cmd
    if not argv:
        return all_cmd
    if len(argv) < 3:
        return all_cmd 

    if argv[2] in return_repo_cmd:
        repos = pack.get_repositories()
        return [repo.name for repo in repos]
    elif argv[2] in files_cmd:
        return os.listdir(os.getcwd())
    return ['a', 'b']
    
def execute_with_argv(args, verbose):
    wasanbon.arg_check(args, 3)

    force = False
    clean = False
    
    if '-l' in args:
        long_option = True
    else:
        long_option = False
    args = [arg for arg in args if not arg is '-l']

    if args[2] == 'create':
        _create(args, verbose, force ,clean)

    elif args[2] == 'register':
        _register(args, verbose)

    elif args[2] == 'unregister':
        _unregister(args, verbose, force, clean)
        
    elif args[2] == 'list':
        _list(args, verbose, force, clean, long=long_option)

    elif args[2] == 'directory':
        try:
            _package = pack.get_package(args[3].strip())
            print _package.path
        except:
            print '.'

    elif args[2] == 'repository':
        sys.stdout.write(' @ Listing Package Repositories\n')
            #rtcs, packs = repositories.load_repositories(verbose=verbose)
        repos = pack.get_repositories(verbose=verbose)
        for repo in repos:
            print_repository(repo, long=long_option)

    elif args[2] == 'clone':
        wasanbon.arg_check(args,4)
        repo = pack.get_repository(args[3], verbose=verbose)
        sys.stdout.write(' @ Cloning Package (%s)\n' % args[3])
        _package = repo.clone(verbose=verbose)
        for rtc_repo in _package.rtc_repositories:
            sys.stdout.write('    @ Cloning RTC (%s)\n' % rtc_repo.name)
            rtc_ = rtc_repo.clone(path=_package.rtc_path, verbose=verbose)
        
    elif args[2] == 'fork':
        repo = _fork(args, verbose, force, clean)
        sys.stdout.write(' @ Cloning Package (%s)\n' % args[3])
        _package = repo.clone(verbose=verbose)
        for rtc_repo in _package.rtc_repositories:
            sys.stdout.write('    @ Cloning RTC (%s)\n' % rtc_repo.name)
            rtc_ = rtc_repo.clone(path=_package.rtc_path, verbose=verbose)

        
    elif args[2] == 'diff':
        wasanbon.arg_check(args, 5)
        sys.stdout.write(' @ Diff between %s and %s\n' % (args[3], args[4]))
        repo1 = pack.get_package(args[3], verbose=verbose)
        repo2 = pack.get_package(args[4], verbose=verbose)
        diff = pack.diff(repo1, repo2)
        print_diff(diff)
    else:
        raise wasanbon.InvalidUsageException()

def print_repository(repo, long=False):

    if long:
        sys.stdout.write('    - ' + repo.name + '\n')
        sys.stdout.write('       - description : ' + repo.description + '\n')
        sys.stdout.write('       - url         : ' + repo.url + '\n')

    else:
        sys.stdout.write('    - ' + repo.name + ' ' * (24-len(repo.name)) + ' : ' + repo.description + '\n')


def _create(args, verbose, force, clean):
    wasanbon.arg_check(args, 4)
    sys.stdout.write(' @ Creating package %s\n' % args[3])
    _package = pack.create_package(args[3], verbose=verbose)


def _register(args, verbose):
    if len(args) < 4:
        args.append(os.getcwd())
    else:
        os.chdir(args[3])
        args.remove(args[3])
        args.append(os.getcwd())
    wasanbon.arg_check(args, 4)
    #_package = pack.get_package(args[3], verbose=verbose)
    _package = pack.Package(args[3])
    sys.stdout.write(' @ Initializing Package in %s\n' % _package.name)
    _package.register(verbose=verbose)
    
def _unregister(args, verbose, force, clean):
    wasanbon.arg_check(args, 4)
    sys.stdout.write(' @ Removing workspace %s\n' % args[3])
    dic = workspace.load_workspace()
    if not args[3] in dic.keys():
        sys.stdout.write(' - Can not find package %s\n' % args[3])
        return
    try:
        _package = pack.get_package(args[3], verbose=verbose)
        _package.unregister(verbose=verbose, clean=clean)
    except wasanbon.PackageNotFoundException, ex:
        sys.stdout.write(' - Package Not Found (%s).\n' % args[3])
        from wasanbon import util
        if util.yes_no('Do you want to remove the record?') == 'yes':
            dic = workspace.load_workspace()
            dic.pop(args[3])
            workspace.save_workspace(dic)
            sys.stdout.write(' - Removed.\n')

def _list(args, verbose, force ,clean, long=False):
    #sys.stdout.write(' @ Listing packages.\n')
    _packages = pack.get_packages(verbose=verbose)
    if not long:
        for p in _packages:
            sys.stdout.write(p.name + ' \n')
        return
    for _package in _packages:
        sys.stdout.write(' ' + _package.name + ' '*(10-len(_package.name)) + ':' + _package.path + '\n')

def _fork(args, verbose, force ,clean):
    wasanbon.arg_check(args, 4)
    sys.stdout.write(' @ Forking Package from Repository %s\n' % args[3])
    user, passwd = wasanbon.user_pass()
    original_repo = pack.get_repository(args[3], verbose=verbose)
    repo = original_repo.fork(user, passwd, verbose=verbose)
    _package = repo.clone(verbose=verbose)

                

def print_diff(diff):
    [plus, minus] = diff.rtcs
    sys.stdout.write(' - RTC\n')
    for rtc in plus:
        sys.stdout.write('  + %s\n' % rtc.name)
    for rtc in minus:
        sys.stdout.write('  - %s\n' % rtc.name)

