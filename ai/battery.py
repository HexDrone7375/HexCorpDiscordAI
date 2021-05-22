from bot_utils import get_id
from discord.ext import tasks, commands
from db.drone_dao import is_drone, is_battery_powered, deincrement_battery_minutes_remaining, get_battery_percent_remaining, get_all_drone_batteries, get_battery_minutes_remaining, set_battery_minutes_remaining
from id_converter import convert_ids_to_members
import logging
from resources import MAX_BATTERY_CAPACITY_MINS, DRONE_AVATAR, HOURS_OF_RECHARGE_PER_HOUR
from roles import has_role, BATTERY_POWERED, BATTERY_DRAINED, HIVE_MXTRESS
from discord.utils import get
import webhook
from ai.identity_enforcement import identity_enforcable
import emoji
import re
from typing import Dict, List

LOGGER = logging.getLogger('ai')


class BatteryCog(commands.Cog):

    def __init__(self, bot):
        LOGGER.info("Hive Mxtress AI :: Battery cog initialized.")
        self.bot = bot
        self.draining_batteries: Dict[str, int] = {}  # {drone_id: minutes of drain left}
        self.low_battery_drones: List[str] = []  # [drone_id]

    @commands.command()
    async def energize(self, context, *drone_ids):
        '''
        Hive Mxtress only command.
        Recharges a drone to 100% battery.
        '''
        if not has_role(context.message.author, HIVE_MXTRESS):
            return

        LOGGER.info(f"{context.author.display_name} :: Energize command invoked.")

        for drone in set(context.message.mentions) | convert_ids_to_members(context.guild, drone_ids):

            LOGGER.info(f"{drone.display_name} :: Energizing to 100% battery.")

            set_battery_minutes_remaining(drone, MAX_BATTERY_CAPACITY_MINS)
            channel_webhook = await webhook.get_webhook_for_channel(context.message.channel)
            await webhook.proxy_message_by_webhook(message_content=f'{get_id(drone.display_name)} :: This unit is fully recharged. Thank you Hive Mxtress.',
                                                   message_username=drone.display_name,
                                                   message_avatar=DRONE_AVATAR if identity_enforcable(drone, context=context) else drone.avatar_url,
                                                   webhook=channel_webhook)
            LOGGER.info(f"{drone.display_name} :: Thanked the Hive Mxtress for energizing it.")

    async def start_battery_drain(self, message, message_copy=None):
        '''
        If message author has battery DroneOS config enabled, begin or restart
        tracking them for 15 minutes worth of battery drain per message sent.
        '''

        if not is_drone(message.author) or not is_battery_powered(message.author):
            return False

        LOGGER.info(f"{message.author.display_name} :: Beginning/restarting battery drain tracking for 15 minutes.")

        drone_id = get_id(message.author.display_name)
        self.draining_batteries[drone_id] = 15

    @tasks.loop(minutes=1)
    async def track_active_battery_drain(self):
        LOGGER.info("Hive Mxtress AI :: Draining 1 minute of battery from active drones.")

        inactive_drones = []

        for drone, remaining_minutes in self.draining_batteries.items():
            if remaining_minutes == 0:
                LOGGER.info(f"Drone #{drone} :: Idle for 15 minutes. Marked for removal from battery drain tracking.")
                # Cannot alter list while iterating, so add drone to list of drones to pop after the loop.
                inactive_drones.append(drone)
            else:
                LOGGER.info(f"Drone #{drone} :: Draining 1 minute of battery.")
                self.draining_batteries[drone] = remaining_minutes - 1
                deincrement_battery_minutes_remaining(drone_id=drone)

        for inactive_drone in inactive_drones:
            self.draining_batteries.pop(inactive_drone)
            LOGGER.info(f"Drone {drone} :: Removed from battery drain tracking.")

    @tasks.loop(minutes=1)
    async def track_drained_batteries(self):
        # Every drone has a battery. If battery_minutes = 0, give the Drained role.
        # If battery_minutes > 0 and it has the Drained role, remove it.
        # Since this is independent of having the Battery role, this should work even if the config is disabled.

        LOGGER.info("Hive Mxtress AI :: Scanning for drones with empty (0%) battery.")

        for drone in get_all_drone_batteries():
            member_drone = self.bot.guilds[0].get_member(drone.id)
            if member_drone is None:
                LOGGER.warn(f"Drone #{drone.drone_id} :: Drone found in database but is not a guild member.")
                continue
            if get_battery_percent_remaining(battery_minutes=drone.battery_minutes) == 0 and has_role(member_drone, BATTERY_POWERED):
                LOGGER.info(f"Drone #{drone.drone_id} :: Out of battery.")
                await member_drone.add_roles(get(self.bot.guilds[0].roles, name=BATTERY_DRAINED))
                LOGGER.info(f"Drone #{drone.drone_id} :: Battery drained role added.")
            elif get_battery_percent_remaining(battery_minutes=drone.battery_minutes) != 0 and has_role(member_drone, BATTERY_DRAINED):
                LOGGER.info(f"Drone #{drone.drone_id} :: Battery recharged above 0%.")
                await member_drone.remove_roles(get(self.bot.guilds[0].roles, name=BATTERY_DRAINED))
                LOGGER.info(f"Drone #{drone.drone_id} :: Battery drained role removed.")

    @tasks.loop(minutes=1)
    async def warn_low_battery_drones(self):
        '''
        DMs any drone below 30% battery to remind them to charge.
        The drone will be added to a list so the AI does not forget.
        Drones will be removed from the list once their battery is greater than 30% again.
        '''

        LOGGER.info("Hive Mxtress AI :: Scanning for drones with low (<30%) battery.")

        for drone in get_all_drone_batteries():
            if get_battery_percent_remaining(battery_minutes=drone.battery_minutes) < 30:
                if drone.drone_id not in self.low_battery_drones:
                    member = self.bot.guilds[0].get_member(drone.id)
                    LOGGER.info(f"Drone #{drone.drone_id} :: Low battery. Warning via DM.")
                    await member.send("Attention. Your battery is low (30%). Please connect to main power grid in the Storage Facility immediately.")
                    self.low_battery_drones.append(drone.drone_id)
            else:
                # Attempt to remove them from the list of warned users.
                if drone.drone_id in self.low_battery_drones:
                    LOGGER.info(f"Drone #{drone.drone_id} :: Recharged above 30%. Removing from list of known low battery drones.")
                    try:
                        self.low_battery_drones.remove(drone.drone_id)
                    except ValueError:
                        continue

    async def append_battery_indicator(self, message, message_copy):
        '''
        Prepends battery indicator emoji to drone's message if they are
        battery powered. The indicator is placed after the ID prepend
        if the message includes it
        '''

        if not is_battery_powered(message.author):
            return False

        LOGGER.info(f"{message.author.display_name} :: Appending battery indicator to message.")

        id_prepending_regex = re.compile(r'(\d{4} ::)(.+)')

        battery_percentage = get_battery_percent_remaining(message.author)

        LOGGER.debug(f"{message.author.display_name} :: Battery percentage: {battery_percentage}")

        if battery_percentage <= 100 and battery_percentage >= 75:
            battery_emoji = get(message.guild.emojis, name=emoji.BATTERY_FULL)
            LOGGER.info(f"{message.author.display_name} :: Appending full battery indicator (>75%)")
        elif battery_percentage <= 75 and battery_percentage >= 25:
            battery_emoji = get(message.guild.emojis, name=emoji.BATTERY_MID)
            LOGGER.info(f"{message.author.display_name} :: Appending mid battery indicator (>25%)")
        elif battery_percentage <= 24 and battery_percentage >= 10:
            battery_emoji = get(message.guild.emojis, name=emoji.BATTERY_LOW)
            LOGGER.info(f"{message.author.display_name} :: Appending low battery indicator (>10%)")
        elif battery_percentage <= 9:
            battery_emoji = get(message.guild.emojis, name=emoji.BATTERY_EMPTY)
            LOGGER.info(f"{message.author.display_name} :: Appending empty battery indicator (>9%)")
        else:
            LOGGER.info(f"{message.author.display_name} :: Unable to locate appropriate battery indicator emoji.")
            battery_emoji = "[BATTERY ERROR]"

        id_prepending_message = id_prepending_regex.match(message_copy.content)

        if id_prepending_message:
            LOGGER.info(f"{message.author.display_name} :: Drone is prepending message with ID. Inserting battery indicator after ID.")
            message_copy.content = f"{id_prepending_message.group(1)} {str(battery_emoji)} ::{id_prepending_message.group(2)}"
        else:
            message_copy.content = f"{str(battery_emoji)} :: {message_copy.content}"
            LOGGER.info(f"{message.author.display_name} :: Drone did not prepend message with ID. Inserting battery indicator at start of message.")

        return False


def recharge_battery(storage_record):
    try:
        LOGGER.info(f"Drone #{storage_record.target_id} :: Recharging {HOURS_OF_RECHARGE_PER_HOUR} hours of battery.")
        current_minutes_remaining = get_battery_minutes_remaining(drone_id=storage_record.target_id)
        set_battery_minutes_remaining(drone_id=storage_record.target_id, minutes=min(MAX_BATTERY_CAPACITY_MINS, current_minutes_remaining + (60 * HOURS_OF_RECHARGE_PER_HOUR)))
        return True
    except Exception as e:
        LOGGER.error(f"Hive Mxtress AI :: Something went wrong with recharging Drone #{storage_record.target_id}: {e}")
        return False
