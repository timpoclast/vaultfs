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

# setting logger.
log = VaultfsLogger()


def vaultfs(mountpoint, local, remote, payload, secrets_path):
    FUSE(vault_fuse(local, remote, payload, secrets_path, recheck_timestamp=604800), mountpoint, nothreads=True,
         foreground=True)


def load_config():
    # .ini is easiest to work with, but .toml is probably better in the long run
    cfg_loc = Path(user_config_dir(appname="vaultfs",
                   appauthor="timpoclast")) / "config.ini"
    # that's it, that was the magic. the rest of the code here is just for illustration

    if not cfg_loc.exists():
        cfg_loc.parent.mkdir(parents=True, exist_ok=True)

        # TODO: replace with a file copy from.. data_files?
        with open(config_loc) as f:
            f.write(
                "[basic]\n"
                "foo = 1\n"
            )
        print(f"Initialized new default config at {config_loc}.")

    cfg = ConfigParser()
    cfg.read(cfg_loc)
    return cfg


def main():
    # FIXME: add a timeout parameter
    # FIXME: add a data_content parameter

    parser = argparse.ArgumentParser(
        description='Vault fuse file system',
        epilog='Note: arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing')

    parser.add_argument('-c', '--config', dest='config',
                        metavar='', required=False, help='Configuration file.')
    parser.add_argument('-m', '--mountpoint', dest='mountpoint', metavar='',
                        required=False, help='where the fuse filesystem will be mounted.')
    parser.add_argument('-l', '--local', dest='local', metavar='', required=False,
                        help='credentials local path after being pulled from vault.')
    parser.add_argument('-r', '--remote', dest='remote', metavar='',
                        required=False, help='Vault Server HTTPS address.')
    parser.add_argument('-s', '--secrets-path', dest='secrets_path', metavar='', required=False,
                        action='append', help='List of secrets path in the Vault server.')
    parser.add_argument('-p', '--payload', dest='payload', metavar='', required=False,
                        help='.Vault authentication token')

    args = parser.parse_args()
    if not args.config and (args.mountpoint is None or args.local is None or args.payload is None or args.remote is None or args.secrets_path is None):
        parser.error(
            'arguments: "--mountpoint", "--local", "--remote", "--secetes-path" and "--payload" are required when "--config" is missing')

    if args.config:
        load_config()

    else:
        mountpoint = args.mountpoint
        local = args.local
        remote = args.remote.rstrip('/')
        secrets_path = args.secrets_path
        payload = args.payload

    # initial checks
    check_remote(remote)
    check_folder(local)
    check_folder(mountpoint)
    check_file(payload)
    print("success")

    vaultfs(mountpoint, local, remote,  payload, secrets_path)


if __name__ == '__main__':

    main()
