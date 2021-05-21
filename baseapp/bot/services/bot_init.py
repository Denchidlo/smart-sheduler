from django.conf import settings
from ..dbmodels.auth import ScheduleUser
import time
from telebot import TeleBot, logger, types
import logging

__author__ = "@schedulebase_bot"

if settings.DEBUG:
    logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

    if not settings.DATA_UPLOAD:
        logging.debug(f"Created base user admin")
        try:
            ScheduleUser.objects.get(username="admin")
        except:
            ScheduleUser.objects.create_superuser(
                "admin", "Чепуха", "Костлявая", "admin"
            )

bot = TeleBot(settings.TOKEN)

bot.set_my_commands(
    [
        types.BotCommand("start", "Begin authentification"),
        types.BotCommand("cancel", "Interrupt all actions, get to the stable state"),
    ]
)

settings.BOT = bot

bot.remove_webhook()
logging.info("Removed previous webhook")
time.sleep(1)
bot.set_webhook(url=f"{settings.DOMAIN}/bot/")
logging.info("Set new webhook")
