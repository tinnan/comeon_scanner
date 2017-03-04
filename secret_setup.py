from configparser import ConfigParser
from pathlib import Path

secret_path = './conf/secret.ini'
secret_file = Path(secret_path)
config = ConfigParser()
cmd_state = None


def invalid_input():
    print('Invalid input. Try again.')


def is_valid_config(uin):
    if len(uin.strip()) == 0:
        return False
    elif uin.startswith('#'):
        return False
    return True


def save():
    with open(secret_path, 'w') as configfile:
        config.write(configfile)


def create_secret():
    if not config.has_section('secret'):
        config['secret'] = {}
    print("---------------------------------------------------------")  # program section separator.
    print("Creating new key-value pair.")
    print("Type in '#ret' to go back to action menu.")

    got_key = False
    while True:
        # Receiving key.
        key = input("Enter new key: ").strip()
        if key == '#ret':
            break
        elif is_valid_config(key):
            config['secret'][key] = ""
            got_key = True
            break
        else:
            invalid_input()

    if got_key:
        got_val = False
        # Get value if key is input.
        while True:
            # Receiving value.
            val = input("Input value for key [{}]: ".format(key)).strip()
            if val == '#ret':
                break
            elif is_valid_config(val):
                config['secret'][key] = val
                got_val = True
                break
            else:
                invalid_input()

        if not got_val:
            # If user did not input the value, presumably by typing in '#ret', clean up the empty key.
            config['secret'].pop(key)

    # Go back to waiting for next action.
    action()


def update_secret(key):
    curr_val = config['secret'][key]
    print("---------------------------------------------------------")  # program section separator.
    print("Updating key [{}], current value is [{}]".format(key, curr_val))
    print("Type in '#ret' to go back to action menu.")
    while True:
        new_val = input("Enter new value: ").strip()
        if new_val == '#ret':
            break
        elif is_valid_config(new_val):
            config['secret'][key] = new_val
            print("Value of key [{}] is updated to new value [{}].".format(key, new_val))
            print("Returning to action menu.")
            break
        else:
            invalid_input()

    # Go back to waiting for next action.
    action()


def end():
    while True:
        uin = input('Do you want to save the change? (y/n) ')
        if uin == 'y':
            save()
            # End program.
            exit(0)
        elif uin == 'n':
            # End program.
            exit(0)
        else:
            # Invalid input.
            invalid_input()


def action():

    if config.has_section('secret'):
        # If secret already exists in config object, list the next possible action.
        print("---------------------------------------------------------")  # program section separator.
        print("Please choose your next action...")
        print('add: Create new key-value.')
        print('quit: Create new key-value.')
        # List of valid actions.
        actions = ['add', 'quit']
        i = 1
        keys = [key for key in config['secret'].keys()]
        for k in keys:
            actions.append(str(i))
            print('{}: Edit value of ({})'.format(i, k))
            i += 1

        while True:
            uin = input('(action) ')
            if uin in actions:
                if uin == 'add':
                    create_secret()
                elif uin == 'quit':
                    end()
                else:
                    update_secret(keys[int(uin) - 1])
            else:
                invalid_input()

    else:
        # Go straight to creation process.
        create_secret()


print("""\
[Come-on scanner] Secret configuration file setup manager.
---------------------------------------------------------""")
if secret_file.is_file():
    # File exists.
    print('Found secret configuration file.')
    config.read(secret_path)
else:
    # File does not exist.
    print('Not found secret configuration file. Start creation procedure...')
action()
