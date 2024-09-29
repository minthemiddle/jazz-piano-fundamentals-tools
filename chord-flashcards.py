import random
import time
import sqlite3
from datetime import datetime, timedelta

def generate_chords():
    roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chord_types = [
        ('Maj7', [0, 4, 7, 11]),
        ('m7', [0, 3, 7, 10]),
        ('7', [0, 4, 7, 10])
    ]

    chords = {}
    for root in roots:
        for chord_type, intervals in chord_types:
            chord_symbol = f"{root}{chord_type}"
            notes = ' '.join([roots[(roots.index(root) + interval) % 12] for interval in intervals])
            chords[chord_symbol] = notes

    return chords

def initialize_database():
    conn = sqlite3.connect('jazz_chords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chord_progress
                 (chord_symbol TEXT PRIMARY KEY, next_review TIMESTAMP, interval INTEGER)''')
    conn.commit()
    return conn

def get_next_chord(conn):
    c = conn.cursor()
    c.execute("SELECT chord_symbol FROM chord_progress WHERE next_review <= ? ORDER BY RANDOM() LIMIT 1", (datetime.now(),))
    result = c.fetchone()
    if result:
        return result[0]
    return None

def update_chord_progress(conn, chord_symbol, correct):
    c = conn.cursor()
    c.execute("SELECT interval FROM chord_progress WHERE chord_symbol = ?", (chord_symbol,))
    result = c.fetchone()

    if result is None:
        interval = 1
    else:
        interval = result[0]

    if correct:
        interval *= 2
    else:
        interval = max(1, interval // 2)

    next_review = datetime.now() + timedelta(minutes=interval)

    c.execute('''INSERT OR REPLACE INTO chord_progress (chord_symbol, next_review, interval)
                 VALUES (?, ?, ?)''', (chord_symbol, next_review, interval))
    conn.commit()

def flashcard_practice(chords, conn):
    print("\nFlashcard Practice")
    print("==================")
    print("Type 'q' at any time to quit the practice session.")

    while True:
        chord_symbol = get_next_chord(conn)
        if chord_symbol is None:
            chord_symbol = random.choice(list(chords.keys()))

        print(f"\nChord Symbol: {chord_symbol}")
        input("Press Enter when you're ready to see the notes...")
        print(f"Notes: {chords[chord_symbol]}")

        response = input("Were you correct? (y/n/q): ").lower()
        if response == 'q':
            break
        elif response in ['y', 'n']:
            update_chord_progress(conn, chord_symbol, response == 'y')
            if response == 'n':
                print("Take a moment to study this chord. You'll see it again soon!")
        else:
            print("Invalid input. Please enter 'y', 'n', or 'q'.")

def vamp_practice(chords):
    print("\nVamp Practice")
    print("=============")
    print("Creating a 4-chord vamp progression for you to practice.")

    vamp_chords = random.sample(list(chords.keys()), 4)
    print("\nYour 4-chord vamp progression:")
    for i, chord in enumerate(vamp_chords, 1):
        print(f"{i}. {chord}: {chords[chord]}")

    print("\nPractice this progression in different rhythms:")
    print("1. Two measures per chord")
    print("2. One measure per chord")
    print("3. Two beats per chord")
    print("4. One beat per chord")

    input("\nPress Enter when you're ready to start practicing...")

    for rhythm in ["Two measures", "One measure", "Two beats", "One beat"]:
        print(f"\nPractice with {rhythm} per chord")
        for _ in range(4):  # Repeat the progression 4 times
            for chord in vamp_chords:
                print(chord, end=" ")
                time.sleep(0.5)  # Pause briefly between chords
        print("\n")
        input("Press Enter when you're ready for the next rhythm...")

def main():
    chords = generate_chords()
    conn = initialize_database()

    while True:
        print("\nJazz Chord Practice")
        print("===================")
        print("1. Flashcard Practice")
        print("2. Vamp Practice")
        print("3. Quit")

        choice = input("Choose an option (1/2/3): ")

        if choice == '1':
            flashcard_practice(chords, conn)
        elif choice == '2':
            vamp_practice(chords)
        elif choice == '3':
            print("Thanks for practicing! Goodbye!")
            conn.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
