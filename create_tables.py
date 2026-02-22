import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="news_pipeline",
    user="postgres",
    password="Reddit00#",
    port=5432
)

cursor = conn.cursor()

# Drop old tables first (clean slate)
cursor.execute("DROP TABLE IF EXISTS daily_summary")
cursor.execute("DROP TABLE IF EXISTS cleaned_articles")
print("✓ Dropped old tables")

# Create cleaned_articles (NO sentiment)
create_cleaned_articles = """
CREATE TABLE IF NOT EXISTS cleaned_articles (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(100),
    source_name VARCHAR(255),
    author VARCHAR(255),
    title TEXT NOT NULL,
    description TEXT,
    url TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP,
    content TEXT,
    word_count INTEGER,
    pulled_at TIMESTAMP
);
"""

# Create daily_summary (NO sentiment)
create_daily_summary = """
CREATE TABLE IF NOT EXISTS daily_summary (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    source_name VARCHAR(255),
    article_count INTEGER,
    avg_word_count INTEGER,
    UNIQUE(date, source_name)
);
"""

cursor.execute(create_cleaned_articles)
print("✓ cleaned_articles table created")

cursor.execute(create_daily_summary)
print("✓ daily_summary table created")

conn.commit()

cursor.close()
conn.close()

print("\n✓ All tables created successfully!")