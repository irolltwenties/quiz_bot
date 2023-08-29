# Study Quiz Bot
 Telegram bot for some tests. 

<h2>Install</h2>
Make sure you got Python 3.8 or later version.
Go to terminal and to the script directory, create venv if needed:

```
pip install -r requirements.txt
```
And wait untill all libraries would be installed.

<h2>Setting up config</h2>

You <b>MUST</b> do this before first run, or script would not run properly.

First of all, you need to create config file with your token. Let's find this in <b>settings.py</b> script:

```
CONFIG_PATH = 'C:\myconfig\config_bot.ini'
```

You can insert your own CONFIG_PATH here.

Then, you got to search this function in <b>settings.py</b> script:

```
def create_config(config_path):
    config = configparser.ConfigParser()
    config.add_section('Main')
    config.set('Main', 'TOKEN', 'Your token goes here')
    config.set('Main', 'TEACHER_KEY', 'somepassword')
    with open(config_path, 'w') as config_file:
        config.write(config_file)
    return True
```

It's easy to guess, that here goes your bot token, and your teacher password:

```
config.set('Main', 'TOKEN', 'Your token goes here')
config.set('Main', 'TEACHER_KEY', 'somepassword')
```

<h2>Run script</h2>

After inserting your token and setting up your password, you can run <b>main.py</b> from it's directory:

```
python main.py
```

Don't forget to <b>delete your token and password from code after the first run:</b> keeping this info in code is bad. If the config is already created with proper data, you can easy change your token in code on any string.

<h3>First command</h3>

First command to bot from new user got to be /register. Insert your teacher password when bot asks you to.
<hr>
Other commands are:<br>
/help -- some additional info, may be updated<br>
/menu -- basic command for work with bot, availiable after using /register<br>

Have fun!
