from configparser import ConfigParser, ExtendedInterpolation
import os
import logging


def get_environ_param():
    """
    Get execution environment from system param 'COMEON_ENV'.
    :return: execution environment
    """
    return os.environ.get('COMEON_ENV')

# Setup logging
logger = logging.getLogger('src')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if get_environ_param() == 'prod':
    fh = logging.FileHandler('scan.log')  # Log to file handler
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

sh = logging.StreamHandler()  # Log to console handler
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(sh)

# Setup constants for project directory path
logger.debug('Setting constant for project root path...')
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
logger.debug('Set constant PROJECT_ROOT = %s', PROJECT_ROOT)

logger.debug('Setting constant for configuration directory path...')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'conf')
logger.debug('Set constant CONFIG_DIR = %s', CONFIG_DIR)

# Simplified configuration dict.
# Contains only key-value, no need to specify section as sections are union together.
# Key-values from 'app' section are loaded first and they will be replaced by the same key-values
# from other section(depends on execution environment.
CONFIG = None
try:
    logger.debug('Initializing application configuration...')
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    config_path = os.path.join(CONFIG_DIR, 'application.ini')
    logger.debug('Reading configuration from %s', config_path)
    parser.read(config_path)
    CONFIG = parser['app']
    # Get OS environment for execution environment, which will be set in .BAT file.
    env_param = get_environ_param()
    if env_param is not None:
        logger.debug('Reading and overwrite configuration for environment: %s', env_param)
        env_section = parser[env_param]
        # Iterate through all config in the environment section.
        for e in list(enumerate(env_section)):
            key = e[1]
            value = env_section[key]
            CONFIG[key] = value  # Existing value will be replaced.
    logger.debug('Initializing application configuration completed.')
    for key in CONFIG:
        logger.debug('CONFIG[%s] = %s', key, CONFIG[key])
except Exception as e:
    logger.exception('Application configuration file read failed.', e)
    exit(1)

# Secret configuration.
SECRET_CONFIG = ConfigParser()
try:
    logger.debug('Initializing application secret configuration...')
    SECRET_CONFIG.read(os.path.join(CONFIG_DIR, 'secret.ini'))
    logger.debug('Initializing application secret configuration completed.')
except Exception as e:
    logger.exception('Secret configuration file read failed. '
                     'Make sure to run secret_setup.bat before starting the application.')
    exit(1)

from src.scan import scanner
from src.cloud import mail

if __name__ == "__main__":
    """
    Start the scanner.
    """
    logger.info('Starting followed fiction thread scanner...')
    # Load follow list
    f = scanner.load_follow_list()
    if f is not None:
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
    logger.info('Scanning process ended.')