# Customer Experience Analytics for Fintech Apps

## Project Overview

This project analyzes customer satisfaction with mobile banking apps by collecting and processing user reviews from the Google Play Store for three Ethiopian banks:

- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

## Current Status and Findings

### Data Collection Results

- Successfully collected 1,199 unique reviews across three banks
- Implemented automated scraping with error handling and rate limiting
- Achieved 99.9% data completeness (1,199 out of 1,200 target)

### Sentiment Analysis Results

Bank-wise sentiment distribution:

- BOA: 342 negative, 58 positive (85.5% negative)
- CBE: 315 negative, 85 positive (78.8% negative)
- Dashen: 102 negative, 297 positive (74.4% positive)

Average confidence scores:

- BOA: 98.63%
- CBE: 97.46%
- Dashen: 98.57%

### Thematic Analysis Results

Five major themes identified across reviews:

1. Transaction Issues (361 reviews)

   - CBE: 34.04%
   - BOA: 14.69%
   - Dashen: 13.89%

2. App Performance (214 reviews)

   - BOA: 21.84%
   - CBE: 13.07%
   - Dashen: 4.49%

3. Account Access (198 reviews)

   - CBE: 16.87%
   - BOA: 11.02%
   - Dashen: 7.05%

4. User Interface (162 reviews)

   - CBE: 14.13%
   - Dashen: 7.48%
   - BOA: 6.94%

5. Customer Support (132 reviews)
   - CBE: 10.94%
   - BOA: 6.33%
   - Dashen: 6.20%

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

### Analysis Methods

1. **Sentiment Analysis**:

   - Uses DistilBERT model for binary classification
   - Provides confidence scores for each prediction
   - Processes all reviews with 100% coverage

2. **Thematic Analysis**:
   - TF-IDF vectorization for keyword extraction
   - Rule-based theme classification
   - Five major themes identified and tracked
   - Cross-bank theme comparison

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
│   ├── raw/           # Raw scraped data
│   └── processed/     # Cleaned and preprocessed data
├── src/
│   ├── config.py              # Configuration settings
│   ├── scraper.py            # Web scraping functionality
│   ├── preprocess.py         # Data preprocessing functionality
│   ├── sentiment_analysis.py # Sentiment analysis module
│   └── thematic_analysis.py  # Thematic analysis module
├── logs/              # Analysis and execution logs
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

To run sentiment analysis:

```bash
python src/sentiment_analysis.py
```

To run thematic analysis:

```bash
python src/thematic_analysis.py
```

## Output Files

The analysis generates several output files:

1. `data/processed/processed_reviews.csv`: Cleaned and preprocessed reviews
2. `data/processed/sentiment_analysis_results.csv`: Sentiment analysis results
3. `data/processed/thematic_analysis_results.csv`: Theme classification results
4. `data/processed/theme_keywords.csv`: Keywords associated with each theme
5. `logs/`: Detailed execution logs with timestamps
