from configparser import ConfigParser, ExtendedInterpolation
import os
import logging
import logging.handlers

APP_SYSTEM_ENV = 'COMEON_ENV'  # Name of environment variable for application execution

# Setup logger
logger = logging.getLogger('src')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

logger.debug('Setting constant for log directory path...')
LOG_DIR = os.path.join(PROJECT_ROOT, 'log')
logger.debug('Set constant LOG_DIR = %s', LOG_DIR)

logger.debug('Setting constant for log file name...')
LOG_FILENAME = os.path.join(LOG_DIR, 'scan.log')
logger.debug('Set constant LOG_FILENAME = %s', LOG_FILENAME)

# Setup log file rotation
if os.environ.get(APP_SYSTEM_ENV) == 'prod':
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    need_roll = os.path.isfile(LOG_FILENAME)
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=48)  # Log to file handler
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    if need_roll:  # Do roll over to new file if log exists
        fh.doRollover()
    logger.addHandler(fh)

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
    env_param = os.environ.get(APP_SYSTEM_ENV)
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
                     'Make sure to run secret_setup.bat before starting the application.', e)
    exit(1)
