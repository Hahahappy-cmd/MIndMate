# quick_check.py
import sqlite3
import json

conn = sqlite3.connect('mindmate.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT emotion_data, subjectivity, key_phrases 
    FROM journal_entries 
    WHERE id = 3
""")
data = cursor.fetchone()

if data:
    print("🔍 Full AI Analysis of Entry #3:")
    if data[0]:
        emotions = json.loads(data[0])
        print("😊 Emotions:")
        for emotion, score in emotions.items():
            if score > 0:
                print(f"  {emotion}: {score:.2f}")
    
    print(f"📊 Subjectivity: {data[1]:.3f}")
    
    if data[2]:
        phrases = json.loads(data[2])
        print(f"🔑 Key phrases: {phrases}")

conn.close()