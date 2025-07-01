"""
Configuration settings for the app review scraper.
"""

# Bank app IDs on Google Play Store
BANKS = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "Dashen": "com.dashen.dashensuperapp"
}

# Scraper configuration
SCRAPER_CONFIG = {
    'max_retries': 3,
    'retry_delay': 2,  # seconds
    'target_reviews': 400,  # reduced to meet minimum requirements
    'lang': 'en',
    'country': 'et'
}

# Logging configuration
LOG_CONFIG = {
    'filename': 'logs/scraper.log',
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Data directories
DATA_DIRS = {
    'raw': 'data/raw',
    'processed': 'data/processed',
    'logs': 'logs'
}
