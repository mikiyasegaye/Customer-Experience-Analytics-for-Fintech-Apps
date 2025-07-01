"""
Script to preprocess and clean the scraped reviews data.
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path


def load_data(data_dir: str = 'data/raw') -> pd.DataFrame:
    """
    Load all review data files from the raw data directory.

    Args:
        data_dir (str): Directory containing the raw CSV files

    Returns:
        pd.DataFrame: Combined DataFrame containing all reviews
    """
    try:
        # Get all review CSV files
        data_path = Path(data_dir)
        review_files = list(data_path.glob('*_reviews_*.csv'))

        if not review_files:
            print(f"No review files found in {data_dir}")
            return pd.DataFrame()

        # Read and combine all files
        dfs = []
        for file in review_files:
            df = pd.read_csv(file)
            # Rename columns to match expected format if needed
            column_mapping = {
                'review_text': 'review',
                'bank_name': 'bank'
            }
            df = df.rename(columns=column_mapping)
            dfs.append(df)

        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        print(
            f"Loaded {len(review_files)} files with total {len(combined_df)} reviews")
        return combined_df

    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the reviews data.

    Args:
        df (pd.DataFrame): Raw reviews DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    if df.empty:
        return df

    # Create a copy to avoid modifying the original
    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['review', 'bank', 'date'])

    # Remove rows where review is empty or NaN
    df = df.dropna(subset=['review'])

    # Convert date to datetime if not already
    df['date'] = pd.to_datetime(df['date'])

    # Normalize date format
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Ensure rating is numeric
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Remove rows with invalid ratings
    df = df[df['rating'].between(1, 5)]

    # Strip whitespace from text columns
    df['review'] = df['review'].str.strip()
    df['bank'] = df['bank'].str.strip()

    return df


def save_processed_data(df: pd.DataFrame, output_dir: str = 'data/processed'):
    """
    Save the processed data to CSV files.

    Args:
        df (pd.DataFrame): Processed DataFrame
        output_dir (str): Directory to save the processed files
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save combined processed data
        df.to_csv(f'{output_dir}/processed_reviews.csv', index=False)

        # Save individual bank files
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            bank_df.to_csv(
                f'{output_dir}/{bank.lower()}_processed_reviews.csv',
                index=False
            )

        print(f"Processed data saved to {output_dir}/")

    except Exception as e:
        print(f"Error saving processed data: {str(e)}")


def main():
    """Main function to process the reviews data."""
    # Load raw data
    raw_data = load_data()

    if raw_data.empty:
        print("No data to process!")
        return

    # Clean and process the data
    processed_data = clean_reviews(raw_data)

    # Print some statistics
    print("\nProcessing Statistics:")
    print(f"Original reviews: {len(raw_data)}")
    print(f"Processed reviews: {len(processed_data)}")
    print("\nReviews per bank:")
    print(processed_data['bank'].value_counts())

    # Save the processed data
    save_processed_data(processed_data)


if __name__ == '__main__':
    main()
