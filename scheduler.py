import schedule
import time
import logging
from datetime import datetime
from run_pipeline import run_full_pipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),  # Save logs to file
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

def job():
    logger.info("="*70)
    logger.info(f"SCHEDULED RUN STARTED AT {datetime.now()}")
    logger.info("="*70)
    
    try:
        run_full_pipeline()
        logger.info("Scheduled run completed successfully")
    except Exception as e:
        logger.error(f"Scheduled run failed: {e}")
    
    logger.info("="*70)
    logger.info(f"Next run scheduled in 1 hour")
    logger.info("="*70 + "\n")

# Schedule the job to run every hour
schedule.every(2).minutes.do(job)


logger.info("Pipeline scheduler started")
logger.info("Running initial pipeline execution...")
job()

logger.info("\nScheduler is now running. Press Ctrl+C to stop.")
logger.info("Pipeline will run every 1 hour.")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute if it's time to run