import sys
import os
import ConfigParser


def config_file_path():
    '''
    WARNING: This is an ugly hack. If you want dev-env on
    non-darwin systems, you have do some additional hacks.
    This is perfectly fine if you are developing on darwin
    and deploying on a linux2. Happy Hacking.
    '''
    dir_name = os.path.dirname(os.path.abspath(__file__))
    if sys.platform == 'darwin':
        conf_name = 'development.conf'
    else:
        conf_name = 'production.conf'
    return os.path.join(dir_name, conf_name)


def get_settings(filename=None):
    if not filename:
        filename = config_file_path()
    cfg = ConfigParser.RawConfigParser()
    with open(filename) as fp:
        cfg.readfp(fp)
    settings = {}
    for section in cfg.sections():
        settings[section] = {}
        for item in cfg.items(section):
            settings[section][item[0]] = item[1]
    return settings


def get_settings_prod():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    conf_name = 'production.conf'
    return get_settings(os.path.join(dir_name, conf_name))
