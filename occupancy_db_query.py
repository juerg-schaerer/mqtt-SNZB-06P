#!/usr/bin/env python3

import sqlite3
import datetime
import argparse
import sys
import os

# Database Configuration
DB_FILE = "occupancy_data.db"

def check_database_exists():
    """
    Check if the database file exists.
    """
    if not os.path.exists(DB_FILE):
        print(f"Fehler: Datenbank {DB_FILE} existiert nicht. Bitte führen Sie zuerst mqtt_occupancy_monitor_db.py aus.")
        return False
    return True

def get_connection():
    """
    Get a connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Configure connection to return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        sys.exit(1)

def get_recent_events(limit=10):
    """
    Get the most recent occupancy events.
    
    Args:
        limit (int): Maximum number of events to return
    """
    if not check_database_exists():
        return []
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT id, timestamp, occupancy 
        FROM occupancy_events 
        ORDER BY timestamp DESC 
        LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        events = []
        
        for row in rows:
            # Convert SQLite row to dictionary
            event = dict(row)
            # Convert occupancy to human-readable text
            event['status'] = "Anwesend" if event['occupancy'] else "Abwesend"
            events.append(event)
            
        return events
    except sqlite3.Error as e:
        print(f"Fehler bei der Datenbankabfrage: {e}")
        return []
    finally:
        conn.close()

def get_events_by_date(date_str):
    """
    Get occupancy events for a specific date.
    
    Args:
        date_str (str): Date in format YYYY-MM-DD
    """
    if not check_database_exists():
        return []
        
    try:
        # Parse the date string
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        # Calculate the next day
        next_day = date_obj + datetime.timedelta(days=1)
        # Format dates for SQLite query
        date_start = date_obj.strftime("%Y-%m-%d")
        date_end = next_day.strftime("%Y-%m-%d")
    except ValueError:
        print(f"Fehler: Ungültiges Datumsformat. Bitte verwenden Sie YYYY-MM-DD.")
        return []
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT id, timestamp, occupancy 
        FROM occupancy_events 
        WHERE timestamp >= ? AND timestamp < ? 
        ORDER BY timestamp ASC
        """, (date_start, date_end))
        
        rows = cursor.fetchall()
        events = []
        
        for row in rows:
            event = dict(row)
            event['status'] = "Anwesend" if event['occupancy'] else "Abwesend"
            # Format timestamp for better readability
            try:
                dt = datetime.datetime.fromisoformat(event['timestamp'])
                event['formatted_time'] = dt.strftime("%H:%M:%S")
            except ValueError:
                event['formatted_time'] = event['timestamp']
            events.append(event)
            
        return events
    except sqlite3.Error as e:
        print(f"Fehler bei der Datenbankabfrage: {e}")
        return []
    finally:
        conn.close()

def get_statistics():
    """
    Get statistics about occupancy events.
    """
    if not check_database_exists():
        return {}
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get total count of events
        cursor.execute("SELECT COUNT(*) as total FROM occupancy_events")
        total = cursor.fetchone()['total']
        
        # Get count of presence events
        cursor.execute("SELECT COUNT(*) as presence FROM occupancy_events WHERE occupancy = 1")
        presence = cursor.fetchone()['presence']
        
        # Get count of absence events
        cursor.execute("SELECT COUNT(*) as absence FROM occupancy_events WHERE occupancy = 0")
        absence = cursor.fetchone()['absence']
        
        # Get first and last event timestamps
        cursor.execute("SELECT MIN(timestamp) as first, MAX(timestamp) as last FROM occupancy_events")
        row = cursor.fetchone()
        first = row['first']
        last = row['last']
        
        # Calculate date range
        try:
            first_date = datetime.datetime.fromisoformat(first)
            last_date = datetime.datetime.fromisoformat(last)
            days = (last_date - first_date).days + 1
        except (ValueError, TypeError):
            days = 0
        
        return {
            'total_events': total,
            'presence_events': presence,
            'absence_events': absence,
            'first_event': first,
            'last_event': last,
            'days_covered': days
        }
    except sqlite3.Error as e:
        print(f"Fehler bei der Datenbankabfrage: {e}")
        return {}
    finally:
        conn.close()

def print_recent_events(limit=10):
    """
    Print the most recent occupancy events.
    """
    events = get_recent_events(limit)
    
    if not events:
        print("Keine Ereignisse gefunden.")
        return
    
    print(f"\nLetzte {len(events)} Anwesenheitsereignisse:")
    print("-" * 60)
    print(f"{'ID':<5} {'Zeitstempel':<25} {'Status':<10}")
    print("-" * 60)
    
    for event in events:
        print(f"{event['id']:<5} {event['timestamp']:<25} {event['status']:<10}")

def print_events_by_date(date_str):
    """
    Print occupancy events for a specific date.
    """
    events = get_events_by_date(date_str)
    
    if not events:
        print(f"Keine Ereignisse für das Datum {date_str} gefunden.")
        return
    
    print(f"\nAnwesenheitsereignisse für {date_str}:")
    print("-" * 60)
    print(f"{'Zeit':<10} {'Status':<10}")
    print("-" * 60)
    
    for event in events:
        print(f"{event['formatted_time']:<10} {event['status']:<10}")

def print_statistics():
    """
    Print statistics about occupancy events.
    """
    stats = get_statistics()
    
    if not stats:
        print("Keine Statistiken verfügbar.")
        return
    
    print("\nStatistik der Anwesenheitsereignisse:")
    print("-" * 60)
    print(f"Gesamtzahl der Ereignisse: {stats['total_events']}")
    print(f"Anwesenheitsereignisse:    {stats['presence_events']}")
    print(f"Abwesenheitsereignisse:    {stats['absence_events']}")
    print(f"Erstes Ereignis:           {stats['first_event']}")
    print(f"Letztes Ereignis:          {stats['last_event']}")
    print(f"Abgedeckte Tage:           {stats['days_covered']}")

def main():
    parser = argparse.ArgumentParser(description="Abfrage der Anwesenheits-Datenbank")
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")
    
    # Recent events command
    recent_parser = subparsers.add_parser("recent", help="Zeige die letzten Ereignisse")
    recent_parser.add_argument("-n", "--limit", type=int, default=10, help="Anzahl der anzuzeigenden Ereignisse")
    
    # Date events command
    date_parser = subparsers.add_parser("date", help="Zeige Ereignisse für ein bestimmtes Datum")
    date_parser.add_argument("date", help="Datum im Format YYYY-MM-DD")
    
    # Statistics command
    subparsers.add_parser("stats", help="Zeige Statistiken über alle Ereignisse")
    
    args = parser.parse_args()
    
    if not check_database_exists():
        return
    
    if args.command == "recent":
        print_recent_events(args.limit)
    elif args.command == "date":
        print_events_by_date(args.date)
    elif args.command == "stats":
        print_statistics()
    else:
        # If no command is provided, show help
        parser.print_help()

if __name__ == "__main__":
    main()