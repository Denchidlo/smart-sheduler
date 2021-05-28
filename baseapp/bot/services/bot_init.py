from django.conf import settings
from ..dbmodels.auth import ScheduleUser
import time
from telebot import AsyncTeleBot, logger, types
import logging

__author__ = "@schedulebase_bot"

if settings.DEBUG:  # pragma: no cover
    logger.setLevel(settings.LOG_LEVEL)

    # if not settings.DATA_UPLOAD:
    logging.debug(f"Created base user admin")
    try:
        ScheduleUser.objects.get(username="admin")
    except:
        ScheduleUser.objects.create_superuser("admin", "Чепуха", "Костлявая", "admin")


bot = AsyncTeleBot(settings.TOKEN)
bot.threaded = True

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
logging.info(f"Webhook info: {bot.get_webhook_info()}")
