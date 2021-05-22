import logging
import discord
from channels import DRONE_HIVE_CHANNELS, HEXCORP_CONTROL_TOWER_CATEGORY, MODERATION_CATEGORY
from resources import DRONE_AVATAR
from db.drone_dao import is_identity_enforced, is_drone

LOGGER = logging.getLogger('ai')


async def enforce_identity(message: discord.Message, message_copy):
    if identity_enforcable(message.author, channel=message.channel):
        LOGGER.info(f"{message.author.display_name} :: Identity enforcable. Updating message copy.")
        message_copy.avatar_url = DRONE_AVATAR
        return False
    LOGGER.info(f"{message.author.display_name} :: User does not have enforcable identity.")
    return False


def identity_enforcable(member: discord.Member, channel):
    '''
    Takes a channel object and uses it to check if the identity of a user should be enforced.
    '''

    if is_drone(member) and (channel.name in DRONE_HIVE_CHANNELS or is_identity_enforced(member)) and channel.category.name not in [HEXCORP_CONTROL_TOWER_CATEGORY, MODERATION_CATEGORY]:
        LOGGER.info(f"{member.display_name} :: Identity is enforcable.")
        return True
    else:
        LOGGER.info(f"{member.display_name} :: Identity is not enforcable.")
        return False
