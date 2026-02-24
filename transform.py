import psycopg2
import re

from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="news_pipeline",
        user="postgres",
        password=os.getenv('POSTGRES_PASSWORD'),
        port=5432
    )

def clean_text(text):
    if text is None:
        return None
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def count_words(text):
    if text is None or text == '':
        return 0
    return len(text.split())

def transform_articles():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, source_id, source_name, author, title, 
               description, url, published_at, content, pulled_at
        FROM raw_articles
        WHERE url NOT IN (SELECT url FROM cleaned_articles)
    """)
    
    raw_articles = cursor.fetchall()
    
    if not raw_articles:
        print("No new articles to transform")
        cursor.close()
        conn.close()
        return
    
    print(f"Transforming {len(raw_articles)} articles...")
    
    for article in raw_articles:
        (id, source_id, source_name, author, title, 
         description, url, published_at, content, pulled_at) = article
        
        cleaned_title = clean_text(title)
        cleaned_description = clean_text(description)
        cleaned_content = clean_text(content)
        word_count = count_words(cleaned_content)
        
        try:
            insert_query = """
                INSERT INTO cleaned_articles 
                (source_id, source_name, author, title, description, 
                 url, published_at, content, word_count, pulled_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                source_id, source_name, author, cleaned_title, 
                cleaned_description, url, published_at, cleaned_content,
                word_count, pulled_at
            ))
            
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    print(f"Transformed {len(raw_articles)} articles")
    
    cursor.close()
    conn.close()

def create_daily_summary():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM daily_summary")
    
    cursor.execute("""
        INSERT INTO daily_summary (date, source_name, article_count)
        SELECT 
            DATE(published_at) as date,
            source_name,
            COUNT(*) as article_count
        FROM cleaned_articles
        GROUP BY DATE(published_at), source_name
        ORDER BY date DESC, source_name
    """)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM daily_summary")
    count = cursor.fetchone()[0]
    print(f" Created {count} daily summary records")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("Starting transformation pipeline...\n")
    transform_articles()
    print("\nCreating daily summary...")
    create_daily_summary()
    print("\nTransformation pipeline completed!")