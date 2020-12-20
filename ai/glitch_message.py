import discord
import random
from db.drone_dao import is_glitched, get_battery_charge
import re
import logging
from decimal import Decimal

diacritics = list(range(0x0300, 0x036F))  # This is the unicode range for diacritic marks.
garbage = list(range(33, 126))  # Standard ascii characters.
MAX_DIACRITIC_MARKS = 200  # Discord gets fussy if you try and put more than 300 diacritic marks in a message to prevent a crash from zalgo overload.

LOGGER = logging.getLogger('ai')


def glitch_message_content(text: str, battery_percentage: Decimal):

    glitched_text_array = list(text)
    max_message_length = int(2000 * float(battery_percentage))


    # How tf do I interpolate again

    min_garbage_character_diacritics = 1
    max_garbage_character_diacritics = 4
    additional_diacritics_used = 0

    LOGGER.info(f"Maximum message length is: {max_message_length}")

    if len(text) > max_message_length:
        additional_diacritics_used = 0
        LOGGER.info("Interrupting and glitching excessively long message.")
        # Chop off anything past the 1000 character mark and add garbage scrambling.
        glitched_text_array = glitched_text_array[0:max_message_length]
        garbage_length = random.randrange(10, 20)
        for diacritic_step in range(0, garbage_length):
            garbage_character = chr(random.choice(garbage))

            
            for diacritic in range(0, diacritic_step):
                garbage_character += chr(random.choice(diacritics))
                additional_diacritics_used += 1
            glitched_text_array.append(garbage_character)
        
        LOGGER.info(f"Used {additional_diacritics_used}")

    LOGGER.info(f"Adding {min(int((MAX_DIACRITIC_MARKS - additional_diacritics_used) * (1 - float(battery_percentage))), 2000 - len(glitched_text_array))} diacritics.")
    LOGGER.info(f"Length: {len(glitched_text_array)}")

    for diacritic in range(0, min(int((MAX_DIACRITIC_MARKS - additional_diacritics_used) * (1 - float(battery_percentage))), 2000 - len(glitched_text_array))):  # Add either the maximum amount of diacritics, or however many the message can fit. Whichever's less.
        index = random.randrange(0, len(glitched_text_array))
        #LOGGER.info(f"Adding character at: {index}")
        glitched_text_array[index] += chr(random.choice(diacritics))

    # if (battery_percentage.compare(Decimal(0.2)) <= 0):  # Add a low battery indicator to the start of the message if the drone is below 20% battery.
    #     glitched_text_array = list("[⚠️ :: Low battery.] ") + glitched_text_array

    return "".join(glitched_text_array)


glitch_template = re.compile(r'(\d{4} :: )(.*)')


async def glitch_if_applicable(message: discord.Message, message_copy):
    if is_glitched(message.author):

        battery_percentage = get_battery_charge(message.author)

        template_match = glitch_template.match(message_copy.content)
        if template_match:
            message_copy.content = template_match.group(1) + glitch_message_content(template_match.group(2), battery_percentage)  # If a drone is using an op code, only glitch the part after its ID.
        else:
            message_copy.content = glitch_message_content(message_copy.content, battery_percentage)  # Otherwise, glitch the whole message.
    return False
