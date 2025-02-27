import logging
import discord
import re
from db.drone_dao import is_drone
from discord.utils import get
from emoji import DRONE_EMOJI
LOGGER = logging.getLogger("ai")

banned_words = [r"t+h+i+n+k+", r"t+h+o+u+g+h+t+", r"m+o+r+n+i+n+g+"]


async def deny_thoughts(message: discord.Message, message_copy):

    if not is_drone(message.author):  # Associates are allowed to think.
        return

    emoji_replacement = get(message.guild.emojis, name=DRONE_EMOJI)

    LOGGER.info("Expunging all thoughts.")
    for banned_word in banned_words:
        for match in re.findall(banned_word, message_copy.content, flags=re.IGNORECASE):
            message_copy.content = message_copy.content.replace(match, "\_" * len(match), 1)

    message_copy.content = message_copy.content.replace("🤔", str(emoji_replacement))

    # Todo: Escape emoji names.
    # Todo: Don't include the \s if the "think" is inside a `code block`
