"""
Module for sentiment analysis of bank reviews using DistilBERT.
"""
import pandas as pd
import torch
import logging
import os
from datetime import datetime
from pathlib import Path
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
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
    log_file = os.path.join(log_dir, f'sentiment_analysis_{timestamp}.log')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )


class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analyzer with DistilBERT model."""
        logging.info("Initializing SentimentAnalyzer...")
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"

        try:
            self.tokenizer = DistilBertTokenizer.from_pretrained(
                self.model_name)
            self.model = DistilBertForSequenceClassification.from_pretrained(
                self.model_name)
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model.eval()
            logging.info(
                f"Model loaded successfully. Using device: {self.device}")
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            raise

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single text.

        Args:
            text (str): Text to analyze

        Returns:
            tuple: (sentiment_label, confidence_score)
        """
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(
                    outputs.logits, dim=1)
                prediction = torch.argmax(probabilities, dim=1)
                confidence = torch.max(probabilities)

            # Map prediction to label
            sentiment_map = {0: "negative", 1: "positive"}
            sentiment = sentiment_map[prediction.item()]

            return sentiment, confidence.item()
        except Exception as e:
            logging.error(
                f"Error analyzing sentiment for text: {text[:50]}... Error: {str(e)}")
            return "error", 0.0

    def analyze_reviews(self, df):
        """
        Analyze sentiment for all reviews in the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing reviews

        Returns:
            pd.DataFrame: DataFrame with sentiment analysis results
        """
        logging.info(f"Starting sentiment analysis for {len(df)} reviews...")
        results = []

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing sentiments"):
            try:
                sentiment, confidence = self.analyze_sentiment(row['review'])
                results.append({
                    'review_id': idx + 1,
                    'review_text': row['review'],
                    'rating': row['rating'],
                    'bank': row['bank'],
                    'date': row['date'],
                    'sentiment_label': sentiment,
                    'sentiment_score': confidence
                })
            except Exception as e:
                logging.error(f"Error processing review {idx + 1}: {str(e)}")
                continue

        results_df = pd.DataFrame(results)
        logging.info(
            f"Completed sentiment analysis. Processed {len(results_df)} reviews successfully.")
        return results_df


def main():
    """Main function to run sentiment analysis on processed reviews."""
    setup_logging()
    logging.info("Starting sentiment analysis process...")

    try:
        # Load processed reviews
        input_file = os.path.join(
            PROJECT_ROOT, 'data/processed/processed_reviews.csv')
        logging.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)

        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer()

        # Analyze sentiments
        results_df = analyzer.analyze_reviews(df)

        # Save results
        output_dir = os.path.join(PROJECT_ROOT, 'data/processed')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(
            output_dir, 'sentiment_analysis_results.csv')
        results_df.to_csv(output_file, index=False)
        logging.info(f"Sentiment analysis results saved to {output_file}")

        # Print summary statistics
        logging.info("\nSentiment Analysis Summary:")
        sentiment_summary = results_df.groupby(
            ['bank', 'sentiment_label']).size().unstack(fill_value=0)
        logging.info("\nSentiment by Bank:\n" + str(sentiment_summary))

        score_summary = results_df.groupby('bank')['sentiment_score'].mean()
        logging.info("\nAverage Sentiment Score by Bank:\n" +
                     str(score_summary))

    except Exception as e:
        logging.error(f"Error in sentiment analysis process: {str(e)}")
        raise


if __name__ == '__main__':
    main()
