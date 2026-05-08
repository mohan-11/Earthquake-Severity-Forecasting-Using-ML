import sqlite3
import pandas as pd

conn = sqlite3.connect("earthquake.db")

df = pd.read_sql_query("SELECT * FROM earthquakes", conn)

print("Total rows:", len(df))
print("\nClass distribution:")
print(df['alert_level'].value_counts())

conn.close()