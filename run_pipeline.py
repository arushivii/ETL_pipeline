import logging
from extract_load import fetch_articles, load_to_database, get_last_published_timestamp
from transform import transform_articles, create_daily_summary

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_full_pipeline():
    """Run the complete ETL pipeline"""
    logger.info("=" * 60)
    logger.info("RUNNING FULL DATA PIPELINE")
    logger.info("=" * 60)
    
    # Step 1: Extract and Load
    logger.info("\n[1/3] EXTRACT & LOAD")
    logger.info("-" * 60)
    last_timestamp = get_last_published_timestamp()
    articles = fetch_articles(from_date=last_timestamp)
    inserted = load_to_database(articles)
    
    if inserted == 0:
        logger.info("No new articles - skipping transformation")
        logger.info("\n" + "=" * 60)
        logger.info("✓ PIPELINE COMPLETED (No new data)")
        logger.info("=" * 60)
        return
    
    # Step 2: Transform
    logger.info("\n[2/3] TRANSFORM")
    logger.info("-" * 60)
    transform_articles()
    
    # Step 3: Summarize
    logger.info("\n[3/3] SUMMARIZE")
    logger.info("-" * 60)
    create_daily_summary()
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ FULL PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_full_pipeline()