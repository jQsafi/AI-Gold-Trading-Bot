import MetaTrader5 as mt5
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_calendar():
    if not mt5.initialize():
        print("Failed to initialize MT5")
        return

    authorized = mt5.login(int(os.getenv("MT5_LOGIN")), password=os.getenv("MT5_PASSWORD"), server=os.getenv("MT5_SERVER"))
    if not authorized:
        print("Login failed")
        return

    # Get events for the next 24 hours
    utc_from = datetime.utcnow()
    utc_to = utc_from + timedelta(hours=24)
    
    events = mt5.calendar_events_get(utc_from=utc_from, utc_to=utc_to)
    
    if events is None or len(events) == 0:
        print("No calendar events found. Note: MT5 calendar may not be populated on all servers.")
    else:
        print(f"Found {len(events)} events.")
        for event in events[:5]: # Show first 5
            print(f"Time: {datetime.fromtimestamp(event.time)}, Currency: {event.currency}, Importance: {event.importance}, Name: {event.event_name}")

    mt5.shutdown()

if __name__ == "__main__":
    test_calendar()
