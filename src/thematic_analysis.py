"""
Module for thematic analysis of bank reviews using TF-IDF and rule-based classification.
"""
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from tqdm import tqdm

# Get the absolute path to the project root directory
PROJECT_ROOT = str(Path(__file__).parent.parent)


def setup_logging():
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(PROJECT_ROOT, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create a timestamp for the log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'thematic_analysis_{timestamp}.log')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )


# Define themes and their associated keywords
THEMES = {
    'Account Access': ['login', 'password', 'authentication', 'access', 'account', 'sign', 'credentials'],
    'Transaction Issues': ['transfer', 'payment', 'transaction', 'send', 'receive', 'money', 'balance'],
    'App Performance': ['slow', 'crash', 'bug', 'error', 'loading', 'freeze', 'performance'],
    'Customer Support': ['support', 'service', 'help', 'contact', 'response', 'assistance', 'agent'],
    'User Interface': ['interface', 'design', 'ui', 'layout', 'button', 'screen', 'menu', 'navigation']
}


class ThematicAnalyzer:
    def __init__(self):
        """Initialize the thematic analyzer with TF-IDF vectorizer."""
        logging.info("Initializing ThematicAnalyzer...")
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            logging.info("TF-IDF vectorizer initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing TF-IDF vectorizer: {str(e)}")
            raise

    def extract_keywords(self, texts):
        """
        Extract keywords using TF-IDF.

        Args:
            texts (list): List of text documents

        Returns:
            list: List of important keywords
        """
        try:
            logging.info("Extracting keywords using TF-IDF...")
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            feature_names = self.vectorizer.get_feature_names_out()

            # Get average TF-IDF scores across all documents
            avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)

            # Get top keywords
            top_indices = avg_scores.argsort()[-20:][::-1]  # Top 20 keywords
            keywords = [feature_names[i] for i in top_indices]

            logging.info(f"Extracted {len(keywords)} keywords successfully")
            return keywords
        except Exception as e:
            logging.error(f"Error extracting keywords: {str(e)}")
            return []

    def classify_themes(self, text):
        """
        Classify text into predefined themes using rule-based approach.

        Args:
            text (str): Text to classify

        Returns:
            list: List of identified themes
        """
        try:
            text = text.lower()
            identified_themes = []

            for theme, keywords in THEMES.items():
                if any(keyword in text for keyword in keywords):
                    identified_themes.append(theme)

            return identified_themes if identified_themes else ['Other']
        except Exception as e:
            logging.error(
                f"Error classifying themes for text: {text[:50]}... Error: {str(e)}")
            return ['Error']

    def analyze_reviews(self, df):
        """
        Perform thematic analysis on reviews.

        Args:
            df (pd.DataFrame): DataFrame containing reviews

        Returns:
            tuple: (DataFrame with theme analysis, dict of keywords by theme)
        """
        logging.info(f"Starting thematic analysis for {len(df)} reviews...")
        results = []
        theme_keywords = defaultdict(list)

        try:
            # Extract overall keywords
            all_keywords = self.extract_keywords(df['review'].tolist())
            logging.info(
                f"Overall top keywords: {', '.join(all_keywords[:10])}")

            # Analyze each review
            for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing themes"):
                try:
                    themes = self.classify_themes(row['review'])

                    # Extract keywords for each theme
                    for theme in themes:
                        if theme != 'Other' and theme != 'Error':
                            theme_keywords[theme].extend(
                                [word for word in all_keywords
                                 if word in row['review'].lower()]
                            )

                    results.append({
                        'review_id': idx + 1,
                        'review_text': row['review'],
                        'rating': row['rating'],
                        'bank': row['bank'],
                        'date': row['date'],
                        'themes': themes
                    })
                except Exception as e:
                    logging.error(
                        f"Error processing review {idx + 1}: {str(e)}")
                    continue

            # Process theme keywords
            for theme in theme_keywords:
                theme_keywords[theme] = list(set(theme_keywords[theme]))

            results_df = pd.DataFrame(results)
            logging.info(
                f"Completed thematic analysis. Processed {len(results_df)} reviews successfully")
            return results_df, dict(theme_keywords)

        except Exception as e:
            logging.error(f"Error in thematic analysis: {str(e)}")
            return pd.DataFrame(), {}


def main():
    """Main function to run thematic analysis on processed reviews."""
    setup_logging()
    logging.info("Starting thematic analysis process...")

    try:
        # Load processed reviews
        input_file = os.path.join(
            PROJECT_ROOT, 'data/processed/processed_reviews.csv')
        logging.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)

        # Initialize analyzer
        analyzer = ThematicAnalyzer()

        # Analyze themes
        results_df, theme_keywords = analyzer.analyze_reviews(df)

        # Save results
        output_dir = os.path.join(PROJECT_ROOT, 'data/processed')
        os.makedirs(output_dir, exist_ok=True)

        # Save theme analysis results
        output_file = os.path.join(output_dir, 'thematic_analysis_results.csv')
        results_df.to_csv(output_file, index=False)
        logging.info(f"Thematic analysis results saved to {output_file}")

        # Save theme keywords
        keywords_file = os.path.join(output_dir, 'theme_keywords.csv')
        keywords_df = pd.DataFrame([
            {'theme': theme, 'keywords': ', '.join(keywords)}
            for theme, keywords in theme_keywords.items()
        ])
        keywords_df.to_csv(keywords_file, index=False)
        logging.info(f"Theme keywords saved to {keywords_file}")

        # Print summary statistics
        logging.info("\nThematic Analysis Summary:")
        theme_counts = results_df.explode('themes')['themes'].value_counts()
        logging.info("\nTheme Distribution:\n" + str(theme_counts))

        # Calculate theme distribution by bank
        theme_by_bank = results_df.explode('themes').groupby(
            'bank')['themes'].value_counts(normalize=True).unstack(fill_value=0) * 100
        theme_by_bank = theme_by_bank.round(2)  # Round to 2 decimal places
        logging.info("\nTheme Distribution by Bank (%):\n" +
                     str(theme_by_bank))

    except Exception as e:
        logging.error(f"Error in thematic analysis process: {str(e)}")
        raise


if __name__ == '__main__':
    main()
