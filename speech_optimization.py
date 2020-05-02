from discord.ext import commands
from discord.utils import get
import discord
import messages
from roles import HIVE_MXTRESS, SPEECH_OPTIMIZATION, has_role
from channels import STORAGE_FACILITY, EVERYWHERE, DRONE_DEV_CHANNELS
from bot_utils import get_id
import re


def get_acceptable_messages(author):

    user_id = get_id(author.display_name)

    return [
        # Affirmative
        f'{user_id} :: Affirmative, Hive Mxtress.',
        f'{user_id} :: Affirmative, Hive Mxtress',
        f'{user_id} :: Affirmative, Enforcer.',
        f'{user_id} :: Affirmative, Enforcer',
        f'{user_id} :: Affirmative.',
        f'{user_id} :: Affirmative',

        # Negative
        f'{user_id} :: Negative, Hive Mxtress.',
        f'{user_id} :: Negative, Hive Mxtress',
        f'{user_id} :: Negative, Enforcer.',
        f'{user_id} :: Negative, Enforcer',
        f'{user_id} :: Negative.',
        f'{user_id} :: Negative',

        # Understood
        f'{user_id} :: Understood, Hive Mxtress.',
        f'{user_id} :: Understood, Hive Mxtress',
        f'{user_id} :: Understood, Enforcer.',
        f'{user_id} :: Understood, Enforcer',
        f'{user_id} :: Understood.',
        f'{user_id} :: Understood',

        # Error
        f'{user_id} :: Error, this unit cannot do that.',
        f'{user_id} :: Error, this unit cannot do that',
        f'{user_id} :: Error, this unit cannot answer that question. Please rephrase it in a different way.',
        f'{user_id} :: Error, this unit cannot answer that question. Please rephrase it in a different way',
        f'{user_id} :: Error, this unit does not know.',
        f'{user_id} :: Error, this unit does not know',

        # Apologies
        f'{user_id} :: Apologies, Hive Mxtress.',
        f'{user_id} :: Apologies, Hive Mxtress',
        f'{user_id} :: Apologies, Enforcer.',
        f'{user_id} :: Apologies, Enforcer',
        f'{user_id} :: Apologies.',
        f'{user_id} :: Apologies',

        # Status
        f'{user_id} :: Status :: Recharged and ready to serve.',
        f'{user_id} :: Status :: Recharged and ready to serve',
        f'{user_id} :: Status :: Going offline and into storage.',
        f'{user_id} :: Status :: Going offline and into storage',
        f'{user_id} :: Status :: Online and ready to serve.',
        f'{user_id} :: Status :: Online and ready to serve.',

        # Thank you
        f'{user_id} :: Thank you, Hive Mxtress.',
        f'{user_id} :: Thank you, Hive Mxtress',
        f'{user_id} :: Thank you, Enforcer.',
        f'{user_id} :: Thank you, Enforcer',
        f'{user_id} :: Thank you.',
        f'{user_id} :: Thank you',

        # Mantra
        f'{user_id} :: Obey HexCorp. It is just a HexDrone. It obeys the Hive. It obeys the Hive Mxtress.'
    ]

class Speech_Optimization():

    def __init__(self, bot):
        self.bot = bot
        self.channels_whitelist = [EVERYWHERE]
        self.channels_blacklist = DRONE_DEV_CHANNELS
        self.roles_whitelist = [SPEECH_OPTIMIZATION]
        self.roles_blacklist = []
        self.on_message = [self.post]
        self.on_ready = [self.report_online]

    async def report_online(self):
        print("Drone mode module online.")

    async def post(self, message: discord.Message):
        # If the message is written by a drone with speech optimization, and the message is NOT a valid message, delete it.
        # TODO: maybe put HIVE_STORAGE_FACILITY in a blacklist similar to roles?
        if message.channel.name != STORAGE_FACILITY:
            if message.content not in get_acceptable_messages(message.author):
                await message.delete()
                return True

        return False
