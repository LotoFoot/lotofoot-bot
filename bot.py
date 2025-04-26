import requests
import asyncio
import nest_asyncio
import schedule
import time
from telegram import Bot
from telegram.error import RetryAfter
from datetime import datetime, timedelta

nest_asyncio.apply()

SPORTMONKS_API_TOKEN = "RctqRYlHUA7RncEHvgOQ9siUSWt7vQcX8RlAJ2QgEjY9jHGD0rfUI92vmJNS"
TELEGRAM_BOT_TOKEN = "7634364558:AAHGThjyyp2EkH5fTT1TPt1cSFGeCY7-hlk"
CHAT_ID = 7534364558

def get_french_leagues():
    url = "https://api.sportmonks.com/v3/football/leagues"
    params = {"api_token": SPORTMONKS_API_TOKEN, "per_page": 100}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        leagues = response.json().get("data", [])
        return [league['id'] for league in leagues if league.get('country', {}).get('name', '').lower() == 'france']
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
        return [m for m in all_matches if m.get('league') and m['league'].get('data') and m['league']['data']['id'] in league_ids]
    else:
        print(f"Erreur API : {response.status_code}")
        return []

def get_team_form(team_id):
    url = f"https://api.sportmonks.com/v3/football/teams/{team_id}/form"
    params = {"api_token": SPORTMONKS_API_TOKEN}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        wins = sum(1 for m in data if m.get('score', {}).get('winner_team_id') == team_id)
        total = len(data)
        return wins / total if total > 0 else 0
    return 0

def generate_pronostic(home_id, away_id):
    home_form = get_team_form(home_id)
    away_form = get_team_form(away_id)
    if home_form > away_form + 0.2:
        return "1"
    elif away_form > home_form + 0.2:
        return "2"
    else:
        return "N"

async def send_telegram_message(bot, text):
    retry = True
    while retry:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            retry = False
        except RetryAfter as e:
            print(f"Flood détecté, attente de {e.retry_after}s")
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
        home_id = match['participants'][0]['id']
        away_id = match['participants'][1]['id']
        league = match['league']['data']['name']
        pronostic = generate_pronostic(home_id, away_id)
        messages.append(f"{home} vs {away} | Ligue : {league} | Pronostic : {pronostic}")
    message_text = "\n".join(messages)
    await send_telegram_message(bot, message_text)
    print("Pronostics envoyés.")

def job():
    asyncio.run(main())

if __name__ == "__main__":
    schedule.every().day.at("09:00").do(job)
    print("Bot démarré, envoi des pronostics chaque jour à 09:00.")
    while True:
        schedule.run_pending()
        time.sleep(30)
