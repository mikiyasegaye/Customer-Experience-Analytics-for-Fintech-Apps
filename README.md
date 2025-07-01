# Customer Experience Analytics for Fintech Apps

## Project Overview

This project analyzes customer satisfaction with mobile banking apps by collecting and processing user reviews from the Google Play Store for three Ethiopian banks:

- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

## Methodology

### Data Collection

- **Source**: Google Play Store reviews using google-play-scraper library
- **Sample Size**: 400 reviews per bank (1,200 total reviews)
- **Banks Covered**:
  - CBE (com.combanketh.mobilebanking)
  - BOA (com.boa.boaMobileBanking)
  - Dashen Bank (com.dashen.dashensuperapp)

### Data Preprocessing

1. **Duplicate Removal**:

   - Identifies and removes duplicate reviews based on text, bank, and date
   - Ensures data quality and prevents bias from repeated entries

2. **Missing Data Handling**:

   - Removes rows with missing review text
   - Ensures ratings are valid (1-5 scale)

3. **Date Standardization**:

   - Converts all dates to YYYY-MM-DD format
   - Ensures consistent temporal analysis

4. **Text Cleaning**:
   - Strips whitespace from review text and bank names
   - Maintains data consistency

### Output Format

- Processed data saved in CSV format with columns:
  - review: Review text
  - rating: Numeric rating (1-5)
  - date: Review date (YYYY-MM-DD)
  - bank: Bank name
  - source: 'Google Play'

## Setup

1. Clone the repository

```bash
git clone https://github.com/mikiyasegaye/Customer-Experience-Analytics-for-Fintech-Apps.git
cd Customer-Experience-Analytics-for-Fintech-Apps
```

2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── data/
│   └── raw/           # Raw scraped data
│   └── processed/     # Cleaned and preprocessed data
├── src/
│   ├── config.py     # Configuration settings
│   ├── scraper.py    # Web scraping functionality
│   └── preprocess.py # Data preprocessing functionality
└── tests/            # Unit tests
```

## Usage

To scrape reviews:

```bash
python src/scraper.py
```

To preprocess data:

```bash
python src/preprocess.py
```
