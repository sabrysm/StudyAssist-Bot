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
- !study create <topic> <starting after> <duration>- Initiates a new study group session with a specific topic
- !study join <topic> - Joins an existing study group session on a specific topic
- !study leave <topic> - Leaves a study group session
- !study list - Lists all active study group sessions
- !study details <topic> - Displays details about a specific study group session
- !study end <topic> - Ends a study group session (only available to the creator)
- !study remind <topic> - Sends a reminder about an upcoming study group session
- !study resources <topic> - Shares study resources and materials related to a topic
- !study notify <message> - Sends a notification to all participants of a study group session

## Examples of Usage
- You can create a new study group session by typing `!study create Physics Session 1 5 5` notice that the last two parameters are the starting time and the duration of the session in minutes.
![Create](https://i.imgur.com/XwjyyYL.png)

- You can join an existing study group session by typing `!study join Physics Session 1`
![Join](https://i.imgur.com/zZdYb9U.png)

- You can leave a study group session by typing `!study leave Physics Session 1`

- You can list all active study group sessions by typing `!study list`

- You can get details about a specific study group session by typing `!study details Physics Session 1`

- You can end a study group session by typing `!study end Physics Session 1`
![End](https://i.imgur.com/5dSvHXb.png)

- You can set a reminder for an upcoming study group session by typing `!study remind Physics Session 1`
![Remind](https://i.imgur.com/UdNzsrd.png)

- You can share study resources and materials related to a topic by typing `!study resources Physics Session 1` (Only available to the session creator to share resources)
![Resources](https://i.imgur.com/oUVY3SP.png)