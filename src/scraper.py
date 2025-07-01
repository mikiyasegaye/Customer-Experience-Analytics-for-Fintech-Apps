"""
Script to scrape reviews from Google Play Store for Ethiopian banking apps.
"""
from config import BANKS, SCRAPER_CONFIG, DATA_DIRS, LOG_CONFIG
import os
import csv
import json
import time
import logging
from datetime import datetime
from google_play_scraper import Sort, reviews

# Import config from the same directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Get the absolute path to the project root directory
PROJECT_ROOT = str(Path(__file__).parent.parent)


def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.join(PROJECT_ROOT, DATA_DIRS['logs'])
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, os.path.basename(LOG_CONFIG['filename']))
    logging.basicConfig(
        filename=log_file,
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format']
    )


def scrape_bank_reviews(bank_name: str, app_id: str) -> list:
    """
    Scrape reviews for a specific bank's app.

    Args:
        bank_name (str): Name of the bank
        app_id (str): Google Play Store app ID

    Returns:
        list: List of review dictionaries
    """
    logging.info(f"🔄 Fetching reviews for {bank_name}...")
    retries = 0

    while retries < SCRAPER_CONFIG['max_retries']:
        try:
            results, _ = reviews(
                app_id,
                lang=SCRAPER_CONFIG['lang'],
                country=SCRAPER_CONFIG['country'],
                sort=Sort.NEWEST,
                count=SCRAPER_CONFIG['target_reviews'],
                filter_score_with=None
            )

            logging.info(
                f"✅ Successfully fetched {len(results)} reviews for {bank_name}")
            return results

        except Exception as e:
            retries += 1
            logging.error(
                f"Error scraping {bank_name} (Attempt {retries}): {str(e)}")

            if retries < SCRAPER_CONFIG['max_retries']:
                sleep_time = SCRAPER_CONFIG['retry_delay']
                logging.info(
                    f"Waiting {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)

    logging.error(
        f"❌ Failed to scrape reviews for {bank_name} after {SCRAPER_CONFIG['max_retries']} attempts")
    return []


def save_reviews(reviews_data: list, bank_name: str):
    """
    Save reviews to CSV file.

    Args:
        reviews_data (list): List of review dictionaries
        bank_name (str): Name of the bank
    """
    if not reviews_data:
        return

    raw_dir = os.path.join(PROJECT_ROOT, DATA_DIRS['raw'])
    os.makedirs(raw_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(
        raw_dir, f'{bank_name.lower()}_reviews_{timestamp}.csv')

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file, fieldnames=['review_text', 'rating', 'date', 'bank_name', 'source'])
            writer.writeheader()

            for entry in reviews_data:
                writer.writerow({
                    'review_text': entry['content'],
                    'rating': entry['score'],
                    'date': entry['at'].strftime('%Y-%m-%d'),
                    'bank_name': bank_name,
                    'source': 'Google Play'
                })

        logging.info(f"✅ Saved reviews to {filename}")

        # Save metadata
        metadata = {
            'bank': bank_name,
            'total_reviews': len(reviews_data),
            'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'config_used': SCRAPER_CONFIG
        }

        metadata_file = os.path.join(
            raw_dir, f'{bank_name.lower()}_metadata_{timestamp}.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)

    except Exception as e:
        logging.error(f"Error saving reviews for {bank_name}: {str(e)}")


def main():
    """Main function to scrape reviews for all banks."""
    setup_logging()
    logging.info("🎯 Bank Review Scraper Started")

    for bank_name, app_id in BANKS.items():
        reviews_data = scrape_bank_reviews(bank_name, app_id)
        save_reviews(reviews_data, bank_name)

    logging.info("✨ Completed review scraping process")


if __name__ == '__main__':
    main()
