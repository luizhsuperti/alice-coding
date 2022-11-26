import logging
import sys


def check_integrity(key, var_type):

    def _namestr(obj, namespace):
        return [name for name in namespace if namespace[name] is obj]

    if not isinstance(key, var_type):
        logging.error('The config file is corrupted in {} key!'.format(
            _namestr, globals()))
        sys.exit(1)