import os
import configparser


def create_config(config_path):
    # you can use it once to create token and delete from your code
    # having pure TOKEN inda code is bad
    config = configparser.ConfigParser()
    config.add_section('Main')
    config.set('Main', 'TOKEN', 'HERE GOES BOT TOKEN')
    config.set('Main', 'TEACHER_KEY', '8239872348ddj5suiSUhn723')
    with open(config_path, 'w') as config_file:
        config.write(config_file)
    return True


def load_teacher_key(config_path):
    if not os.path.exists(config_path):
        create_config(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    teacher_key = config.get('Main', 'TEACHER_KEY')
    return teacher_key


def load_token(config_path):
    if not os.path.exists(config_path):
        create_config(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    token = config.get('Main', 'TOKEN')
    return token


CONFIG_PATH = r'C:\myconfig\config_bot.ini'
TEACHER = load_teacher_key(CONFIG_PATH)
TOKEN = load_token(CONFIG_PATH)
