import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="news_pipeline",
    user="postgres",
    password=os.getenv('POSTGRES_PASSWORD'),
    port=5432
)

cursor = conn.cursor()

print("=" * 60)
print("DATA PIPELINE STATUS")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM raw_articles")
raw_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM cleaned_articles")
cleaned_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM daily_summary")
summary_count = cursor.fetchone()[0]

print(f"\n📊 Article Counts:")
print(f"  Raw articles:     {raw_count}")
print(f"  Cleaned articles: {cleaned_count}")
print(f"  Summary records:  {summary_count}")

cursor.execute("""
    SELECT source_name, title, word_count, published_at
    FROM cleaned_articles
    ORDER BY published_at DESC
    LIMIT 5
""")

print(f"\n Latest Articles:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[1][:50]}... ({row[2]} words)")

cursor.execute("""
    SELECT date, source_name, article_count, avg_word_count
    FROM daily_summary
    ORDER BY date DESC, article_count DESC
    LIMIT 8
""")

print(f"\n Daily Summary (Top Sources by Date):")
for row in cursor.fetchall():
    avg_words = row[3] if row[3] is not None else 0
    print(f"  {row[0]} | {row[1]:20} | {row[2]:2} articles | Avg: {avg_words:4} words")

cursor.execute("""
    SELECT source_name, COUNT(*) as count
    FROM cleaned_articles
    GROUP BY source_name
    ORDER BY count DESC
    LIMIT 5
""")

print(f"\n Top News Sources:")
for row in cursor.fetchall():
    print(f"  {row[0]:30} | {row[1]} articles")

print("\n" + "=" * 60)

cursor.close()
conn.close()