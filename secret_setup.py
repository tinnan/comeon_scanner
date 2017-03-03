from configparser import ConfigParser
from pathlib import Path

secret_path = './conf/secret.ini'
secret_file = Path(secret_path)
if secret_file.is_file():
    # File exists.
    print('Found secret configuration file. Please choose your next action.')
    conf = ConfigParser()
    conf.read(secret_path)

else:
    # File does not exist.
    config = {}

