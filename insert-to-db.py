import pandas as pd
import oracledb
# Load your data
df = pd.read_csv("data/analyzed_reviews.csv")

try:
    # Load your data
    print("Loading data from CSV...")
    df = pd.read_csv("data/analyzed_reviews.csv")
    print(f"Successfully loaded {len(df)} records")
except FileNotFoundError:
    print("Error: Could not find the CSV file. Please check if the file exists in the data directory.")
    raise
except pd.errors.EmptyDataError:
    print("Error: The CSV file is empty.")
    raise
except Exception as e:
    print(f"An unexpected error occurred while loading the data: {str(e)}")
    raise

# Data validation
try:
    required_columns = ['bank', 'review_text', 'rating', 'date', 'sentiment_label', 'sentiment_score', 'identified_theme(s)']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for null values in required fields
    null_counts = df[required_columns].isnull().sum()
    if null_counts.any():
        print("Warning: Found null values in the following columns:")
        print(null_counts[null_counts > 0])
        
    # Validate data types
    df['rating'] = pd.to_numeric(df['rating'], errors='raise')
    df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='raise')
    # pd.to_datetime(df['date'], format='%Y-%m-%d', errors='raise')


    print("Data validation completed successfully")
except ValueError as e:
    print(f"Data validation error: {str(e)}")
    raise
except Exception as e:
    print(f"An unexpected error occurred during data validation: {str(e)}")
    raise


# Database connection setup
try:
    print("Connecting to database...")
    conn = oracledb.connect(
        user="bank_reviews",
        password="bank_reviews",
        dsn="localhost/XEPDB1"  # default DSN for Oracle XE 21c
    )
    cursor = conn.cursor()
    print("Database connection established successfully")

    # Verify database connection and table existence
    try:
        cursor.execute("SELECT 1 FROM banks WHERE ROWNUM = 1")
        cursor.execute("SELECT 1 FROM reviews WHERE ROWNUM = 1")
    except oracledb.DatabaseError:
        print("Creating required tables...")
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE banks (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR2(50) UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE reviews (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                review_text CLOB NOT NULL,
                rating NUMBER(1) NOT NULL,
                review_date DATE NOT NULL,
                bank_id NUMBER NOT NULL,
                sentiment_label VARCHAR2(20) NOT NULL,
                sentiment_score NUMBER NOT NULL,
                theme VARCHAR2(4000),
                CONSTRAINT fk_bank
                    FOREIGN KEY (bank_id)
                    REFERENCES banks(id)
            )
        """)
        conn.commit()
        print("Tables created successfully")

except oracledb.DatabaseError as e:
    error_obj, = e.args
    print(f"Database connection error: {error_obj.message}")
    raise
except Exception as e:
    print(f"An unexpected error occurred while connecting to database: {str(e)}")
    raise

# Validate and handle bank names
valid_banks = {'CBE', 'BOA', 'DASHEN'}
bank_names = df['bank'].unique()
invalid_banks = set(bank_names) - valid_banks

if invalid_banks:
    raise ValueError(f"Invalid bank names found: {', '.join(invalid_banks)}. Only CBE, BOA, and DASHEN are allowed.")

# Get or create bank IDs
bank_ids = {}
for name in bank_names:
    # Check if bank already exists
    cursor.execute("SELECT id FROM banks WHERE name = :1", [name])
    result = cursor.fetchone()
    
    if result:
        bank_ids[name] = result[0]
    else:
        # Create a variable to store the returned ID
        returning_var = cursor.var(int)
        cursor.execute(
            "INSERT INTO banks (name) VALUES (:1) RETURNING id INTO :2",
            [name, returning_var]
        )
        bank_ids[name] = returning_var.getvalue()[0]
        conn.commit()

# Insert into reviews table
try:
    print("Starting data insertion...")
    inserted_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO reviews (
                    review_text, rating, review_date, bank_id,
                    sentiment_label, sentiment_score, theme
                ) VALUES (
                    :review_text, :rating, TO_DATE(:review_date, 'YYYY-MM-DD'), :bank_id,
                    :sentiment_label, :sentiment_score, :theme
                )
            """, {
                'review_text': row['review_text'],
                'rating': int(row['rating']),
                'review_date': row['date'],
                'bank_id': bank_ids[row['bank']],
                'sentiment_label': row['sentiment_label'],
                'sentiment_score': float(row['sentiment_score']),
                'theme': row['identified_theme(s)']
            })
            inserted_count += 1

            # Commit every 100 records
            if inserted_count % 100 == 0:
                conn.commit()
                print(f"Inserted {inserted_count} records...")

        except Exception as e:
            error_count += 1
            errors.append(f"Error at row {index}: {str(e)}")
            continue

    # Final commit
    conn.commit()
    print(f"\nInsertion completed:")
    print(f"Successfully inserted: {inserted_count} records")
    if error_count > 0:
        print(f"Failed to insert: {error_count} records")
        print("First few errors:")
        for error in errors[:5]:
            print(error)

except Exception as e:
    print(f"An error occurred during data insertion: {str(e)}")
    conn.rollback()
    raise

finally:
    cursor.close()
    conn.close()
    print("Database connection closed.")