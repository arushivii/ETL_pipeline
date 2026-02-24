import requests
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv('NEWS_API_KEY')

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="news_pipeline",
        user="postgres",
        password=os.getenv('POSTGRES_PASSWORD'),
        port=5432
    )

def get_last_24h_timestamp():
    """Get timestamp for 24 hours ago"""
    from datetime import timedelta
    
    timestamp_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    logger.info(f"Fetching articles from last 24 hours (since {timestamp_24h_ago})")
    return timestamp_24h_ago

def get_last_published_timestamp():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(published_at) 
            FROM raw_articles
        """)
        
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if result:
            logger.info(f"Last article in DB published at: {result}")
            return result
        else:
            logger.info("No articles in database yet")
            return None
            
    except Exception as e:
        logger.error(f"Error getting last timestamp: {e}")
        return None

def fetch_articles(from_date=None):
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
        
        if from_date:
            from_str = from_date.strftime('%Y-%m-%dT%H:%M:%S')
            url += f'&from={from_str}'
            logger.info(f"Fetching articles from {from_str} onwards")
        else:
            logger.info("Fetching all recent articles (first run)")
        
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'ok':
            logger.info(f"Fetched {len(data['articles'])} articles from NewsAPI")
            return data['articles']
        else:
            logger.error(f"API Error: {data}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def load_to_database(articles):
    if not articles:
        logger.info("No articles to load")
        return 0
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        duplicate_count = 0
        error_count = 0
        
        for article in articles:
            try:
                source_id = article['source']['id']
                source_name = article['source']['name']
                author = article.get('author')
                title = article['title']
                description = article.get('description')
                url = article['url']
                published_at = article['publishedAt']
                content = article.get('content')
                
                published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                
                insert_query = """
                    INSERT INTO raw_articles 
                    (source_id, source_name, author, title, description, url, published_at, content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    source_id, source_name, author, title, 
                    description, url, published_dt, content
                ))
                
                inserted_count += 1
                
            except psycopg2.errors.UniqueViolation:
                # Article already exists (duplicate URL)
                conn.rollback()
                duplicate_count += 1
                continue
                
            except Exception as e:
                logger.error(f"Error inserting article '{title}': {e}")
                conn.rollback()
                error_count += 1
                continue
        
        conn.commit()
        
        logger.info(f"Inserted {inserted_count} new articles")
        logger.info(f"Skipped {duplicate_count} duplicates")
        if error_count > 0:
            logger.warning(f"{error_count} errors occurred")
        
        cursor.close()
        conn.close()
        
        return inserted_count
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return 0

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Starting Incremental ETL Pipeline")
    logger.info("=" * 50)
    
    try:
        # Step 1: Get last timestamp from database
        last_timestamp = get_last_published_timestamp()
        
        # Step 2: Fetch new articles
        articles = fetch_articles(from_date=last_timestamp)
        
        # Step 3: Load to database
        if articles:
            inserted = load_to_database(articles)
            
            if inserted > 0:
                logger.info("\nPipeline completed successfully!")
                logger.info(f"Loaded {inserted} new articles")
            else:
                logger.info("\nPipeline ran but no new articles were added")
        else:
            logger.info("\nPipeline completed - no new articles found")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        
    logger.info("=" * 50)