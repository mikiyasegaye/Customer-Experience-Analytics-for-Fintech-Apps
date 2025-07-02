-- V1: Initial schema
-- Created: 2025-07-02
-- Create banks table
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_id VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Create reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (
        rating BETWEEN 1 AND 5
    ),
    review_date DATE,
    sentiment VARCHAR(10),
    sentiment_score NUMERIC(5, 4),
    themes VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);