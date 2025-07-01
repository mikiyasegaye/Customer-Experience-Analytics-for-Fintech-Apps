"""
Tests for the scraper functionality.
"""
from config import BANKS, SCRAPER_CONFIG, DATA_DIRS, SCHEDULE_CONFIG
from scraper import scrape_bank_reviews, save_reviews
import os
import json
from datetime import datetime
import pytest
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))


def test_bank_ids_exist():
    """Test that all bank IDs are defined."""
    assert len(BANKS) == 3
    assert all(isinstance(app_id, str) for app_id in BANKS.values())
    assert all(isinstance(bank, str) for bank in BANKS.keys())
    assert all('com.' in app_id for app_id in BANKS.values())


def test_scraper_config():
    """Test that scraper configuration is valid."""
    assert isinstance(SCRAPER_CONFIG['max_retries'], int)
    assert SCRAPER_CONFIG['max_retries'] > 0
    assert isinstance(SCRAPER_CONFIG['retry_delay'], (int, float))
    assert SCRAPER_CONFIG['retry_delay'] > 0
    assert isinstance(SCRAPER_CONFIG['target_reviews'], int)
    assert SCRAPER_CONFIG['target_reviews'] > 0


def test_schedule_config():
    """Test that schedule configuration is valid."""
    assert isinstance(SCHEDULE_CONFIG['enabled'], bool)
    assert SCHEDULE_CONFIG['schedule_type'] in [
        'daily', 'interval', 'weekly', 'hourly']
    if SCHEDULE_CONFIG['schedule_type'] == 'daily':
        assert isinstance(SCHEDULE_CONFIG['daily_time'], str)
        assert ':' in SCHEDULE_CONFIG['daily_time']


@pytest.mark.integration
def test_scrape_bank_reviews():
    """Test that scrape_bank_reviews returns reviews data."""
    # Test with CBE app
    reviews_data = scrape_bank_reviews('CBE', BANKS['CBE'])
    assert isinstance(reviews_data, list)

    if reviews_data:
        review = reviews_data[0]
        assert 'content' in review
        assert 'score' in review
        assert 'at' in review
        assert isinstance(review['score'], (int, float))
        assert 1 <= review['score'] <= 5


@pytest.mark.integration
def test_save_reviews(tmp_path):
    """Test that save_reviews creates the expected files."""
    # Create test data
    test_data = [{
        'content': 'Test review',
        'score': 5,
        'at': datetime.now()
    }]

    # Temporarily modify DATA_DIRS to use tmp_path
    original_raw_dir = DATA_DIRS['raw']
    DATA_DIRS['raw'] = str(tmp_path)

    try:
        save_reviews(test_data, 'TestBank')

        # Check if files were created
        files = os.listdir(tmp_path)
        csv_files = [f for f in files if f.endswith('.csv')]
        json_files = [f for f in files if f.endswith('.json')]

        assert len(csv_files) == 1
        assert len(json_files) == 1

        # Check CSV content
        csv_path = os.path.join(tmp_path, csv_files[0])
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test review' in content
            assert 'TestBank' in content

        # Check metadata
        json_path = os.path.join(tmp_path, json_files[0])
        with open(json_path, 'r') as f:
            metadata = json.load(f)
            assert metadata['bank'] == 'TestBank'
            assert metadata['total_reviews'] == 1

    finally:
        # Restore original DATA_DIRS
        DATA_DIRS['raw'] = original_raw_dir
