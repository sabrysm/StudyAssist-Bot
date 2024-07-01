import discord
from discord.ext import commands
from discord.app_commands import Group
import aiosqlite
from datetime import datetime


study = Group(name='study', description='Study commands')

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

class Topic:
    def __init__(self, name, description, author_id, guild_id):
        self.name = name
        self.description = description
        self.author_id = author_id
        self.guild_id = guild_id
    
    @staticmethod
    async def createTablesIfNotExists():
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    start_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    author_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS topic_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()


    async def insertTopicToDatabase(self):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO topics (name, description, author_id, guild_id)
                VALUES (?, ?, ?, ?)
            ''', (self.name, self.description, self.author_id, self.guild_id))
            await db.commit()
            
            
    @staticmethod
    async def getTopics():
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics
            ''') as cursor:
                return await cursor.fetchall()
            
    @staticmethod
    async def joinTopic(topic_name, user_id):
        async with aiosqlite.connect('study.db') as db:
            await db.execute('''
                INSERT INTO topic_members (topic_name, user_id)
                VALUES (?, ?)
            ''', (topic_name, user_id))
            await db.commit()
    
    @staticmethod
    async def getTopicMembers(topic_name):
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topic_members WHERE topic_name=?
            ''', (topic_name,)) as cursor:
                return await cursor.fetchall()
    
    @staticmethod
    async def getTopicByName(name):
        async with aiosqlite.connect('study.db') as db:
            async with db.execute('''
                SELECT * FROM topics WHERE name=?
            ''', (name,)) as cursor:
                return await cursor.fetchone()
    
    @staticmethod
    async def createTopicEmbed(topic: aiosqlite.Row):
        embed = discord.Embed(title=topic['name'], description=topic['description'], color=discord.Color.green())
        members = await Topic.getTopicMembers(topic['name'])
        embed.add_field(name="Host", value=f"<@{topic['author_id']}>")
        embed.add_field(name="Members", value="\n".join([f"<@{member['user_id']}>" for member in members]))
        embed.set_footer(text=f"Created by {topic['author_id']}")
        return embed
    
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