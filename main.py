from configparser import ConfigParser, ExtendedInterpolation
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'conf')


def get_environ_param():
    """
    Get execution environment from system param 'COMEON_ENV'.
    :return: execution environment
    """
    return os.environ.get('COMEON_ENV')

# Simplified configuration dict.
# Contains only key-value, no need to specify section as sections are union together.
# Key-values from 'app' section are loaded first and they will be replaced by the same key-values
# from other section(depends on execution environment.
CONFIG = None
try:
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    parser.read(os.path.join(CONFIG_DIR, 'application.ini'))
    CONFIG = parser['app']
    # Get OS environment for execution environment, which will be set in .BAT file.
    env_param = get_environ_param()
    if env_param is not None:
        env_section = parser[env_param]
        # Iterate through all config in the environment section.
        for e in list(enumerate(env_section)):
            key = e[1]
            value = env_section[key]
            CONFIG[key] = value  # Existing value will be replaced.
except:
    print('Application configuration file read failed.')
    exit(1)

# Secret configuration.
SECRET_CONFIG = ConfigParser()
try:
    SECRET_CONFIG.read(os.path.join(CONFIG_DIR, 'secret.ini'))
except:
    print('Secret configuration file read failed. Make sure to run secret_setup.bat before starting the application.')
    exit(1)

from src.scan import scanner
from src.cloud import mail

if __name__ == "__main__":
    """
    Start the scanner.
    """
    # TODO logging
    # Load follow list
    f = scanner.load_follow_list()
    if f is None:
        exit(0)
    # Load history
    h = scanner.History(scanner.load_history())
    # Scanner object
    s = scanner.Scanner()
    # Execute scan and get notifications in return
    n = s.scan(f, h)
    if len(n) != 0:
        # have something to notify
        mail.send_notification(n)
    # write history to file
    scanner.write_history(h.get_history())
