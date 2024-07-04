from discord.ext import commands
import discord
from utils import Topic, TimeCalculations, Utils, Reminder
from components import AddResourceView
import config
    
class Study(commands.Cog):
    """The description for Create goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.topic =  None
    
    @commands.group(name='study', invoke_without_command=False)
    async def study(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid study command. Please use `!study <command> <topic>` to create a new study session.', ephemeral=True)
    
    @study.command(name='create', description='Create a new study session')
    async def create(self, ctx: commands.Context, *args):
        topic_name, start_time, duration = Utils.parseCreateArgs(args)
        print(f"Topic: {topic_name}, Start Time: {start_time}, Duration: {duration}")
        # Check if the topic already exists
        topic_exists = await Topic.activeOrUpcomingTopicExists(topic_name)
        print(f"Topic Exists: {topic_exists}")
        if topic_exists:
            await ctx.send('There is already an active topic. Please join that topic or wait for it to end.')
            return
        author_has_active_or_upcoming_topic = await Topic.authorHasActiveOrUpcomingTopic(ctx.author.id)
        if author_has_active_or_upcoming_topic:
            await ctx.send('You cannot create a new topic because you have an active or upcoming topic.')
            return
        self.topic = Topic(topic_name, ctx.author.id, ctx.guild.id)
        
        if start_time:
            start_time = TimeCalculations.minutesToDateTime(int(start_time))
        if duration:
            duration = int(duration)
            
        await self.topic.insertTopicToDatabase(start_time, duration)
        topic_row = await self.topic.getActiveOrUpcomingTopicByName(topic_name)
        embed = await self.topic.createTopicEmbed(topic_row)
        await ctx.send(embed=embed)

    @create.error
    async def create_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Please provide a valid start time and duration.', ephemeral=True)
            print(error)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('You have an active topic. Please join that topic or wait for it to end.', ephemeral=True)
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
    
    @study.command(name='details', description='Get details of the current study session')
    async def details(self, ctx: commands.Context, *topic_name):
        topic_name = ' '.join(topic_name)
        print(f"Details for Topic: {topic_name}")
        topic_row = await Topic.getDetails(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        topic_embed = await Topic.createTopicEmbed(topic_row)
        await ctx.send(embed=topic_embed)
    
    @details.error
    async def details_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
    
    @study.command(name='join', description='Join the current study session')
    async def join(self, ctx: commands.Context, *topic_name):
        topic_name = ' '.join(topic_name)
        print(f"Joining Topic: {topic_name}")
        topic_row = await Topic.getActiveOrUpcomingTopicByName(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        user_joined = await Topic.checkIfAlreadyJoined(topic_name, ctx.author.id)
        if user_joined:
            await ctx.send('You have already joined the topic.', ephemeral=True)
            return
        is_author = await Topic.checkIfAuthor(topic_name, ctx.author.id)
        if is_author:
            await ctx.send('You are the author of the topic. You cannot join your own topic.', ephemeral=True)
            return
        await Topic.joinTopic(topic_name, ctx.author.id)
        topic_embed = await Topic.createTopicEmbed(topic_row)
        await ctx.send(embed=topic_embed)
    
    @join.error
    async def join_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
            
    @study.command(name='leave', description='Leave the current study session')
    async def leave(self, ctx: commands.Context, *topic_name):
        topic_name = ' '.join(topic_name)
        print(f"Leaving Topic: {topic_name}")
        topic_row = await Topic.getActiveOrUpcomingTopicByName(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        is_member = await Topic.checkIfAlreadyJoined(topic_name, ctx.author.id)
        if not is_member:
            await ctx.send('You are not a member of the topic.', ephemeral=True)
            return
        topic_author = await Topic.checkIfAuthor(topic_name, ctx.author.id)
        if topic_author:
            await ctx.send('You cannot leave your own topic because you are the author, but you can end it.', ephemeral=True)
            return
        await Topic.leaveTopic(topic_name, ctx.author.id)
        topic_embed = await Topic.createTopicEmbed(topic_row)
        await ctx.send(embed=topic_embed)
        
    @leave.error
    async def leave_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
            
    @study.command(name='end', description='End the current study session')
    async def end(self, ctx: commands.Context, *topic_name):
        topic_name = ' '.join(topic_name)
        print(f"Ending Topic: {topic_name}")
        topic_row = await Topic.getActiveOrUpcomingTopicByName(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        is_author = await Topic.checkIfAuthor(topic_name, ctx.author.id)
        if not is_author:
            await ctx.send('You are not the author of the topic. You cannot end the topic.', ephemeral=True)
            return
        await Topic.endTopic(topic_name, ctx.author.id)
        topic_embed = await Topic.createTopicEmbed(topic_row, end=True)
        await ctx.send(embed=topic_embed)
        topic_members = await Topic.getTopicMembers(topic_name)
        for member in topic_members:
            await Topic.removeTopicMember(topic_name, member[2])
        
    @end.error
    async def end_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
    
    @study.command(name='list', description='List all active study sessions')
    async def list(self, ctx: commands.Context):
        active_topics = await Topic.getActiveTopics()
        upcoming_topics = await Topic.getUpcomingTopics()
        topic_rows = active_topics + upcoming_topics
        if not topic_rows:
            await ctx.send('There are no active topics.', ephemeral=True)
            return
        embed = await Topic.createTopicsListEmbed(topic_rows)
        await ctx.send(embed=embed)
    
    @list.error
    async def list_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('There are no active topics.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
            
    @study.command(name='resources', description='Add resources to the current study session')
    async def resources(self, ctx: commands.Context, *args):
        topic_name = ' '.join(args)
        print(f"Adding Resources to Topic: {topic_name}")
        topic_row = await Topic.getActiveOrUpcomingTopicByName(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        is_member = await Topic.checkIfAlreadyJoined(topic_name, ctx.author.id)
        if not is_member:
            await ctx.send('You are not a member of the topic. Please join the topic to view resources.')
            return
        is_author = await Topic.checkIfAuthor(topic_name, ctx.author.id)
        view = AddResourceView(topic_name, ctx.author.id, topic_row[2])
        embed = await Topic.createTopicResourcesEmbed(topic_name)
        if is_author:
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)
    
    @resources.error
    async def resources_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
            
    @study.command(name='remind', description='Remind member of the current study session')
    async def remind(self, ctx: commands.Context, *topic_name):
        topic_name = ' '.join(topic_name)
        print(f"Reminding Members of Topic: {topic_name}")
        topic_row = await Topic.getActiveOrUpcomingTopicByName(topic_name)
        if not topic_row:
            await ctx.send('The topic does not exist.', ephemeral=True)
            return
        is_member = await Topic.checkIfAlreadyJoined(topic_name, ctx.author.id) or await Topic.checkIfAuthor(topic_name, ctx.author.id)
        if not is_member:
            await ctx.send('You are not a member of the topic. Please join the topic to receive reminders.')
            return
        has_started = await Topic.isTopicStarted(topic_name)
        if has_started:
            await ctx.send('The topic has already started.', ephemeral=True)
            return
        reminer_exists = await Reminder.reminderExists(ctx.author.id, topic_name)
        if reminer_exists:
            await ctx.send('You have already set a reminder for that topic.', ephemeral=True)
            return
        await Reminder.newReminder(ctx.author.id, topic_name)
        await ctx.send(f'Reminder is set for the topic: {topic_name}')
    
    @remind.error
    async def remind_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
            
    @study.command(name='notify', description='Notify members of the current study session')
    async def notify(self, ctx: commands.Context, *message):
        message = ' '.join(message)
        print(f"Notifying Members: {message}")
        topic_name = await Topic.getTopicNameByAuthor(ctx.author.id)
        if not topic_name:
            await ctx.send('You do not have an active topic.', ephemeral=True)
            return
        await Topic.notifyTopicMembers(self.bot, topic_name, message)
    
    @notify.error
    async def notify_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('You do not have an active topic.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
    
    
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Study(bot), guilds=[discord.Object(id=config.guild_id)])
