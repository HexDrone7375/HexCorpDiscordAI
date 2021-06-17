import logging
from logging import handlers
import discord
from discord.ext.commands import Context

LOG_RULES = {
    'content': True,
    'guild.id': False,
    'author.display_name': True,
    'author.name': True,
    'channel.name': True,
    'category.name': False
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

    full_msg = "["

    for attribute_path, is_logged in LOG_RULES:
        if not is_logged:
            continue
        attribute_path = attribute_path.split(".")
        current_attribute = dmsg
        for next_attribute in attribute_path:
            try:
                current_attribute = getattr(current_attribute, next_attribute)
            except AttributeError:
                break
        full_msg += f"{attribute_path}: {current_attribute},"
    
    full_msg += "]"

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
