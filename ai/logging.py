import logging
from logging import handlers
import discord
from discord.ext.commands import Context
from db.drone_dao import is_drone, is_glitched, is_prepending_id, is_battery_powered, is_identity_enforced, is_optimized


def get_droneos_configs(msg: discord.Message):
    '''
    Returns single string list of all active DroneOS configs.
    Returns "None" if no configs active.
    Returns "N/A" if user is not a drone.
    '''

    if not is_drone(msg.author):
        return "N/A"

    full_config_list = ""

    if is_glitched(msg.author):
        full_config_list += "Glitched, "
    if is_prepending_id(msg.author):
        full_config_list += "Prepending ID, "
    if is_battery_powered(msg.author):
        full_config_list += "Battery powered, "
    if is_identity_enforced(msg.author):
        full_config_list += "Identity enforced, "
    if is_optimized(msg.author):
        full_config_list += "Optimized, "

    if full_config_list == "":
        return "None"
    return full_config_list


def get_author_roles(msg: discord.Message):
    '''
    Gets all roles from the Author of a Discord Message and returns all names
    names as a joined string.
    '''

    full_roles_list = ""

    for role in msg.author.roles:
        if role.name == "@everyone":
            continue
        full_roles_list += f"{role}, "

    return full_roles_list


LOG_FORMAT_RULES = {
    'newline': True  # Each data piece on a newline.
}

# Dict of toggleable values. True if logged, false if not. The key must be a
# dotted lookup for attribute traversal (see build_log_message)
LOG_DATA_RULES = {
    'content': True,
    'guild.id': False,
    'author.display_name': True,
    'author.name': True,
    'channel.name': True,
    'category.name': False
}

LOG_ADVANCED_DATA_RULES = {
    'roles': get_author_roles,
    'droneOS configs': get_droneos_configs
}

LOGGER = logging.getLogger('ai')


def set_up_logger():
    # Logging setup
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d :: %(levelname)s :: %(message)s', datefmt='%Y-%m-%d :: %H:%M:%S')

    log_file_handler = handlers.TimedRotatingFileHandler(
        filename='ai.log', encoding='utf-8', backupCount=6, when='D', interval=7)
    log_file_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.WARNING)
    root_logger = logging.getLogger()
    root_logger.addHandler(log_file_handler)

    LOGGER = logging.getLogger('ai')
    LOGGER.setLevel(logging.DEBUG)


def build_log_message(msg, dcon, dmsg):
    # If have a message, use that, otherwise get the message object from the context.
    if dmsg is None:
        dmsg = dcon.message

    full_msg = msg + "\n"  # String concat because fstrings don't like backslashes.

    # Handle dotted lookups on message object.
    for full_attribute_path, is_logged in LOG_DATA_RULES.items():
        if not is_logged:
            continue
        split_attribute_path = full_attribute_path.split(".")
        current_attribute = dmsg
        for next_attribute in split_attribute_path:
            try:
                current_attribute = getattr(current_attribute, next_attribute)
            except AttributeError:
                break
        full_msg += f"[{full_attribute_path}: {current_attribute}],"

        if LOG_FORMAT_RULES.get('newline', False):
            full_msg += "\n"
        else:
            full_msg += " "

    # Handle special data functionality.
    for identifier, func in LOG_ADVANCED_DATA_RULES.items():
        full_msg += f"[{identifier}: {func(dmsg)}],"

        if LOG_FORMAT_RULES.get('newline', False):
            full_msg += "\n"
        else:
            full_msg += " "

    # Delete the previous formatting character
    full_msg = full_msg[:-1]

    return full_msg


def info(msg, dcon: Context = None, dmsg: discord.Message = None):
    '''
    Used for logging events ("Transformed status code to status message.")
    '''
    if dcon is None and dmsg is None:
        # Lets you log outside of standard events like in main.py's initial setup.
        LOGGER.info(msg)
    else:
        LOGGER.info(build_log_message(msg, dcon, dmsg))


def debug(msg, dcon: Context = None, dmsg: discord.Message = None):
    '''
    Used for logging additional data ("Array length: 30")
    '''
    pass


def warn(msg, dcon: Context = None, dmsg: discord.Message = None):
    # Unimplemented
    pass


def error(msg, dcon: Context = None, dmsg: discord.Message = None):
    # Unimplemented
    pass