from discord.ext import commands
import discord
from utils import Topic, TimeCalculations, Utils
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
        await Topic.endTopic(topic_name, ctx.author.id)
        topic_embed = await Topic.createTopicEmbed(topic_row, end=True)
        await ctx.send(embed=topic_embed)
        
    @end.error
    async def end_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please provide a topic name.', ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('The topic does not exist.', ephemeral=True)
            raise error
        else:
            await ctx.send('An error occurred. Please try again.', ephemeral=True)
    
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Study(bot), guilds=[discord.Object(id=config.guild_id)])
