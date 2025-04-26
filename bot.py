import asyncio
import nest_asyncio
from telegram import Bot
from telegram.error import RetryAfter

nest_asyncio.apply()

TELEGRAM_BOT_TOKEN = "7634110829:AAHGThjyyp2EkH5fTT1TPt1cSFGeCY7-hlk"
CHAT_ID = 7534364558

async def send_telegram_message(bot, text):
    print("Début envoi message Telegram...")
    retry = True
    while retry:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            print("Message Telegram envoyé avec succès")
            retry = False
        except RetryAfter as e:
            print(f"Flood détecté, attente {e.retry_after} secondes")
            await asyncio.sleep(e.retry_after)
    print("Fin de la fonction d’envoi Telegram")

async def main():
    print("Script démarré.")
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await send_telegram_message(bot, "Test d’envoi Telegram - Yazid")
    print("Script terminé.")

if __name__ == "__main__":
    asyncio.run(main())

