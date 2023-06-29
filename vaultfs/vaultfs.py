import argparse
import sys
from fuse import FUSE
import ast
from vaultfs.logger import VaultfsLogger
# from logger import VaultfsLogger
import vaultfs
from vaultfs.vault_fuse import vault_fuse
from vaultfs.vault_api import check_remote, check_folder, check_file
# from vault_fuse import vault_fuse
# from vault_api import check_remote, check_folder, check_file
from pathlib import Path
from appdirs import user_config_dir
from configparser import ConfigParser
# from configparser import ConfigParser, NoOptionError
from textwrap import dedent


# setting logger.
log = VaultfsLogger()

config_path = Path(user_config_dir(appname="vaultfs", appauthor="timpoclast")) / "config.ini"


def vaultfs(mountpoint, local, remote, payload, secrets_path, timeout):
    vf = vault_fuse(local, remote, payload, secrets_path,
                    recheck_timestamp=604800)

    FUSE(vf, mountpoint, nothreads=True, foreground=True)

    pass


def load_file_config():
    config = ConfigParser()

    if config_path.exists():
        config.read(config_path)
    else:
        config_path.parent.mkdir(exist_ok=True, parents=True)
        config['main'] = {'timeout':  5 }
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    config.read(config_path)
    
    file_config = dict(config.items('main'))

    return file_config


def main():
    # FIXME: add a timeout parameter
    # FIXME: add a data_content parameter

    parser = argparse.ArgumentParser(
        description='Vault fuse file system',
        epilog='Note: arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing')

    parser.add_argument('-c', '--config', dest='config', help='Configuration file.')
    parser.add_argument('-m', '--mountpoint', dest='mountpoint', help='where the fuse filesystem will be mounted. E.g. /mtn/vaultfs')
    parser.add_argument('-l', '--local', dest='local', help='credentials local path after being pulled from vault. E.g. ')
    parser.add_argument('-r', '--remote', dest='remote', help='Vault Server HTTPS address. E.g. https://localhost:8200')
    parser.add_argument('-s', '--secrets-path', dest='secrets_path',   action='append', help='List of secrets path in the Vault server.')
    parser.add_argument('-p', '--payload', dest='payload',   help='.Vault authentication token. E.g. $(cat $HOME/.vault-token)')


    cli_config = vars(parser.parse_args())
    
    config = load_file_config()

    del cli_config['config']

    config.update(cli_config)

    missing_config = [ entry for entry in iter(config) if config[entry] == None and entry != 'config' ]

    if missing_config:
        parser.error(f"Please specify {missing_config.join(', ')} at command line or in {config_path}")

    # initial formatting and checks
    config['remote'] = config['remote'].rstrip('/')
    config['payload'] = Path(config['payload'])

    check_remote(config['remote'])
    check_folder(config['local'])
    check_folder(config['mountpoint'])
    check_file(config['payload'])
    print("success")

    vaultfs(**config)


if __name__ == '__main__':
    main()
