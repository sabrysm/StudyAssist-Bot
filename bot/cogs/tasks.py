from discord.ext import commands, tasks
import discord
from utils import Check
import config


class Tasks(commands.Cog):
    """The description for Tasks goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_start_times.start()
        self.check_end_times.start()
    
    @tasks.loop(seconds=config.check_start_times_interval)
    async def check_start_times(self):
        await Check.checkStartTimes(self.bot)
    
    @tasks.loop(seconds=config.check_end_times_interval)
    async def check_end_times(self):
        await Check.checkEndTimes()

async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot), guilds=[discord.Object(id=config.guild_id)])
