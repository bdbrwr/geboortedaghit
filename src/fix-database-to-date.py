import sqlite3
from datetime import datetime, timedelta

DB_PATH = "geboortedaghit.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, from_date, to_date FROM charts ORDER BY from_date")
    rows = cursor.fetchall()

    updates = 0

    for i in range(len(rows) - 1):
        current_id, current_from, current_to = rows[i]
        next_id, next_from, _ = rows[i + 1]

        current_to_date = datetime.strptime(current_to, "%Y-%m-%d").date()
        next_from_date = datetime.strptime(next_from, "%Y-%m-%d").date()

        expected_to = next_from_date - timedelta(days=1)

        if current_to_date != expected_to:
            print(f"Updating chart ID {current_id}: to_date {current_to_date} -> {expected_to}")
            cursor.execute("""
                UPDATE charts SET to_date = ? WHERE id = ?
            """, (expected_to.isoformat(), current_id))
            updates += 1

    conn.commit()
    conn.close()
    print(f"Fixed {updates} chart(s)")

if __name__ == "__main__":
    main()
