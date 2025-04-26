import asyncio
import nest_asyncio
from telegram import Bot
from telegram.error import RetryAfter

nest_asyncio.apply()

TELEGRAM_BOT_TOKEN = "7634110829:AAHGThjyyp2EkH5fTT1TPt1cSFGeCY7-hlk"
CHAT_ID = 7534364558

async def send_telegram_message(bot, text):
    retry = True
    while retry:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            retry = False
        except RetryAfter as e:
            print(f"Flood détecté, attente de {e.retry_after} secondes")
            await asyncio.sleep(e.retry_after)

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await send_telegram_message(bot, "Test d’envoi message Telegram réussi.")
    print("Message de test envoyé sur Telegram.")

if __name__ == "__main__":
    asyncio.run(main())
