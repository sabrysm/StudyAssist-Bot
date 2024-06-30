# StudyAssist-Bot
StudyAssis is a Discord bot designed to facilitate virtual study groups within Discord servers. It provides tools for creating, managing, and enhancing study sessions, fostering collaborative learning environments.

## Installation
- Setup the bot in Discord Developer portal: https://discord.com/developers/applications
- Copy the token and paste it in `config.py`
- Install the dependencies
```bash
 > Windows
 ===========
 py -m pip install -r requirements.txt

 Linux/Mac
 ===========
 python3 -m pip install -r requirements.txt
 ```
 - cd bot/
 - run the bot: `python3 -m bot.py`

 ## Commands
- !study create <topic> - Initiates a new study group session with a specific topic
- !study join <topic> - Joins an existing study group session on a specific topic
- !study leave <topic> - Leaves a study group session
- !study list - Lists all active study group sessions
- !study details <topic> - Displays details about a specific study group session
- !study end <topic> - Ends a study group session (only available to the creator)
- !study remind <topic> - Sends a reminder about an upcoming study group session
- !study resources <topic> - Shares study resources and materials related to a topic
- !study notify <message> - Sends a notification to all participants of a study group session
