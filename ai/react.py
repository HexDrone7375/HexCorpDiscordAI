import re
import discord
from discord.utils import get
from logging import getLogger

PATTERN_REACTS = {
    r'^(\d{4}) :: Code `109` :: .*': 'gooddrone'
}

LOGGER = getLogger('ai')


async def parse_for_reactions(message: discord.Message, message_copy=None) -> bool:
    '''
    Look for patterns and react with an emote if one matches.
    '''
    for (pattern, emote_name) in PATTERN_REACTS.items():
        if re.match(pattern, message.content):
            LOGGER.info(f"Hive Mxtress AI :: Reacting to {message.author.display_name}'s message with :{emote_name}:")
            await message.add_reaction(get(message.guild.emojis, name=emote_name))

    return False
