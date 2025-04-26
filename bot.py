import requests
import asyncio
import nest_asyncio
from telegram import Bot
from telegram.error import RetryAfter
from datetime import datetime, timedelta

nest_asyncio.apply()

SPORTMONKS_API_TOKEN = "juhvbus1A58J1qdImzNHOvPpV4FNd9FeotReBGHFtcVX3Glp69ndHjrKHmh9"
TELEGRAM_BOT_TOKEN = "7634110829:AAHGThjyyp2EkH5fTT1TPt1cSFGeCY7-hlk"
CHAT_ID = 7534364558

def get_french_leagues():
    url = "https://api.sportmonks.com/v3/football/leagues"
    params = {"api_token": SPORTMONKS_API_TOKEN, "per_page": 100}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        leagues = response.json().get("data", [])
        france_leagues = [league['id'] for league in leagues if league.get('country', {}).get('name', '').lower() == 'france']
        print(f"Ligues françaises détectées : {france_leagues}")
        return france_leagues
    else:
        print(f"Erreur API : {response.status_code}")
        return []

def get_next_date():
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

def get_scheduled_matches(date, league_ids):
    url = f"https://api.sportmonks.com/v3/football/fixtures/date/{date}"
    params = {
        "include": "participants;league",
        "api_token": SPORTMONKS_API_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        all_matches = response.json().get("data", [])
        filtered = [m for m in all_matches if m.get('league') and m['league'].get('data') and m['league']['data']['id'] in league_ids]
        print(f"Nombre de matchs français pour la date {date}: {len(filtered)}")
        return filtered
    else:
        print(f"Erreur API : {response.status_code}")
        return []

async def send_telegram_message(bot, text):
    retry = True
    while retry:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            retry = False
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)

async def main():
    league_ids = get_french_leagues()
    date = get_next_date()
    print(f"Pronostics Loto Foot pour le {date}")

    matches = get_scheduled_matches(date, league_ids)
    if not matches:
        print("Aucun match trouvé pour la date.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    messages = []

    for match in matches:
        home = match['participants'][0]['name']
        away = match['participants'][1]['name']
        league = match['league']['data']['name'] if match.get('league') and match['league'].get('data') else "Inconnu"
        messages.append(f"{home} vs {away} | Ligue: {league}")

    message_text = f"📅 Matchs français pour le {date}:\n" + "\n".join(messages)
    print(message_text)
    await send_telegram_message(bot, message_text)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())




