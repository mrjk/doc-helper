#!/usr/bin/env python3

# Libraries import
################################################################################

# Std libs
import logging
import yaml

# Specialised libs
import pickle
import click

# Local libs
import lib.common as common
from lib.common import out_yaml
from lib.mods import Mods


# Constants
################################################################################
APP_NAME='app_name'
APP_VERSION='0.0.1'
APP_DATE=''
APP_LICENSE=''
APP_AUTHOR='mrjk'


global DIR_APP_SHARE 
DIR_APP_SHARE = '/home/jez/.usr/local/share'
DIR_MOD_ENABLED ='/home/jez/.local/share/Steam/steamapps/workshop/content/255710'
DIR_MOD_CACHED = DIR_APP_SHARE + '/' + APP_NAME + '/mods/cached'


# Initialisation
################################################################################

# Enable logger
logger = common.Logger()
log = logger.log(level='normal')
#log = logger.log(level='debug')
log_except = logger.log_except

# General stuffs
################################################################################


# Main cli
################################################################################


# Group: Main
# ===================================

@click.group()
@click.version_option()

@click.pass_context
@click.option('--debug', '-d',
        default=False,
        is_flag=True,
        help='Enable debug mode')
@click.option('--dry-run', '-n',
        default=False,
        is_flag=True,
        help='Enable dry run mode')
def cli(ctx, debug=False, dry_run=False):
    """ Command line to manage SteamWorkshop extensions for Cities Skylines"""

    # Register behavioral cli
    ctx.obj = {}
    ctx.obj['run'] = not dry_run
    ctx.obj['debug'] = debug

    if debug:
        log.info ('Debug mode is enabled')
    if dry_run:
        log.info ('Dry run mode is enabled')



# Group: Main/Mod
# ===================================

@cli.group()
@click.pass_context
@click.option('--mod-enabled-dir',
        default=DIR_MOD_ENABLED,
        help='Define the game mod directory')
@click.option('--mod-cached-dir',
        default=DIR_MOD_CACHED,
        help='Define the cached mod directory')
def mod(ctx, mod_enabled_dir, mod_cached_dir):
    """Manages mods."""

    # Show debug messages
    log.debug ('mod_enabled_dir = %s' % mod_enabled_dir)
    log.debug ('mod_cached_dir = %s' % mod_cached_dir)

    #print ('THIS IS MY MOD MGR')



@mod.command()
@click.pass_context
@click.argument('filter', 
        type=click.Choice(
            ['all',
            'enabled', 'disabled',
            'cached', 'uncached',
            'managed', 'unmanaged']
            ),
        default='enabled'
        )
def list(ctx, filter):
    """Show the list of mods"""
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)

    # Manage all keyword
    if 'all' in filter:
        filter = ['enabled', 'disabled', 'cached', 'uncached']
    else:
        filter = [filter]

    # user output
    out_yaml(mods.list(filters=filter))


@mod.command()
@click.pass_context
@click.argument('mod_id')
def enable(ctx, mod_id):
    """Enable a mod"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)

    # Catch All
    if mod_id == 'all':
        mod_ids = mods.list(filters=['managed','disabled'])
    else:
        mod_ids = [mod_id]
    
    # Loop on each mods
    for mod_id in mod_ids:

        # Do action
        try:
            if ctx.obj['run']:
                mods.enable(mod_id)
            log.info('Mod %s has been enabled' % mod_id)
        except UserWarning as e:
            log.warn(e)

@mod.command()
@click.pass_context
@click.argument('mod_id')
def disable(ctx, mod_id):
    """Disable a mod"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)

    # Catch All
    if mod_id == 'all':
        mod_ids = mods.list(filters=['managed','enabled'])
    else:
        mod_ids = [mod_id]
    
    # Loop on each mods
    for mod_id in mod_ids:

        # Do action
        try:
            if ctx.obj['run']:
                mods.disable(mod_id)
            log.info('Mod %s has been disabled' % mod_id)
        except UserWarning as e:
            log.warn(e)


@mod.command()
@click.pass_context
@click.argument('mod_id')
def status(ctx, mod_id):
    """Show the status of a mod"""

    # Create mods object
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)
    
    # Do action
    try:
        out = { mod_id: mods.status(mod_id) }
        out_yaml( out )
    except Exception as e:
        log_except(e)


@mod.group(invoke_without_command=True)
@click.pass_context
def cache(ctx):
    """Cache a mod"""
    
    if ctx.invoked_subcommand is None:

        # Instanciate mod manager
        mods = Mods(dir_enabled=DIR_MOD_ENABLED,
                dir_local=DIR_MOD_CACHED)

        # User output
        log.info('Managed mods')
        out_yaml ( mods.list(filters=['managed']) )

    #else:
    #    click.echo('I am about to invoke %s' % ctx.invoked_subcommand)

@cache.command()
@click.pass_context
def managed(ctx):
    """List managed mods"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)
    out_yaml ( mods.list(filters=['managed']) )
    
@cache.command()
@click.pass_context
def unmanaged(ctx):
    """List unmanaged mods"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)
    out_yaml ( mods.list(filters=['unmanaged']) )
    

@cache.command()
@click.pass_context
@click.argument('mod_id')
def add(ctx, mod_id='all'):
    """Add a mod to cache"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)

    # Catch All
    if mod_id == 'all':
        mod_ids = mods.list(filters=['unmanaged'])
    else:
        mod_ids = [mod_id]

    # Loop over mods
    for mod_id in mod_ids:
        try:
            if ctx.obj['run']:
                mods.cache_add(mod_id)
            log.info('Mod %s is now managed' % mod_id)
        except Exception as e:
            log_except(e)


@cache.command()
@click.pass_context
@click.argument('mod_id')
def remove(ctx, mod_id='all'):
    """remove a mod to cache"""

    # Instanciate mod manager
    mods = Mods(dir_enabled=DIR_MOD_ENABLED,
            dir_local=DIR_MOD_CACHED)

    # Catch All
    if mod_id == 'all':
        mod_ids = mods.list(filters=['managed'])
    else:
        mod_ids = [mod_id]

    # Loop over mods
    for mod_id in mod_ids:
        try:
            if ctx.obj['run']:
                mods.cache_remove(mod_id)
            log.info('Mod %s is now unmanaged' % mod_id)
        except Exception as e:
            log_except(e)




# Script init
################################################################################

# Run main function
if __name__ == '__main__':

    # Run main piece of code
    cli()

