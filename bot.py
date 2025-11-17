import os
import time
from datetime import timedelta, datetime
from pytz import timezone
from aiohttp import web

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from route import web_server


SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None)
PORT = Config.PORT


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Botskingdom",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.start_time = time.time()

    async def start(self):
        await super().start()

        me = await self.get_me()
        print(f"{me.first_name} Started... ✨️")

        # Webhook start if enabled
        if Config.WEBHOOK:
            runner = web.AppRunner(await web_server())
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", PORT).start()

        # Uptime formatting
        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))

        # Prepare restart message
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime("%d %B, %Y")
        time_str = curr.strftime("%I:%M:%S %p")

        caption = (
            "**I Restarted Again !**\n\n"
            f"🕒 Uptime before restart: `{uptime_string}`\n"
            f"📅 Date: `{date}`\n"
            f"⏰ Time: `{time_str}`"
        )

        # Broadcast to log + support chat
        send_list = [Config.LOG_CHANNEL]

        # Add support chat only if valid
        if SUPPORT_CHAT and SUPPORT_CHAT.startswith("@"):
            send_list.append(SUPPORT_CHAT)

        for chat_id in send_list:
            try:
                await self.send_photo(
                    chat_id=chat_id,
                    photo=Config.START_PIC,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Updates", url="https://t.me/botskingdoms")]]
                    )
                )
            except Exception as e:
                print(f"❌ Failed to send message to {chat_id}: {e}")


bot = Bot()
bot.run()
