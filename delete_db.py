import sqlite3

# Verbindung mit der Datenbank herstellen
conn = sqlite3.connect("./db.sqlite3")
cursor = conn.cursor()

# Alle Tabellen in der Datenbank abrufen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Für jede Tabelle eine DELETE-Anweisung ausführen
for table in tables:
    table_name = table[0]
    cursor.execute(f"DELETE FROM {table_name};")

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()
print('Deleting complete!')