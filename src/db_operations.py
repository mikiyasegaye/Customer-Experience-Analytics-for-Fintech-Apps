"""
Module for database operations with PostgreSQL.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Get the absolute path to the project root directory
PROJECT_ROOT = str(Path(__file__).parent.parent)


def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.join(PROJECT_ROOT, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'db_operations_{timestamp}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


class DatabaseManager:
    def __init__(self):
        """Initialize database connection using environment variables."""
        load_dotenv()
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'bank_reviews')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.engine = None

    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(url)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logging.info("Successfully connected to PostgreSQL database")
            return True
        except SQLAlchemyError as e:
            logging.error(f"Error connecting to database: {str(e)}")
            return False

    def close(self):
        """Close database connection."""
        if self.engine:
            try:
                self.engine.dispose()
                logging.info("Database connection closed")
            except Exception as e:
                logging.error(f"Error closing database connection: {str(e)}")

    def init_migrations(self):
        """Initialize migrations tracking table."""
        try:
            with self.engine.connect() as conn:
                # Create migrations table if it doesn't exist
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(50) PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """))
                conn.commit()
                logging.info("Migrations tracking table initialized")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error initializing migrations table: {str(e)}")
            return False

    def apply_migration(self, version, description):
        """Apply a specific migration version."""
        try:
            # Check if migration was already applied
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT version FROM schema_migrations WHERE version = :version"),
                    {"version": version}
                )
                if result.fetchone():
                    logging.info(f"Migration {version} was already applied")
                    return True

                # Read migration file
                migration_file = os.path.join(
                    PROJECT_ROOT, 'database', 'migrations', f'V{version}__{description}.sql'
                )

                if not os.path.exists(migration_file):
                    logging.error(
                        f"Migration file not found: {migration_file}")
                    return False

                with open(migration_file, 'r') as f:
                    migration_sql = f.read()

                # Execute migration
                conn.execute(text(migration_sql))

                # Record migration
                conn.execute(
                    text("""
                        INSERT INTO schema_migrations (version, description)
                        VALUES (:version, :description)
                    """),
                    {"version": version, "description": description}
                )

                conn.commit()
                logging.info(
                    f"Successfully applied migration {version}: {description}")
                return True

        except Exception as e:
            logging.error(f"Error applying migration {version}: {str(e)}")
            return False

    def create_tables(self):
        """Create the required tables if they don't exist."""
        try:
            # Initialize migrations
            if not self.init_migrations():
                raise Exception("Failed to initialize migrations table")

            # Apply initial schema migration
            if not self.apply_migration("1", "initial_schema"):
                raise Exception("Failed to apply initial schema migration")

            logging.info("Tables created successfully")
            return True
        except Exception as e:
            logging.error(f"Error creating tables: {str(e)}")
            return False

    def insert_banks(self):
        """Insert bank information."""
        try:
            with self.engine.connect() as conn:
                # Bank data
                banks = [
                    ('Commercial Bank of Ethiopia',
                     'com.combanketh.mobilebanking'),
                    ('Bank of Abyssinia', 'com.boa.boaMobileBanking'),
                    ('Dashen Bank', 'com.dashen.dashensuperapp')
                ]

                # Insert banks
                for bank_name, app_id in banks:
                    conn.execute(
                        text("""
                        INSERT INTO banks (bank_name, app_id)
                        VALUES (:bank_name, :app_id)
                        ON CONFLICT (bank_name) DO NOTHING
                        """),
                        {"bank_name": bank_name, "app_id": app_id}
                    )

                conn.commit()
                logging.info("Bank information inserted successfully")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error inserting bank information: {str(e)}")
            return False

    def insert_reviews(self):
        """Insert review data from processed files."""
        try:
            # Load processed data
            reviews_file = os.path.join(
                PROJECT_ROOT, 'data/processed/sentiment_analysis_results.csv')
            themes_file = os.path.join(
                PROJECT_ROOT, 'data/processed/thematic_analysis_results.csv')

            reviews_df = pd.read_csv(reviews_file)
            themes_df = pd.read_csv(themes_file)

            # Merge sentiment and theme data
            merged_df = pd.merge(reviews_df, themes_df,
                                 on='review_id', suffixes=('', '_theme'))

            with self.engine.connect() as conn:
                # Get bank IDs
                result = conn.execute(
                    text("SELECT bank_name, bank_id FROM banks"))
                bank_mapping = dict(result.fetchall())

                # Insert reviews
                for _, row in merged_df.iterrows():
                    bank_id = bank_mapping.get(row['bank'])
                    if bank_id:
                        conn.execute(
                            text("""
                            INSERT INTO reviews (
                                bank_id, review_text, rating, review_date,
                                sentiment, sentiment_score, themes
                            )
                            VALUES (
                                :bank_id, :review_text, :rating, :review_date,
                                :sentiment, :sentiment_score, :themes
                            )
                            """),
                            {
                                "bank_id": bank_id,
                                "review_text": row['review_text'],
                                "rating": row['rating'],
                                "review_date": pd.to_datetime(row['date']).date(),
                                "sentiment": row['sentiment_label'],
                                "sentiment_score": row['sentiment_score'],
                                "themes": '; '.join(eval(row['themes']))
                            }
                        )

                conn.commit()
                logging.info(f"Successfully inserted {len(merged_df)} reviews")
                return True
        except Exception as e:
            logging.error(f"Error inserting reviews: {str(e)}")
            return False

    def create_dump(self, timestamp=None):
        """Create SQL dumps of the database schema and data."""
        try:
            # Create database directories if they don't exist
            db_dir = os.path.join(PROJECT_ROOT, 'database')
            dumps_dir = os.path.join(db_dir, 'dumps')
            os.makedirs(dumps_dir, exist_ok=True)

            # Generate timestamp for file names
            if timestamp is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Create schema-only dump
            schema_file = os.path.join(db_dir, 'schema.sql')
            escaped_schema_file = f'"{schema_file}"'
            schema_cmd = f'pg_dump -h {self.host} -p {self.port} -U {self.user} -d {self.database} --schema-only > {escaped_schema_file}'
            os.system(schema_cmd)
            logging.info(f"Schema dump created successfully at {schema_file}")

            # Create complete dump with timestamp (schema + data)
            dump_file = os.path.join(
                dumps_dir, f'bank_reviews_dump_{timestamp}.sql')
            escaped_dump_file = f'"{dump_file}"'
            dump_cmd = f'pg_dump -h {self.host} -p {self.port} -U {self.user} -d {self.database} > {escaped_dump_file}'
            os.system(dump_cmd)
            logging.info(
                f"Complete database dump created successfully at {dump_file}")

            # Create a latest symlink to the most recent dump
            latest_link = os.path.join(dumps_dir, 'latest_dump.sql')
            if os.path.exists(latest_link):
                os.remove(latest_link)
            os.symlink(dump_file, latest_link)
            logging.info(
                f"Updated latest dump symlink to point to {dump_file}")

            return True
        except Exception as e:
            logging.error(f"Error creating database dumps: {str(e)}")
            return False


def main():
    """Main function to set up database and insert data."""
    setup_logging()
    logging.info("Starting database operations...")

    db = DatabaseManager()

    try:
        # Connect to database
        if not db.connect():
            raise Exception("Failed to connect to database")

        # Create tables using migrations
        if not db.create_tables():
            raise Exception("Failed to create tables")

        # Insert bank information
        if not db.insert_banks():
            raise Exception("Failed to insert bank information")

        # Insert review data
        if not db.insert_reviews():
            raise Exception("Failed to insert review data")

        # Create database dump
        if not db.create_dump():
            raise Exception("Failed to create database dump")

        logging.info("Database operations completed successfully")

    except Exception as e:
        logging.error(f"Database operation failed: {str(e)}")
    finally:
        db.close()


if __name__ == '__main__':
    main()
