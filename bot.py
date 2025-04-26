import requests
from bs4 import BeautifulSoup
import asyncio
import nest_asyncio
from telegram import Bot
from telegram.error import RetryAfter

nest_asyncio.apply()

TELEGRAM_BOT_TOKEN = "7634110829:AAHGThjyyp2EkH5fTT1TPt1cSFGeCY7-hlk"
CHAT_ID = 7534364558

def get_lotofoot_matches():
    url = "https://www.flashscore.fr/football/france/loto-foot/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    matches = []
    # Trouve tous les matchs 
    match_divs = soup.select('div.event__match')
    for match_div in match_divs:
        home = match_div.select_one('div.event__participant--home')
        away = match_div.select_one('div.event__participant--away')
        time = match_div.select_one('div.event__time')
        if home and away and time:
            matches.append({
                "home": home.text.strip(),
                "away": away.text.strip(),
                "time": time.text.strip()
            })
    return matches

def generate_simple_pronostics(matches):
    pronostics = []
    for m in matches:
        # Pronostic basique : victoire domicile
        pronostics.append(f"{m['home']} vs {m['away']} à {m['time']} → Pronostic: 1")
    return pronostics

async def send_telegram_message(bot, text):
    retry = True
    while retry:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            retry = False
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)

async def main():
    matches = get_lotofoot_matches()
    if not matches:
        print("Aucun match récupéré.")
        return
    
    pronostics = generate_simple_pronostics(matches)
    message_text = "📅 Pronostics Loto Foot :\n" + "\n".join(pronostics[:15])  # limite à 15

    print(message_text)

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await send_telegram_message(bot, message_text)

if __name__ == "__main__":
    asyncio.run(main())





