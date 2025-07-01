"""
Tests for the preprocessing functionality.
"""
import pandas as pd
import pytest
from src.preprocess import clean_reviews


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'review': [
            'Good app',
            'Bad experience',
            'Good app',  # Duplicate
            None,  # Missing review
            '  Needs improvement  '  # Extra whitespace
        ],
        'rating': [5, 2, 5, 1, 3],
        'date': [
            '2024-01-01',
            '2024-01-02',
            '2024-01-01',
            '2024-01-03',
            '2024-01-04'
        ],
        'bank': [
            'CBE',
            'BOA',
            'CBE',
            'Dashen',
            '  CBE  '  # Extra whitespace
        ],
        'source': [
            'Google Play',
            'Google Play',
            'Google Play',
            'Google Play',
            'Google Play'
        ]
    })


def test_clean_reviews_removes_duplicates(sample_data):
    """Test that clean_reviews removes duplicate reviews."""
    cleaned = clean_reviews(sample_data)
    assert len(cleaned) < len(sample_data)
    assert len(cleaned[cleaned['review'] == 'Good app']) == 1


def test_clean_reviews_handles_missing_data(sample_data):
    """Test that clean_reviews handles missing data correctly."""
    cleaned = clean_reviews(sample_data)
    assert cleaned['review'].isna().sum() == 0


def test_clean_reviews_strips_whitespace(sample_data):
    """Test that clean_reviews strips whitespace from text fields."""
    cleaned = clean_reviews(sample_data)
    assert cleaned[cleaned['review'] ==
                   'Needs improvement']['bank'].iloc[0] == 'CBE'


def test_clean_reviews_validates_ratings(sample_data):
    """Test that clean_reviews validates rating values."""
    # Add invalid rating
    sample_data.loc[len(sample_data)] = ['Test', 6,
                                         '2024-01-05', 'CBE', 'Google Play']
    cleaned = clean_reviews(sample_data)
    assert cleaned['rating'].max() <= 5
    assert cleaned['rating'].min() >= 1
