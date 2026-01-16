import sqlite3

conn = sqlite3.connect("backend/talentlens.db")
cur = conn.cursor()

tables = ['users', 'resumes', 'jobs', 'matches', 'recommendations']

for table in tables:
    print(f"\n=== {table.upper()} ===")
    cur.execute(f"PRAGMA table_info({table})")
    for row in cur.fetchall():
        print(f"  {row[1]:25} {row[2]:15} {'NOT NULL' if row[3] else ''} {'PK' if row[5] else ''}")

conn.close()
