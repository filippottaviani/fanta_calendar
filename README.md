# Fantacalcio Calendar Reminder

Questo servizio genera dinamicamente un feed iCalendar (`.ics`) che contiene un promemoria (sotto forma di evento) per la prossima giornata di Serie A. Il calendario controlla automaticamente gli orari aggiornati e imposta il promemoria in concomitanza con il **primo anticipo** della giornata.

## Come funziona

Quando il tuo calendario (es. Google Calendar o Apple Calendar) richiede il link, il server:
1. Interroga l'API di `football-data.org` per ottenere il calendario della Serie A.
2. Trova la prossima giornata da giocare.
3. Trova la prima partita in programma per quella giornata.
4. Genera un evento che inizia 15 minuti prima del calcio d'inizio per ricordarti di schierare la formazione.

## Configurazione Locale

1. Crea un account gratuito su [football-data.org](https://www.football-data.org/) e ottieni la tua chiave API.
2. Crea un file `.env` nella directory principale copiando `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Inserisci la tua chiave API nel file `.env`:
   ```
   FOOTBALL_DATA_API_KEY=la_tua_chiave_qui
   ```
4. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
5. Avvia il server:
   ```bash
   uvicorn main:app --reload
   ```
6. Il feed sarà disponibile all'indirizzo: `http://localhost:8000/calendar.ics`

## Deploy

Per far sì che il tuo Google Calendar o Apple Calendar possa accedere al feed, devi esporlo su internet. Il modo più semplice è usare servizi gratuiti come **Render**, **Vercel** o **Railway**.

### Deploy su Render (Gratuito)
1. Carica questo progetto su un tuo repository GitHub.
2. Vai su [Render.com](https://render.com) e crea un nuovo "Web Service".
3. Collega il tuo repository GitHub.
4. Imposta "Build Command" a `pip install -r requirements.txt`.
5. Imposta "Start Command" a `uvicorn main:app --host 0.0.0.0 --port $PORT`.
6. Nella sezione "Environment Variables", aggiungi la variabile `FOOTBALL_DATA_API_KEY` con la tua chiave.
7. Una volta online, usa il link fornito da Render (es. `https://tuo-app.onrender.com/calendar.ics`) per iscriverti dal tuo calendario.

## Come iscriversi (Sottoscrizione iCal)

### Google Calendar
1. Apri Google Calendar sul web.
2. Sulla sinistra, accanto a "Altri calendari", clicca sul tasto "+" e poi su "Da URL".
3. Incolla l'URL del tuo servizio (es. `https://tuo-app.onrender.com/calendar.ics`).
4. Clicca su "Aggiungi calendario".

### Apple Calendar
1. Apri l'app Calendario.
2. Vai su File > Nuova iscrizione a calendario...
3. Incolla l'URL e clicca "Iscriviti".
