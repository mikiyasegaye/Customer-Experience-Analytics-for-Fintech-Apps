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

### Task 3: Database Implementation Results

- Successfully implemented PostgreSQL database for storing review data
- Created normalized schema with proper relationships
- Imported 1,199 reviews with 100% data integrity
- Set up automated database dumps and migrations
- Implemented comprehensive database operations module

To run database operations:

```bash
# Initialize database and run migrations
python src/db_operations.py init

# Import scraped data into database
python src/db_operations.py import

# Create database backup
python src/db_operations.py backup
```

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
│       ├── sentiment_analysis_results.csv
│       ├── thematic_analysis_results.csv
│       └── theme_keywords.csv
├── database/          # Database files
│   ├── dumps/         # Database backups
│   └── migrations/    # Schema migrations
├── src/
│   ├── config.py             # Configuration settings
│   ├── scraper.py            # Web scraping functionality
│   ├── preprocess.py         # Data preprocessing functionality
│   ├── sentiment_analysis.py # Sentiment analysis module
│   ├── thematic_analysis.py  # Thematic analysis module
│   ├── db_operations.py      # Database operations
│   └── insights_recommendations.py  # Visualization and insights generation
├── visualizations/    # Generated visualization outputs
│   ├── theme_analysis_dashboard.png
│   ├── sentiment_trends_dashboard.png
│   └── user_experience_dashboard.png
├── logs/             # Analysis and execution logs
└── tests/            # Unit tests
```

## Visualization Dashboards

The project includes three comprehensive visualization dashboards:

### 1. Theme Analysis Dashboard

- Theme Frequency Analysis
- Theme Sentiment Analysis (color-coded)
- Theme Evolution Over Time
- Theme Co-occurrence Network

### 2. Sentiment Trends Dashboard

- Sentiment Score Distribution
- Sentiment Over Time
- Rating vs Sentiment Analysis
- Theme Impact on Sentiment

### 3. User Experience Dashboard

- Rating Distribution Over Time
- Theme Distribution by Rating
- Theme Frequency by Rating Category
- Sentiment-Rating Correlation

To generate visualizations:

```bash
python src/insights_recommendations.py
```

## Analysis Pipeline

1. **Data Collection** (`scraper.py`)

   - Scrapes reviews from Google Play Store
   - Handles rate limiting and error recovery

2. **Preprocessing** (`preprocess.py`)

   - Removes duplicates and invalid entries
   - Standardizes dates and text format

3. **Sentiment Analysis** (`sentiment_analysis.py`)

   - Uses DistilBERT for sentiment classification
   - Generates confidence scores

4. **Thematic Analysis** (`thematic_analysis.py`)

   - Extracts and categorizes themes
   - Identifies key topics and patterns

5. **Database Operations** (`db_operations.py`)

   - Stores processed data
   - Handles backups and migrations

6. **Insights Generation** (`insights_recommendations.py`)
   - Creates visualization dashboards
   - Generates actionable insights
   - Provides strategic recommendations

## Usage

### 1. Data Collection

```bash
# Scrape reviews from Google Play Store
python src/scraper.py

# Output: data/raw/bank_reviews_raw.csv
```

### 2. Data Preprocessing

```bash
# Clean and prepare the data
python src/preprocess.py

# Output: data/processed/preprocessed_reviews.csv
```

### 3. Sentiment Analysis

```bash
# Run sentiment analysis on preprocessed data
python src/sentiment_analysis.py

# Output: data/processed/sentiment_analysis_results.csv
```

### 4. Thematic Analysis

```bash
# Run thematic analysis
python src/thematic_analysis.py

# Outputs:
# - data/processed/thematic_analysis_results.csv
# - data/processed/theme_keywords.csv
```

### 5. Database Operations

```bash
# Initialize database and run migrations
python src/db_operations.py init

# Import processed data
python src/db_operations.py import

# Create database backup
python src/db_operations.py backup

# Outputs:
# - database/dumps/backup_YYYY_MM_DD.sql
```

### 6. Generate Insights and Visualizations

```bash
# Generate analysis dashboards and insights report
python src/insights_recommendations.py

# Outputs:
# - visualizations/theme_analysis_dashboard.png
# - visualizations/sentiment_trends_dashboard.png
# - visualizations/user_experience_dashboard.png
```

## Output Files

### Data Files

1. **Raw Data**

   - `data/raw/bank_reviews_raw.csv`
     - Raw scraped reviews
     - Contains: review text, rating, date, app name, reviewer info

2. **Processed Data**

   - `data/processed/preprocessed_reviews.csv`

     - Cleaned and standardized reviews
     - Contains: cleaned text, normalized dates, bank names

   - `data/processed/sentiment_analysis_results.csv`

     - Sentiment analysis results
     - Contains: review_id, sentiment_label, sentiment_score, confidence

   - `data/processed/thematic_analysis_results.csv`

     - Thematic analysis results
     - Contains: review_id, themes (list), theme_confidence

   - `data/processed/theme_keywords.csv`
     - Theme definitions and keywords
     - Contains: theme_name, keywords, description

### Visualization Outputs

1. **Theme Analysis Dashboard** (`visualizations/theme_analysis_dashboard.png`)

   - Theme frequency distribution
   - Sentiment by theme
   - Theme evolution over time
   - Theme correlations

2. **Sentiment Trends Dashboard** (`visualizations/sentiment_trends_dashboard.png`)

   - Overall sentiment distribution
   - Temporal sentiment trends
   - Rating-sentiment relationships
   - Theme sentiment impact

3. **User Experience Dashboard** (`visualizations/user_experience_dashboard.png`)
   - Rating trends
   - Theme-rating relationships
   - High vs low rating analysis
   - Sentiment-rating correlation

### Database Files

1. **Schema Migrations**

   - `database/migrations/*.sql`
   - Database structure and relationship definitions

2. **Backups**
   - `database/dumps/backup_YYYY_MM_DD.sql`
   - Daily database snapshots
   - Complete data preservation

### Log Files

- `logs/scraping_log.txt`: Data collection process logs
- `logs/analysis_log.txt`: Analysis execution logs
- `logs/error_log.txt`: Error tracking and debugging info
