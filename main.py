import os
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from icalendar import Calendar, Event, vText, Alarm
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Fantacalcio Calendar Reminder")

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_URL = "http://api.football-data.org/v4/competitions/SA/matches"

def get_next_matchday_first_match():
    if not FOOTBALL_DATA_API_KEY:
        raise ValueError("API Key per football-data.org non configurata.")

    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    response = requests.get(API_URL, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Errore API football-data.org: {response.status_code} - {response.text}")
        
    data = response.json()
    matches = data.get("matches", [])
    
    # Filtriamo le partite non ancora giocate
    upcoming_matches = [m for m in matches if m["status"] in ("SCHEDULED", "TIMED")]
    
    if not upcoming_matches:
        return None
        
    # Troviamo la prossima giornata (matchday)
    upcoming_matchdays = [m["matchday"] for m in upcoming_matches if m["matchday"] is not None]
    if not upcoming_matchdays:
        return None
        
    next_matchday = min(upcoming_matchdays)
    
    # Prendiamo tutte le partite di quella giornata
    next_matchday_matches = [m for m in upcoming_matches if m["matchday"] == next_matchday]
    
    # Ordiniamo per data
    next_matchday_matches.sort(key=lambda x: x["utcDate"])
    
    # Il primo match (l'anticipo)
    first_match = next_matchday_matches[0]
    return first_match

@app.get("/calendar.ics", response_class=Response)
def get_calendar():
    try:
        first_match = get_next_matchday_first_match()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    cal = Calendar()
    cal.add('prodid', '-//Fantacalcio Reminder//fantacalcio.it//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('x-wr-calname', 'Fantacalcio')
    cal.add('x-wr-timezone', 'Europe/Rome')
    cal.add('refresh-interval', 'PT4H') # Suggerisce al client di aggiornare ogni 4 ore
    
    if first_match:
        # utcDate è in formato ISO "2023-09-16T13:00:00Z"
        match_time = datetime.strptime(first_match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        
        # Vogliamo la scadenza 15 minuti prima dell'inizio
        reminder_time = match_time - timedelta(minutes=15)
        
        event = Event()
        event.add('summary', f'Schierare Formazione - Giornata {first_match["matchday"]}')
        
        home_team = first_match["homeTeam"]["shortName"]
        away_team = first_match["awayTeam"]["shortName"]
        
        event.add('description', f'Primo match della giornata: {home_team} vs {away_team}\nRicordati di schierare la formazione!')
        
        # Evento di 15 minuti che termina all'inizio della partita
        event.add('dtstart', reminder_time)
        event.add('dtend', match_time)
        event.add('dtstamp', datetime.utcnow())
        
        # ID univoco basato sulla giornata
        event.add('uid', f'fantacalcio-matchday-{first_match["matchday"]}@fantacalcio.it')
        
        # Aggiungiamo un allarme visivo/sonoro (molti client lo supportano)
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Promemoria Formazione Fantacalcio')
        alarm.add('trigger', timedelta(minutes=-15)) # 15 minuti prima del 'dtstart' dell'evento (quindi 30 min prima del match)
        event.add_component(alarm)
        
        cal.add_component(event)

    # Restituisce l'iCal formattato correttamente
    return Response(content=cal.to_ical(), media_type="text/calendar")

@app.get("/")
def index():
    return {"message": "Fantacalcio Calendar Service is running. Add /calendar.ics to your calendar app."}
