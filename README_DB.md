# MQTT Occupancy Monitor mit SQLite-Datenbank

Diese erweiterte Version des MQTT Occupancy Monitors speichert Anwesenheitsdaten in einer SQLite-Datenbank. Sie behält alle Funktionen der Originalversion bei und fügt Datenbankfunktionalität hinzu.

## Neue Funktionen

- Automatische Erstellung einer SQLite-Datenbank beim ersten Start
- Speicherung aller Anwesenheitsereignisse mit Zeitstempel
- Abfragemöglichkeiten für historische Daten

## Dateien

- `mqtt_occupancy_monitor_db.py`: Hauptskript mit Datenbankintegration
- `occupancy_db_query.py`: Hilfsskript zum Abfragen der gespeicherten Daten
- `occupancy_data.db`: SQLite-Datenbankdatei (wird automatisch erstellt)

## Installation

1. Installieren Sie die erforderlichen Abhängigkeiten:

```bash
pip3 install -r requirements.txt
```

2. Machen Sie die Skripte ausführbar (optional):

```bash
chmod +x mqtt_occupancy_monitor_db.py
chmod +x occupancy_db_query.py
```

## Verwendung

### Starten des Monitors mit Datenbankunterstützung

```bash
python3 mqtt_occupancy_monitor_db.py
```

Beim ersten Start wird die Datenbank automatisch erstellt. Das Skript verbindet sich mit dem MQTT-Broker und beginnt, Anwesenheitsereignisse zu überwachen und in der Datenbank zu speichern.

### Abfragen der Datenbank

Das Skript `occupancy_db_query.py` bietet verschiedene Möglichkeiten, die gespeicherten Daten abzufragen:

#### Anzeigen der letzten Ereignisse

```bash
python3 occupancy_db_query.py recent
```

Optional können Sie die Anzahl der anzuzeigenden Ereignisse angeben:

```bash
python3 occupancy_db_query.py recent -n 20
```

#### Anzeigen von Ereignissen für ein bestimmtes Datum

```bash
python3 occupancy_db_query.py date 2023-05-15
```

#### Anzeigen von Statistiken

```bash
python3 occupancy_db_query.py stats
```

## Datenbankstruktur

Die Datenbank enthält eine Tabelle `occupancy_events` mit folgenden Feldern:

- `id`: Eindeutige ID (automatisch inkrementiert)
- `timestamp`: Zeitstempel des Ereignisses
- `occupancy`: Anwesenheitsstatus (1 = anwesend, 0 = abwesend)
- `raw_data`: Rohdaten der MQTT-Nachricht (JSON)

## Konfiguration

Die Konfigurationsparameter sind die gleichen wie beim Original-Monitor, mit einer zusätzlichen Einstellung für die Datenbankdatei:

- `DB_FILE`: Pfad zur SQLite-Datenbankdatei (Standard: "occupancy_data.db")

## Hinweise

- Die Datenbank wird im gleichen Verzeichnis wie das Skript erstellt
- Alle Zeitstempel werden im ISO-Format gespeichert
- Die Abfragen sind auf Deutsch lokalisiert