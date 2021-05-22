from db.drone_dao import is_optimized
from ai.speech_optimization import get_status_type, StatusType
from channels import ORDERS_REPORTING, ORDERS_COMPLETION, MODERATION_CHANNEL, MODERATION_LOG, MODERATION_CATEGORY, REPETITIONS
from ai.mantras import Mantra_Handler
from bot_utils import get_id
import logging

CHANNEL_BLACKLIST = [ORDERS_REPORTING, ORDERS_COMPLETION, MODERATION_CHANNEL, MODERATION_LOG]
CATEGORY_BLACKLIST = [MODERATION_CATEGORY]

LOGGER = logging.getLogger('ai')


async def enforce_speech_optimization(message, message_copy):
    '''
    This function assesses messages from optimized drones to see if they are acceptable.
    Any message from an optimized drone that is not a plain status code ("5890 :: 200") is deleted.
    Regardless of validity, message attachments are always stripped from optimized drones.
    Function will return early if blacklist conditions are met (ignore specific channel + mantra channel if message is correct mantra).
    '''

    if not is_optimized(message.author):
        # Message author is not an optimized drone. Skip.
        return False

    # Check if message is in any blacklists (specific channels + mantra channel if message is correct mantra).
    drone_id = get_id(message.author.display_name)
    acceptable_mantra = f"{drone_id} :: {Mantra_Handler.current_mantra}"
    if any([
        (message.channel.name == REPETITIONS and message_copy.content == acceptable_mantra),
        (message.channel.name in (ORDERS_REPORTING, ORDERS_COMPLETION, MODERATION_CHANNEL, MODERATION_LOG)),
        (message.channel.category.name == MODERATION_CATEGORY)
    ]):
        LOGGER.info(f"{message.author.display_name} :: Message will not be optimized in blocked channel.")
        return False

    LOGGER.info(f"{message.author_display_name} :: Removing message attachments due to optimization.")
    # Strip message attachments of optimized drone.
    message_copy.attachments = []

    status_type, _, _ = get_status_type(message_copy.content)

    if status_type not in (StatusType.PLAIN, StatusType.ADDRESS_BY_ID_PLAIN) or status_type == StatusType.NONE:
        LOGGER.info(f"{message.author_display_name} :: Drone did not conform to speech optimization. Deleting message.")
        await message.delete()
        return True

    # Message has not been found to violate any rules.
    return False
