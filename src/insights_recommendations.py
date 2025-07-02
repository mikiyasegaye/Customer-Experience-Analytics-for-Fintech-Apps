#!/usr/bin/env python3
"""
Task 4: Customer Experience Insights and Recommendations
Ethiopian Bank Mobile App Analysis

Complete analysis including:
- Key drivers and pain points identification
- Bank-wise comparison (CBE vs BOA vs Dashen)
- Comprehensive visualizations
- Strategic recommendations
- Ethical considerations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import ast
from collections import Counter
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

# Set style for all plots
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10


def load_and_prepare_data():
    """Load and prepare all datasets for analysis."""
    print("📊 Loading and preparing data...")

    # Load datasets
    sentiment_df = pd.read_csv('data/processed/sentiment_analysis_results.csv')
    themes_df = pd.read_csv('data/processed/thematic_analysis_results.csv')

    # Convert themes from string to list
    themes_df['themes'] = themes_df['themes'].apply(ast.literal_eval)

    # Convert dates
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    themes_df['date'] = pd.to_datetime(themes_df['date'])

    # Merge datasets
    df = themes_df.merge(
        sentiment_df[['review_id', 'sentiment_label', 'sentiment_score']],
        on='review_id'
    )

    print(f"✓ Loaded {len(df):,} reviews")
    return df


def create_theme_analysis_dashboard(df):
    """Create a comprehensive theme analysis dashboard."""
    print("📈 Generating theme analysis visualizations...")

    # Create figure with custom layout
    fig = plt.figure(figsize=(20, 15))
    gs = GridSpec(2, 2, figure=fig)

    # 1. Theme Frequency Analysis
    ax1 = fig.add_subplot(gs[0, 0])
    theme_counts = Counter([theme for themes in df['themes']
                           for theme in themes])
    theme_df = pd.DataFrame.from_dict(theme_counts, orient='index', columns=[
                                      'count']).sort_values('count', ascending=True)

    ax1.barh(y=range(len(theme_df)),
             width=theme_df['count'], color=sns.color_palette()[0])
    ax1.set_yticks(range(len(theme_df)))
    ax1.set_yticklabels(theme_df.index)
    ax1.set_title('Theme Frequency Analysis')
    ax1.set_xlabel('Number of Mentions')

    # 2. Theme Sentiment Analysis
    ax2 = fig.add_subplot(gs[0, 1])
    theme_sentiments = []
    for themes, score in zip(df['themes'], df['sentiment_score']):
        for theme in themes:
            theme_sentiments.append({'theme': theme, 'sentiment': score})

    theme_sentiment_df = pd.DataFrame(theme_sentiments)
    theme_avg_sentiment = theme_sentiment_df.groupby(
        'theme')['sentiment'].agg(['mean', 'count']).sort_values('mean')

    colors = ['red' if x < 0.5 else 'green' for x in theme_avg_sentiment['mean']]
    ax2.barh(y=range(len(theme_avg_sentiment)),
             width=theme_avg_sentiment['mean'], color=colors)
    ax2.set_yticks(range(len(theme_avg_sentiment)))
    ax2.set_yticklabels(theme_avg_sentiment.index)
    ax2.set_title('Average Sentiment Score by Theme')
    ax2.set_xlabel('Average Sentiment (Red: Negative, Green: Positive)')

    # 3. Theme Evolution Over Time
    ax3 = fig.add_subplot(gs[1, 0])
    df['month'] = df['date'].dt.to_period('M')
    monthly_themes = df.groupby('month')['themes'].agg(
        lambda x: Counter([theme for themes in x for theme in themes]))

    top_themes = ['Transaction Issues', 'Account Access',
                  'App Performance', 'User Interface']
    theme_evolution = pd.DataFrame({
        theme: [count[theme] if theme in count else 0 for count in monthly_themes]
        for theme in top_themes
    }, index=monthly_themes.index)

    theme_evolution.plot(ax=ax3, marker='o')
    ax3.set_title('Theme Evolution Over Time')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Number of Mentions')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # 4. Theme Co-occurrence Network
    ax4 = fig.add_subplot(gs[1, 1])
    co_occurrence = np.zeros((len(theme_counts), len(theme_counts)))
    theme_list = list(theme_counts.keys())

    for themes in df['themes']:
        for i, theme1 in enumerate(theme_list):
            for j, theme2 in enumerate(theme_list):
                if theme1 in themes and theme2 in themes and theme1 != theme2:
                    co_occurrence[i, j] += 1

    sns.heatmap(
        co_occurrence,
        xticklabels=theme_list,
        yticklabels=theme_list,
        cmap='YlOrRd',
        ax=ax4
    )
    ax4.set_title('Theme Co-occurrence Analysis')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('visualizations/theme_analysis_dashboard.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved theme analysis dashboard")


def create_sentiment_trends_dashboard(df):
    """Create a dashboard showing sentiment trends and patterns."""
    print("📊 Generating sentiment trends visualizations...")

    fig = plt.figure(figsize=(20, 15))
    gs = GridSpec(2, 2, figure=fig)

    # 1. Sentiment Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    sns.histplot(data=df, x='sentiment_score', bins=30, ax=ax1)
    ax1.set_title('Distribution of Sentiment Scores')
    ax1.set_xlabel('Sentiment Score')
    ax1.set_ylabel('Count')

    # 2. Sentiment Over Time
    ax2 = fig.add_subplot(gs[0, 1])
    df['month'] = df['date'].dt.to_period('M')
    monthly_sentiment = df.groupby('month')['sentiment_score'].mean()

    monthly_sentiment.plot(ax=ax2, marker='o')
    ax2.set_title('Average Sentiment Score Over Time')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Average Sentiment Score')

    # 3. Rating vs Sentiment
    ax3 = fig.add_subplot(gs[1, 0])
    sns.boxplot(data=df, x='rating', y='sentiment_score', ax=ax3)
    ax3.set_title('Sentiment Score Distribution by Rating')
    ax3.set_xlabel('User Rating')
    ax3.set_ylabel('Sentiment Score')

    # 4. Theme Impact on Sentiment
    ax4 = fig.add_subplot(gs[1, 1])
    theme_impact = []
    for themes, score in zip(df['themes'], df['sentiment_score']):
        for theme in themes:
            theme_impact.append({'theme': theme, 'sentiment': score})

    theme_impact_df = pd.DataFrame(theme_impact)
    sns.boxplot(data=theme_impact_df, x='sentiment', y='theme', ax=ax4)
    ax4.set_title('Impact of Themes on Sentiment')
    ax4.set_xlabel('Sentiment Score')

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('visualizations/sentiment_trends_dashboard.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved sentiment trends dashboard")


def create_user_experience_dashboard(df):
    """Create a dashboard focusing on user experience metrics."""
    print("📱 Generating user experience visualizations...")

    fig = plt.figure(figsize=(20, 15))
    gs = GridSpec(2, 2, figure=fig)

    # 1. Rating Distribution Over Time
    ax1 = fig.add_subplot(gs[0, 0])
    df['month'] = df['date'].dt.to_period('M')
    rating_evolution = df.groupby('month')['rating'].mean()

    rating_evolution.plot(ax=ax1, marker='o')
    ax1.set_title('Average Rating Over Time')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Average Rating')

    # 2. Theme Distribution by Rating
    ax2 = fig.add_subplot(gs[0, 1])
    theme_ratings = []
    for themes, rating in zip(df['themes'], df['rating']):
        for theme in themes:
            theme_ratings.append({'theme': theme, 'rating': rating})

    theme_ratings_df = pd.DataFrame(theme_ratings)
    sns.boxplot(data=theme_ratings_df, x='rating', y='theme', ax=ax2)
    ax2.set_title('Theme Distribution by Rating')
    ax2.set_xlabel('User Rating')

    # 3. Most Common Themes by Rating
    ax3 = fig.add_subplot(gs[1, 0])
    high_rating_themes = Counter([theme for themes, rating in zip(df['themes'], df['rating'])
                                  for theme in themes if rating >= 4])
    low_rating_themes = Counter([theme for themes, rating in zip(df['themes'], df['rating'])
                                 for theme in themes if rating <= 2])

    theme_comparison = pd.DataFrame({
        'High Ratings (4-5)': pd.Series(high_rating_themes),
        'Low Ratings (1-2)': pd.Series(low_rating_themes)
    }).fillna(0)

    theme_comparison.plot(kind='bar', ax=ax3)
    ax3.set_title('Theme Frequency by Rating Category')
    ax3.set_xlabel('Theme')
    ax3.set_ylabel('Count')
    plt.xticks(rotation=45, ha='right')

    # 4. Sentiment-Rating Correlation
    ax4 = fig.add_subplot(gs[1, 1])
    sns.scatterplot(data=df, x='sentiment_score',
                    y='rating', alpha=0.5, ax=ax4)
    ax4.set_title('Correlation between Sentiment Score and Rating')
    ax4.set_xlabel('Sentiment Score')
    ax4.set_ylabel('User Rating')

    # Add correlation coefficient
    corr = df['sentiment_score'].corr(df['rating'])
    ax4.text(0.05, 4.5, f'Correlation: {corr:.2f}', fontsize=12)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('visualizations/user_experience_dashboard.png',
                dpi=300, bbox_inches='tight')
    print("✓ Saved user experience dashboard")


def generate_insights_report(df):
    """Generate a comprehensive insights report."""
    print("\n📋 Generating insights report...")

    # Theme Analysis
    theme_counts = Counter([theme for themes in df['themes']
                           for theme in themes])
    top_themes = dict(sorted(theme_counts.items(),
                      key=lambda x: x[1], reverse=True)[:5])

    # Sentiment Analysis
    avg_sentiment = df['sentiment_score'].mean()
    sentiment_trend = df.groupby(df['date'].dt.to_period('M'))[
        'sentiment_score'].mean()
    sentiment_change = sentiment_trend.iloc[-1] - sentiment_trend.iloc[0]

    # Rating Analysis
    avg_rating = df['rating'].mean()
    rating_trend = df.groupby(df['date'].dt.to_period('M'))['rating'].mean()
    rating_change = rating_trend.iloc[-1] - rating_trend.iloc[0]

    # Print Report
    print("\n=== CBE Mobile Banking App Analysis Report ===")
    print("\n1. Key Metrics:")
    print(f"• Average Sentiment Score: {avg_sentiment:.2f}")
    print(f"• Average Rating: {avg_rating:.2f}")
    print(f"• Total Reviews Analyzed: {len(df):,}")

    print("\n2. Top Themes:")
    for theme, count in top_themes.items():
        print(f"• {theme}: {count:,} mentions")

    print("\n3. Trend Analysis:")
    print(
        f"• Sentiment Trend: {'Improving' if sentiment_change > 0 else 'Declining'} ({sentiment_change:.2f} change)")
    print(
        f"• Rating Trend: {'Improving' if rating_change > 0 else 'Declining'} ({rating_change:.2f} change)")

    print("\n4. Key Recommendations:")
    print("• Improve transaction reliability and error handling")
    print("• Enhance user interface with better feedback mechanisms")
    print("• Implement biometric authentication for better security")
    print("• Add comprehensive transaction history and search functionality")
    print("• Streamline the app activation process")


def main():
    """Main execution function."""
    # Create visualizations directory if it doesn't exist
    import os
    os.makedirs('visualizations', exist_ok=True)

    # Load and prepare data
    df = load_and_prepare_data()

    # Generate visualizations
    create_theme_analysis_dashboard(df)
    create_sentiment_trends_dashboard(df)
    create_user_experience_dashboard(df)

    # Generate insights report
    generate_insights_report(df)


if __name__ == "__main__":
    main()
