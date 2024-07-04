import discord
from discord.ext import commands
from discord.app_commands import Group
import aiosqlite
from datetime import datetime, timedelta
from typing import List
import pytz
import config

class Resource:
    @staticmethod
    async def createTableIfNotExists():
        async with aiosqlite.connect('study.db') as db:
                # foreign key to the topics table's status column
            await db.execute('''CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name INTEGER,
                author_id INTEGER,
                status TEXT,
                url TEXT NOT NULL,
                FOREIGN KEY (topic_name) REFERENCES topics(name),
                FOREIGN KEY (author_id) REFERENCES topics(author_id),
                FOREIGN KEY (status) REFERENCES topics(status)
            );''')
            await db.commit()
    
    @staticmethod
    async def addResource(topic_name: str, author_id: int, status: str, url: str):
        await Resource.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''INSERT INTO resources (topic_name, author_id, status, url) VALUES (?, ?, ?, ?);''', (topic_name, author_id, status, url))
            await db.commit()
    
    @staticmethod
    async def getResources(topic_name: str):
        await Resource.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''SELECT * FROM resources WHERE topic_name=? AND (status='active' OR status='upcoming');''', (topic_name,)) as cursor:
                return await cursor.fetchall()
    

class TimeCalculations:
    @staticmethod
    def timeDifference(start_time: datetime, current_time: datetime) -> int:
        """
        Calculate the difference between two datetime objects
        
        Parameters:
            start_time (datetime): The start time
            current_time (datetime): The current time
            
        Returns:
            int: The difference in seconds
        """
        return int((current_time - start_time).total_seconds())

    @staticmethod
    def minutesToText(minutes: int) -> str:
        """
        Convert minutes to hours and minutes
        
        Parameters:
            minutes (int): The number of minutes
            
        Returns:
            str: The time in hours and minutes
        """
        hours = minutes // 60
        minutes = minutes % 60
        return f'{hours} hours {minutes} minutes' if hours > 0 else f'{minutes} minutes'
    
    @staticmethod
    def minutesToDateTime(minutes: int) -> datetime:
        """
        Convert minutes to datetime
        
        Parameters:
            minutes (int): The number of minutes
            
        Returns:
            datetime: The datetime object
        """
        return discord.utils.utcnow() + timedelta(minutes=minutes)
    
    @staticmethod
    def remainingTime(start_time: str, current_time: str) -> int:
        """
        Calculate the remaining time between the start time and the current time
        
        Parameters:
            start_time (str): The start time
            current_time (str): The current time
            
        Returns:
            int: The remaining time in minutes
        """
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        return int((start_time - current_time).total_seconds() // 60)
    
    @staticmethod
    async def datetimeToSeconds(datetime_str: str) -> int:
        """
        Convert a datetime string to seconds
        
        Parameters:
            datetime_str (str): The datetime string
            
        Returns:
            int: The seconds
        """
        return int((datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S') - datetime.strptime(discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')).total_seconds())

class Topic:
    def __init__(self, name, author_id, guild_id):
        self.name = name
        self.author_id = author_id
        self.guild_id = guild_id

    async def insertTopicToDatabase(self, start_time: datetime=None, duration: int=0):
        current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        start_time = start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else current_time
        print(f"Start time: {start_time}, Current time: {current_time}")
        status = 'active' if start_time <= current_time else 'upcoming'
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO topics (name, status, start_time, duration, author_id, guild_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.name, status, start_time, duration, self.author_id, self.guild_id))
            await db.commit()

    @staticmethod
    async def createTablesIfNotExists():
        """
        Create the tables if they do not exist
        """
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'upcoming',
                    start_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    duration INTEGER NOT NULL DEFAULT 0,
                    author_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS topic_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
    
    @staticmethod
    async def getActiveTopics():
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE status='active'
            ''') as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def getUpcomingTopics():
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE status='upcoming'
            ''') as cursor:
                return await cursor.fetchall()
        
    @staticmethod
    async def getTopics():
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics
            ''') as cursor:
                return await cursor.fetchall()
            
    @staticmethod
    async def joinTopic(topic_name, user_id):
        await Topic.createTablesIfNotExists()
        await Topic.insertTopicMember(topic_name, user_id)
    
    @staticmethod
    async def checkIfAlreadyJoined(topic_name, user_id):
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topic_members WHERE topic_name=? AND user_id=?
            ''', (topic_name, user_id)) as cursor:
                return await cursor.fetchone() is not None
    
    @staticmethod
    async def checkIfAuthor(topic_name, author_id):
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE name=? AND author_id=? AND (status='active' OR status='upcoming')
            ''', (topic_name, author_id)) as cursor:
                return await cursor.fetchone() is not None
    
    @staticmethod
    async def insertTopicMember(topic_name, user_id):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO topic_members (topic_name, user_id)
                VALUES (?, ?)
            ''', (topic_name, user_id))
            await db.commit()
    
    @staticmethod
    async def removeTopicMember(topic_name, user_id):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                DELETE FROM topic_members
                WHERE topic_name=? AND user_id=?
            ''', (topic_name, user_id))
            await db.commit()
    
    @staticmethod
    async def getTopicMembers(topic_name) -> List[aiosqlite.Row]:
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topic_members WHERE topic_name=?
            ''', (topic_name,)) as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def getTopicByName(topic_name: str) -> aiosqlite.Row:
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE name=?
            ''', (topic_name,)) as cursor:
                return await cursor.fetchone()
    
    @staticmethod
    async def activeOrUpcomingTopicExists(topic_name: str) -> bool:
        await Topic.createTablesIfNotExists()
        return await Topic.getActiveOrUpcomingTopicByName(topic_name) is not None
    
    @staticmethod
    async def getActiveOrUpcomingTopicByName(topic_name: str) -> aiosqlite.Row:
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE name=? AND (status='active' OR status='upcoming')
            ''', (topic_name,)) as cursor:
                return await cursor.fetchone()
    
    @staticmethod
    async def endTopic(topic_name: str, author_id: int):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                UPDATE topics
                SET status='ended'
                WHERE name=? AND author_id=? AND (status='active' OR status='upcoming')
            ''', (topic_name, author_id))
            await db.commit()
    
    @staticmethod
    async def isTopicStarted(topic_name: str) -> bool:
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT status FROM topics WHERE name=? ORDER BY id DESC LIMIT 1
            ''', (topic_name,)) as cursor:
                topic = await cursor.fetchone()
                return topic[0] == 'active'
    
    @staticmethod
    async def isTopicEnded(topic_name: str) -> bool:
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT status FROM topics WHERE name=?
            ''', (topic_name,)) as cursor:
                topic = await cursor.fetchone()
                return topic[0] == 'ended'
    
    @staticmethod
    async def createTopicEmbed(topic: aiosqlite.Row, end=False):
        print(topic)
        embed = discord.Embed(title=f"Session:\n{topic[1]}", color=discord.Color.green() if not end else discord.Color.dark_orange())
        members = await Topic.getTopicMembers(topic[1])
        topic_started = await Topic.isTopicStarted(topic[1])
        start_time = topic[3]
        start_time_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        start_time_dt_utc = start_time_dt.replace(tzinfo=pytz.utc)
        time_remaining = discord.utils.format_dt(start_time_dt_utc, 'R')
        time_since_end = discord.utils.format_dt(discord.utils.utcnow(), 'R')
        status = 'Starting' if not topic_started else 'Started'
        status = 'Ended by author' if end else status
        if topic_started:
            embed.add_field(name="Status", value="Active", inline=False)
        else:
            embed.add_field(name=f"Status", value=f"{status} {time_remaining if not end else time_since_end}", inline=False)
        if topic[4] > 0:
            embed.add_field(name="Duration", value=TimeCalculations.minutesToText(topic[4]), inline=False)
        embed.add_field(name="Host", value=f"<@{topic[5]}>", inline=False)
        if len(members) > 0:
            embed.add_field(name="Members", value="\n".join([f"<@{member[2]}>" for member in members]), inline=False)
        else:
            embed.add_field(name="Members", value="No members joined yet", inline=False)
        embed.add_field(name="** **", value=f"Start time: {discord.utils.format_dt(start_time_dt_utc, 'f')} in your timezone", inline=False)
        return embed
    
    @staticmethod
    async def createTopicsListEmbed(topics: List[aiosqlite.Row], title="Topics"):
        embed = discord.Embed(title=title, color=discord.Color.green())
        for topic in topics:
            start_time = topic[3]
            start_time_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            start_time_dt_utc = start_time_dt.replace(tzinfo=pytz.utc)
            time_remaining = discord.utils.format_dt(start_time_dt_utc, 'R')
            status = 'Starting' if topic[2] == 'upcoming' else 'Started'
            embed.add_field(name=topic[1], value=f"- **Host:** <@{topic[5]}>\n- **Status:** {status} {time_remaining}", inline=False)
        return embed
    
    @staticmethod
    async def startTopic(topic_name: str, author_id: int):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                UPDATE topics
                SET status='active'
                WHERE name=? AND author_id=? AND status='upcoming'
            ''', (topic_name, author_id))
            await db.commit()
    
    @staticmethod
    async def getDetails(topic_name: str):
        await Topic.createTablesIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE name=? AND (status='active' OR status='upcoming')
            ''', (topic_name,)) as cursor:
                return await cursor.fetchone()
    
    @staticmethod
    async def leaveTopic(topic_name: str, user_id: int):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                DELETE FROM topic_members
                WHERE topic_name=? AND user_id=?
            ''', (topic_name, user_id))
            await db.commit()
    
    @staticmethod
    async def createTopicResourcesEmbed(topic_name: str):
        resources = await Resource.getResources(topic_name)
        resources = [resource for resource in resources if resource[3] == 'active' or resource[3] == 'upcoming']
        embed = discord.Embed(title=f"Resources for {topic_name}", color=discord.Color.green())
        if len(resources) == 0:
            embed.description = "No resources found for this topic"
        else:
            for resource in resources:
                embed.add_field(name=f"** **", value=f"- [Resource {resources.index(resource) + 1}]({resource[4]})", inline=False)
        return embed

    @staticmethod
    async def authorHasActiveOrUpcomingTopic(author_id: int) -> bool:
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE author_id=? AND (status='active' OR status='upcoming')
            ''', (author_id,)) as cursor:
                return await cursor.fetchone() is not None

class Reminder:
    @staticmethod
    async def createTableIfNotExists():
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    FOREIGN KEY (topic_name) REFERENCES topics(name)
                )
            ''')
            await db.commit()
    
    @staticmethod
    async def newReminder(user_id: int, topic_name: str):
        await Reminder.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO reminders (user_id, topic_name)
                VALUES (?, ?)
            ''', (user_id, topic_name))
            await db.commit()
    
    @staticmethod
    async def createReminder(user_id: int, topic_name: str):
        await Reminder.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO reminders (user_id, topic_name)
                VALUES (?, ?)
            ''', (user_id, topic_name))
            await db.commit()
    
    @staticmethod
    async def sendReminder(bot: discord.Client, user_id: int, topic_name: str):
        await Reminder.createTableIfNotExists()
        member = bot.get_guild(config.guild_id).get_member(user_id)
        await member.send(f"Reminder: The topic {topic_name} is starting now!")
    
    @staticmethod
    async def notifyTopicMembers(bot: discord.Client, topic_name: str, message: str):
        members = await Topic.getTopicMembers(topic_name)
        for member in members:
            member = bot.get_guild(config.guild_id).get_member(member[2])
            await member.send(message)
    
    @staticmethod
    async def getReminders():
        await Reminder.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM reminders
            ''') as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def deleteReminder(user_id: int, topic_name: str):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                DELETE FROM reminders
                WHERE user_id=? AND topic_name=?
            ''', (user_id, topic_name))
            await db.commit()
    
    @staticmethod
    async def getRemindersByUser(user_id: int):
        await Reminder.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM reminders WHERE user_id=?
            ''', (user_id,)) as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def getRemindersByTopic(topic_name: str):
        await Reminder.createTableIfNotExists()
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM reminders WHERE topic_name=?
            ''', (topic_name,)) as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def deleteRemindersByTopic(topic_name: str):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                DELETE FROM reminders
                WHERE topic_name=?
            ''', (topic_name,))
            await db.commit()
    
    @staticmethod
    async def reminderExists(user_id: int, topic_name: str):
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM reminders WHERE user_id=? AND topic_name=?
            ''', (user_id, topic_name)) as cursor:
                return await cursor.fetchone() is not None

class Check:
    @staticmethod
    async def checkStartTimes(bot: commands.Bot):
        """
        Check the starting times for upcoming topics
        
        Parameters:
            bot (commands.Bot): The bot instance
            
        Returns:
            None
        """
        upcoming_topics = await Topic.getUpcomingTopics()
        for topic in upcoming_topics:
            start_time = topic[3]
            current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            if start_time <= current_time:
                print(f"Starting topic: {topic[1]}")
                await Topic.startTopic(topic[1], topic[5])
                reminders = await Reminder.getRemindersByTopic(topic[1])
                for reminder in reminders:
                    await Reminder.sendReminder(bot, reminder[1], reminder[2])
                await Reminder.deleteRemindersByTopic(topic[1])
    
    @staticmethod
    async def checkEndTimes():
        """
        Check the ending times for active topics
        
        Parameters:
            bot (commands.Bot): The bot instance
            
        Returns:
            None
        """
        active_topics = await Topic.getActiveTopics()
        for topic in active_topics:
            start_time = topic[3]
            duration = topic[4]
            if duration == 0:
                continue
            current_time = discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            # Check if the duration has passed
            if TimeCalculations.timeDifference(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'), datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')) >= duration * 60:
                topic_name = topic[1]
                print(f"Ending topic: {topic_name}")
                await Topic.endTopic(topic_name, topic[5])
                topic_members = await Topic.getTopicMembers(topic_name)
                for member in topic_members:
                    await Topic.removeTopicMember(topic_name, member[2])

class Utils:
    @staticmethod
    def parseCreateArgs(args):
        """
        Parse the arguments for the create command
        
        Parameters:
            args (tuple): The arguments
            
        Returns:
            tuple: The topic name, start time, and duration
        """
        numbers = [arg for arg in args if arg.isdigit()]
        topic_name = "".join([arg + " " for arg in args if not arg.isdigit()]).strip()
        topic_name = topic_name + "".join([f" {num}" for num in numbers[:-2]])
        args = [topic_name] + [int(num) for num in numbers[-2:]] if numbers else [topic_name, 0, 0]
        start_time = numbers[-2] if len(numbers) > 0 else 0
        duration = numbers[-1] if len(numbers) > 1 else 0
        return topic_name, start_time, duration

class Attendance:
    @staticmethod
    async def createTableIfNotExists():
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS attendances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    FOREIGN KEY (topic_name) REFERENCES topics(name),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    attended_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    time_spent INTEGER NOT NULL DEFAULT 0
                )
            ''')
            await db.commit()
    
    @staticmethod
    async def createAttendance(topic_name, user_id, time_spent=0):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO attendances (topic_name, user_id, time_spent)
                VALUES (?, ?, ?)
            ''', (topic_name, user_id, time_spent))
            await db.commit()
            
    @staticmethod
    async def getAttendances():
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM attendances
            ''') as cursor:
                return await cursor.fetchall()
    
    