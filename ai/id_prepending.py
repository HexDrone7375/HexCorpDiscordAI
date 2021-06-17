from channels import HEXCORP_CONTROL_TOWER_CATEGORY, MODERATION_CATEGORY
import discord
from db.drone_dao import is_prepending_id
import bot_utils
import ai.logging as LOGGER
from bot_utils import COMMAND_PREFIX


async def check_if_prepending_necessary(message: discord.Message, message_copy=None):
    if is_prepending_id(message.author) and message.channel.category.name not in [HEXCORP_CONTROL_TOWER_CATEGORY, MODERATION_CATEGORY]:
        drone_id = bot_utils.get_id(message.author.display_name)
        if message.content.startswith(f"{drone_id} :: ") or message.content.startswith(COMMAND_PREFIX):
            return False
        else:
            LOGGER.info("Drone did not ID prepend when required.", message)
            await message.delete()
            LOGGER.info("Message deleted.", message)
            return True
    else:
        return False
