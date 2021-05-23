import discord
from discord.utils import get
from roles import MODERATION
from resources import CLOCK, TRAFFIC_LIGHTS
from logging import getLogger

LOGGER = getLogger('ai')


async def check_for_stoplights(message: discord.Message, message_copy=None):
    if CLOCK in message.content:
        LOGGER.info(f"{message.author.display_name} :: Moderators requested via clock emoji.")
        moderator_role = get(message.guild.roles, name=MODERATION)
        await message.channel.send(f"Moderators needed {moderator_role.mention}!")
        return True
    else:
        if any(traffic_light in message.content for traffic_light in TRAFFIC_LIGHTS):
            LOGGER.info(f"{message.author.display_name} :: Traffic light included in message. Halting message processing.")
            return True
        return False
