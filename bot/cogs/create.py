from discord.ext import commands
import discord
from utils import study
import config

class Create(commands.Cog):
    """The description for Create goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @study.command(name='create', help='Create a new study session')
    async def create(self, ctx: commands.Context, topic: str, start_time: str=None, duration: str=None):
        pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Create(bot), guilds=[discord.Object(id=config.guild_id)])
